# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.conf import settings

from io import StringIO
import json
import datetime
import re
from celery.result import AsyncResult 

from app.forms import NazwaForm, PlikForm, FirmaForm, DeklaracjaForm
from app.models import Plik, Wyciag, Firma, Storage, Deklaracja
from sf.models import Sprawozdanie
from app import utils
from fk.models import MagDzial, SysPar

import lxml.etree as ET
from . import tasks
from . import xls
from . import wyslij

from app.deklaracja import DeklaracjaVAT

import logging
logger= logging.getLogger(__name__)
logger_email= logging.getLogger('email')


def GO_HOME(jpk= None, firma= None):
    return HttpResponseRedirect(reverse('home', args= [jpk._firma() if jpk else firma]))

    
@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=('jpk',)) or u.is_superuser, login_url='/polon/')
def home(request, firma= None):
    """
    Lista plików JPK.
    """
    if not firma:
        if SysPar._bra():
            return firmy(request)
        else:
            return GO_HOME(firma= settings.FIRMA)
    
    return render_to_response('app/tabela.html', 
                              { 
                                'rachunki': Wyciag.rachunki(),
                                'magazyny': MagDzial.magazyny(),
                                'FIRMA': settings.FIRMA,
                                'firma': firma,
                                'firmy': Firma.firmy(),
                                'rozwin': request.session.get('rozwin', 'null'),
                                'poprzednie': Sprawozdanie.poprzednie(firma),
                                'config': Sprawozdanie.nowe_config(firma)
                              }, 
                              context_instance= RequestContext(request))


@login_required
def firmy(request):
    """
    Wybór firmy.
    """
    if settings.FIRMA != 'bra':
        return GO_HOME(firma= settings.FIRMA)

    return render_to_response('app/firmy.html', 
                              { 
                                'FIRMA': settings.FIRMA,
                                'firma': settings.FIRMA,
                                'firmy': Firma.firmy(), 
                                'wybor_firmy': True,
                              }, 
                              context_instance= RequestContext(request))


@login_required    
def firma_edit(request, firma= None):
    """
    Zmiana danych firmy.
    """

    if firma:
        f= get_object_or_404(Firma, oznaczenie= firma)
        
    if request.method == 'POST':
        
        if firma:
            form= FirmaForm(request.POST, instance= f)
        else:
            form= FirmaForm(request.POST)
                
        if not form.is_valid():
            logger.warning(form)
        else:
            kod= form.cleaned_data['oznaczenie']
            if not firma:
                db_rok= SysPar.get_wartosc('ROK', kod)
                f= Firma(oznaczenie= kod, db_rok= db_rok)
                            
            f.oznaczenie= kod
            f.db_ostatnia= kod
                
            f.nip= form.cleaned_data['nip']
            f.nazwa= form.cleaned_data['nazwa']
            f.email= form.cleaned_data['email']
            f.telefon= form.cleaned_data['telefon']
            f.regon= form.cleaned_data['regon']
            f.wojewodztwo= form.cleaned_data['wojewodztwo']
            f.powiat= form.cleaned_data['powiat']
            f.gmina= form.cleaned_data['gmina']
            f.ulica= form.cleaned_data['ulica']
            f.nr_domu= form.cleaned_data['nr_domu']
            f.nr_lokalu= form.cleaned_data['nr_lokalu']
            f.miejscowosc= form.cleaned_data['miejscowosc']
            f.kod_pocztowy= form.cleaned_data['kod_pocztowy']
            f.poczta= form.cleaned_data['poczta']
            f.kod_urzedu= form.cleaned_data['kod_urzedu']
            f.api_url= form.cleaned_data['api_url']
            f.api_auth= form.cleaned_data['api_auth']
            f.vat7= form.cleaned_data['vat7']
            
            # Utworzenie pełnego adresu firmy z danych cząstkowych
            f.adres= '{} {}, {} {}'.format(f.miejscowosc, 
                                           f.kod_pocztowy,
                                           f.ulica,
                                           f.nr_domu)
            
            if f.nr_lokalu:
                f.adres += '/'+f.nr_lokalu
                
            f.save()
            
            # Powrót do listy firm
            return GO_HOME(firma= f.oznaczenie)           
    else:        
        if firma:            
            form= FirmaForm(instance= f)
        else:
            form= FirmaForm()
            
    return render_to_response('app/firma.html', 
                              { 
                                'form': form,
                                'FIRMA': settings.FIRMA,                                
                                'firma': firma,   
                              }, 
                              context_instance= RequestContext(request))
    
        
    
@login_required
def jpk_nazwa(request):
    """
    Zmiana nazwy/opisu pliku JPK.
    """
    
    if request.method == 'POST':
        
        jpk_id= request.POST.get('jpk_id')
        jpk= get_object_or_404(Plik, pk= jpk_id)
                
        form= NazwaForm(request.POST)
        if not form.is_valid():
            logger.warning(form)
        else:
            jpk.nazwa= form.cleaned_data['nazwa']
            if len(jpk.nazwa)>0:
                jpk.nazwa= jpk.nazwa[:1].upper()+ jpk.nazwa[1:]
            jpk.save()
            
            utils.alert(request, 'Opis pliku JPK-{} został zmieniony na "{}"'.format(jpk.id, jpk.nazwa), 'success')            
        
    return GO_HOME(jpk)



def jpk_nowy_plik(firma, kod, form, user, rachunek= None, magazyn= None):
    """
    Utworzenie nowego pliku JPK.
    """
    
    plik= Plik()
    plik.firma= firma
    plik.kod= kod.upper()
    plik.dataod= form.cleaned_data['dataod']
    plik.datado= form.cleaned_data['datado']
    plik.rachunek= rachunek
    plik.magazyn= magazyn
    plik.utworzony_user= user
    
    plik.utworzony= datetime.datetime.now()
        
    plik.wariant= {'JPK_VAT': '3', 'JPK_FA': '3', 'JPK_SF': '2'}.get(plik.kod, '1')
    plik.kod_systemowy= "{} ({})".format(plik.kod, plik.wariant)
    plik.wersja_schemy= "1-1"

    if kod == 'jpk_vat' and plik.dataod >= datetime.date(2020, 10, 1):
        plik.kod= 'JPK_VAT'
        plik.wariant= '4'
        plik.wariant_dek= 21
        plik.kod_systemowy= "JPK_V7{} (1)".format(firma.vat7 or 'M')
        plik.wersja_schemy= "1-2E"
        plik.korekta= form.cleaned_data['korekta']
        
    plik.cel_zlozenia= plik.ustal_cel_zlozenia()
    
    plik.xml= None
    plik.save()
    
    plik.firma.ustaw_ostatni_plik()
 
    config= {'wynik': form.cleaned_data['wynik'],
             'kapital': form.cleaned_data['kapital'],
             'przeplywy': form.cleaned_data['przeplywy'],
             'przeplywy_metoda': form.cleaned_data['przeplywy_metoda'],
             'kopia': form.cleaned_data['kopia']
    } if plik.kod == 'JPK_SF' else {}
            
    if config and form.cleaned_data['poprzednie']:
        config['poprzednie']= form.cleaned_data['poprzednie']
            
    if plik.kod in ('JPK_VAT', 'JPK_FA', 'JPK_KR', 'JPK_WB', 'JPK_MAG', 'JPK_SF'):
        tasks.run_task(plik, config)    
        
    return plik



@login_required        
def jpk_nowe(request, firma):
    """
    Tworzenie nowych plików JPK określonych w formularzu.
    """
    
    firma= get_object_or_404(Firma, oznaczenie= firma)    
    user= request.user.username if request.user.is_authenticated() else 'nieznany'
        
    if request.method == 'POST':
        form= PlikForm(request.POST, firma)
        if not form.is_valid():
            logger.warning(form)
        else:
            pliki= []
            for kod in ('jpk_kr', 'jpk_vat', 'jpk_fa', 'jpk_wb', 'jpk_mag', 'jpk_sf', 'jpk_v7m'):
                if form.cleaned_data[kod]:
                    rachunki= form.cleaned_data['rachunki'] if kod == 'jpk_wb' else [None]
                    magazyny= form.cleaned_data['magazyny'] if kod == 'jpk_mag' else [None]

                    if kod == 'jpk_wb':                    
                        for rachunek in rachunki:
                            pliki.append(jpk_nowy_plik(firma, kod, form, user, rachunek= rachunek.replace(' ', '')))
                    elif kod == 'jpk_mag':
                        for magazyn in magazyny:
                            pliki.append(jpk_nowy_plik(firma, kod, form, user, magazyn= magazyn))
                    else:
                        pliki.append(jpk_nowy_plik(firma, kod, form, user))

            utils.alert(request, 'Rozpoczęto tworzenie nowych plików JPK')
            
            logger_email.info('Rozpoczęto tworzenie nowych plików {}'.format(', '.join(jpk.nazwa_pliku() for jpk in pliki)))
    
    return GO_HOME(firma= firma.oznaczenie)


@login_required
def jpk_usun(request, jpk_id):
    """
    Usunięcie podanego pliku JPK.
    """
    
    jpk= get_object_or_404(Plik, pk= jpk_id)
    
    if (jpk.upo or jpk.stan == 'DOSTARCZONY'):
        utils.alert(request, 'Plik {} został dostarczony do MF, dlatego nie może być usunięty!'.format(jpk.nazwa_pliku()), 'danger')                
    elif jpk.stan == 'SPRAWDZANY':
        utils.alert(request, 'Plik {} jest w trakcie przetwaraznia w MF, na razie nie może być usunięty!'.format(jpk.nazwa_pliku()), 'danger')   
    else:
        jpk_nazwa= jpk.nazwa_pliku()
        jpk.delete()
        jpk.firma.ustaw_ostatni_plik()
        
        utils.alert(request, 'Usunięto plik {}.xml'.format(jpk_nazwa), 'warning')
            
    return GO_HOME(jpk= jpk)



@login_required
def jpk_arkusz(request, jpk_id, arkusz):
    """
    Wyświetlenie arkusza kontrolnego części pliku JPK.
    """

    # Pobranie pliku JPK w tym xml    
    jpk= get_object_or_404(Plik, pk= jpk_id)
    
    ctrl= jpk.get_ctrl(arkusz)
    
    if not ctrl.xls or settings.LOCAL_DEV:
        ctrl.xls= xls.jpk_arkusz(jpk, arkusz)
        if utils.par_firmy('save_ctrl_xls'):
            ctrl.save(update_fields= ['xls'])
    
    response= HttpResponse(content_type= 'application/vnd.ms-excel')
    response['Content-Disposition']= 'attachment; filename="{}.xlsx"'.format(jpk.nazwa_pliku(arkusz))
    response.write(ctrl.xls)
    
    return response



@login_required
def jpk_xlsx(request, jpk_id):
    """
    Wyświetlenie zeszytu z wszystkimi arkuszami kontrolnymi pliku JPK.
    """

    # Pobranie pliku JPK w tym xml    
    jpk= get_object_or_404(Plik, pk= jpk_id)
    
    if not jpk.xls or settings.LOCAL_DEV:
        jpk.xls= xls.jpk_workbook(jpk)
        if utils.par_firmy('save_jpk_xls'):  
            jpk.save(update_fields= ['xls'])
        
    response= HttpResponse(content_type= 'application/vnd.ms-excel')
    response['Content-Disposition']= 'attachment; filename="{}.xlsx"'.format(jpk.nazwa_pliku())

    response.write(jpk.xls)
    
    return response



@login_required
def jpk_upo(request, jpk_id, wydruk= False):
    """
    Wyświetlenie UPO pliku JPK.
    """

    jpk= get_object_or_404(Plik, pk= jpk_id)

    response= HttpResponse(content_type= 'application/xhtml+xml')
    response['Content-Disposition']= '{}; filename="{}-UPO.xml"'.format('inline' if wydruk else 'attachment', jpk.kod.lower())
    
    xml= jpk.upo
    if wydruk:
        if '<ds:Signature' in xml:
            # Dla wersji produkcyjnej z podpisem
            xml= xml.replace('<ds:Signature', '<?xml-stylesheet type="text/xsl" href="/static/css/upo.xsl"?><ds:Signature')
        else:
            # Dla wersji testowej bez podpisu
            xml= xml.replace('<Potwierdzenie', '<?xml-stylesheet type="text/xsl" href="/static/css/upo.xsl"?><Potwierdzenie')            

    response.write(xml)
    
    return response


@login_required
def jpk_download(request, jpk_id):
    """
    Pobranie pliku JPK w formacie XML.
    """

    jpk= get_object_or_404(Plik, pk= jpk_id)

    response= HttpResponse(content_type= 'application/xhtml+xml')
    response['Content-Disposition']= 'attachment; filename="{}.xml"'.format(jpk.nazwa_pliku())
 
    response.write(jpk.xml)
     
    return response



@login_required
def jpk_regeneruj(request, jpk_id):
    """
    Odświeżenie (ponowne utworzenie) zawartości danego pliku JPK.
    """
    
    # Ustawienie stanu na - tworzenie
    jpk= get_object_or_404(Plik, pk= jpk_id)    
    jpk.set_stan('W KOLEJCE')
    
    # Usunięcie poprzednich wysyłek i błędów
    jpk.storage_set.all().delete()
    jpk.blad_set.all().delete()
    jpk.deklaracja_set.all().delete()
    
    jpk.xml= None
    jpk.xls= None
    jpk.save(update_fields=['stan', 'odkad', 'xml', 'xls'])
    
    # Countdown jest ważny aby zdążyły się wykonać poniższe update'y
    result= tasks.run_task(jpk)
    
    jpk.task= result.id
    jpk.utworzony= datetime.datetime.now()+datetime.timedelta(days=60) # WAF Wywalić!!!!!!!!!!!!!!!!
    jpk.utworzony_user= request.user.username if request.user.is_authenticated() else 'nieznany'
    jpk.save(update_fields= ['task', 'utworzony', 'utworzony_user'])

    jpk.podsumowania.all().delete()
    
    logger_email.info('Rozpoczęto regenerowanie pliku {}'.format(jpk.nazwa_pliku()))
    
    return GO_HOME(jpk= jpk)



@login_required
def jpk_task(request, jpk_ids):
    """
    Sprawdzenie stanu/statusy podanych plików JPK.
    """
    
    jpk_ids= jpk_ids.split(',')
    
    html= {}
    for jpk in Plik.objects.filter(id__in= jpk_ids):
        if jpk.oczekiwanie():
            if jpk.task:
                
                result= AsyncResult(jpk.task)
                
                if result and result.status == 'SUCCESS':
                    jpk.set_stan('GOTOWY')
                elif result and result.status == 'FAILURE':
                    jpk.set_stan('PROBLEMY')
                else:
                    jpk.set_stan(result.status)
                
            # Jeżeli stan się nie zmienił to nie ma potrzeby zapisywania
            jpk.save(update_fields=['stan', 'odkad', 'task'])
            
        html[jpk.id]= {'stan': jpk.stan, 'czas': str(datetime.datetime.now()-jpk.odkad)[:7]}
        
    return HttpResponse(json.dumps(html), content_type='application/json')


@login_required
def firma_dane(request, firma):
    """
    Sprawdzenie stanu/statusy podanych plików JPK.
    """

    nazwa= SysPar.get_wartosc('NAZ', firma)
    nip= SysPar.get_wartosc('SPR-NIP', firma)
    
    if nip:
        nip= re.sub('-', '', nip)
            
    html= {'nazwa': nazwa,
           'nip': nip,
        }
        
    return HttpResponse(json.dumps(html), content_type='application/json')


@login_required
def jpk_refresh(request, jpk_id):
    """
    Pobranie aktualnych danych pliku JPK.
    """
    
    jpk= get_object_or_404(Plik, pk= jpk_id)
    jpk_data= jpk.to_json()
            
    return HttpResponse(jpk_data, content_type='application/json')



@login_required
def jpk_rozwin(request, jpk_id):
    """
    Pobranie rozwinięcia wiersza pliku JPK w tabeli plików.
    """
    
    jpk= get_object_or_404(Plik, pk= jpk_id)
    
    utils.alert(request, 'Pobranie szczegółów pliku')
    
    request.session['rozwin']= jpk.id 
    
    return render_to_response('app/plik.html',
                        { 
                                'plik': jpk,
                        }, 
                        context_instance= RequestContext(request))


@login_required
def jpk_zwin(request, jpk_id):
    """
    Usunięcie informacji o rozwinięciu wiersza.
    """
    
    if 'rozwin' in request.session:
        del request.session['rozwin']

    return HttpResponse('OK', content_type='application/json')
    


@login_required
def jpk_validate(request, jpk_id):
    """
    Sprawdzenie poprawności pliku JPK.
    """

    # Pobranie pliku JPK w tym xml    
    jpk= get_object_or_404(Plik, pk= jpk_id)
    
    # Parsowanie w celu pobrania danych
    xml= ET.parse(StringIO(jpk.xml.replace(' encoding="UTF-8"', '')))
    with open('app/static/xsd/{}{}{}.xsd'.format(
        jpk.kod.upper(), 
        jpk.wariant if jpk.wariant != '1' else '',
        jpk.v7_okres()
    ), 'r') as f:
        xmlschema_doc= ET.parse(f)
        xmlschema= ET.XMLSchema(xmlschema_doc)
    
    rc= xmlschema.validate(xml)
    
    bledy= {}
    
    for error in iter(xmlschema.error_log):
        line= error.line
        lerr= bledy.get(line, [])
        if not lerr:
            bledy[line]= lerr
        lerr.append(re.sub('{.*?}', '', error.message))
        
    bledy= [(line, '<br/>'.join(bledy[line])) for line in sorted(bledy.keys())]

    return render_to_response('app/validate.html', 
                              { 
                                'plik': jpk,
                                'status': rc,
                                'bledy': bledy,
                              }, 
                              context_instance= RequestContext(request))



@login_required
def jpk_bledy(request, jpk_id):
    """
    Wyświetlenie informacji o błędach podczas tworzenia pliku.
    """

    # Pobranie pliku JPK w tym xml    
    jpk= get_object_or_404(Plik, pk= jpk_id)
    
    return render_to_response('app/bledy.html',
                              { 
                                'plik': jpk,
                              }, 
                              context_instance= RequestContext(request))

    

@login_required
def jpk_initupload(request, jpk_id= None):
    """
    Przygotowanie JPK do wysyłki przez utworzenie i wysłanie do użytkownika
    pliku kontrolnego XML, który powinien być podpisany.
    """

    user= request.user.username if request.user.is_authenticated() else 'nieznany'    
    
    if request.method == 'POST':
        jpk_id= request.POST.get('jpk_id')
        bramka= request.POST.get('bramka')
    else:
        bramka= 'Produkcyjna'
        
    jpk= get_object_or_404(Plik, pk= jpk_id)
    
    try:
        storage= Storage.objects.get(jpk=jpk)
    except Storage.DoesNotExist:
        # Utworzenie pliku initupload.XML
        try:
            storage= wyslij.InituploadMF(jpk).plik_kontrolny(user, bramka)
        except utils.OperacjaNiedozwolona as e:
            utils.alert(request, 'Tworzenie pliku kontrolnego dla {} jest niedozwolone: {}'.format(jpk.nazwa_pliku(), e.args[0]), 'warning')        
            return GO_HOME(jpk= jpk)
        except Exception as e:
            utils.alert(request, 'Błąd podczas tworzenia pliku kontrolnego dla {}: {}'.format(jpk.nazwa_pliku(), e.args[0]), 'danger')        
            return GO_HOME(jpk= jpk)

    # Wysłanie pliku kontrolnego initupload.XML do użytkownika
    
    response= HttpResponse(content_type= 'application/xhtml+xml')
    response['Content-Disposition']= 'attachment; filename="{}.xml"'.format(jpk.nazwa_pliku('initupload'))
    response.write(storage.sign_xml)
    
    jpk.set_stan('PODPISYWANY', save= True)
    
    logger_email.info('Przekazanie pliku kontrolnego pliku {} do podpisania'.format(jpk.nazwa_pliku()))        
     
    return response


@login_required
def sf_upload(request):
    """
    Transakcja dla każdego pliku osobno
    """
    if request.method == 'POST':
        uploaded_file= request.FILES.get('plik')
        
        jpk_id= request.POST.get('jpk_id')
        jpk= get_object_or_404(Plik, pk= jpk_id)
                
        if uploaded_file:
            xml= uploaded_file.read()
            xml= xml.decode('utf-8')
            if not re.match('^<\?xml', xml):
                xml= '<?xml version="1.0" encoding="UTF-8"?>\n'+xml
            jpk.xml= xml.encode('utf-8')
            jpk.save()            

    return GO_HOME(jpk)


@login_required
def jpk_upload(request):
    """
    Transakcja dla każdego pliku osobno
    """
    
    user= request.user.username if request.user.is_authenticated() else 'nieznany'
    
    if request.method == 'POST':
        
        jpk_id= request.POST.get('jpk_id')
        jpk= get_object_or_404(Plik, pk= jpk_id)
        storage= jpk.storage_set.all()[0]
        
        signed_file= request.FILES.get('plik')
        if signed_file:
            
            xades_xml= signed_file.read()
            
            storage.bramka= 'T' if request.POST.get('bramka') == 'Bramka testowa' else 'P'
            signed_name= signed_file._name

            # Na interfejs produkcyjny można wysłać tylko produkcyjne pliki JPK
            
            if storage.interfejs_produkcyjny():
                nazwa_start= '{}-initupload'.format(jpk.nazwa_pliku())
                if not signed_name.startswith(nazwa_start):
                    utils.alert(request, 'Niepoprawny początek nazwy pliku kontrolnego: {}, zamiast oczekiwanego: {}'.format(signed_name, nazwa_start), 'warning')
                    return GO_HOME(jpk= jpk)
               
            # Wgrany, podpisany plik kontrolny musi mieć w nazwie xades
                           
            if not 'xades' in signed_name.lower():
                utils.alert(request, 'Brak xades w nazwie pliku: {} '.format(signed_name), 'warning')
                return GO_HOME(jpk= jpk)

            # Podmiana pliku AES na plik odpowiadający wgranemu plikowi testwemu
                            
            if signed_name.startswith('jpk'):
                try:
                    nazwa= 'send/{}.zip.aes'.format(signed_name.split('-initupload')[0])
                    storage.jpk_aes= open(nazwa, 'rb').read()
                except:
                    storage.jpk_aes= open('send/jpk0.zip.aes', 'rb').read()
            
            storage.xades_time= datetime.datetime.now()
            storage.xades_user= user
            storage.xades_xml= xades_xml
            storage.reset_upload()
            storage.save()
            
            jpk.set_stan('PODPISANY', save= True)
            
            tasks.wyslij_jpk(jpk, user)
            
            logger_email.info('Wysyłanie pliku {}'.format(jpk.nazwa_pliku()))
            
    return render_to_response('app/upload.html',
                            { 
                                'jpk': jpk,
                                'storage': storage,
                                'FIRMA': settings.FIRMA,
                                'firma': settings.FIRMA,
                                'delay': 1,
                            }, 
                            context_instance= RequestContext(request))


@login_required
def jpk_wyslij(request, jpk_id):
    """
    Transakcja dla każdego pliku osobno
    """
    
    user= request.user.username if request.user.is_authenticated() else 'nieznany'

    jpk_id= int(jpk_id)    
    jpk= get_object_or_404(Plik, pk= jpk_id)
    storage= jpk.storage_set.all()[0]
    
    jpk.set_stan('PODPISANY', save= True)
        
    tasks.wyslij_jpk(jpk, user)
        
    logger_email.info('Wysyłanie pliku {}'.format(jpk.nazwa_pliku()))
            
    return render_to_response('app/upload.html',
                            { 
                                'jpk': jpk,
                                'storage': storage,
                                'FIRMA': settings.FIRMA,
                                'firma': settings.FIRMA,
                                'delay': 1,
                            }, 
                            context_instance= RequestContext(request))
    
    

@login_required
def jpk_status(request, jpk_id, delay):
    """
    Sprawdzenie statusu wysyłki pliku JPK.
    """
    
    user= request.user.username if request.user.is_authenticated() else 'nieznany'
        
    jpk= get_object_or_404(Plik, pk= jpk_id)
    storage= jpk.storage_set.all()[0]

    if not jpk.upo and storage.reference:
        wyslij.WysylkaMF(jpk).status(user)
            
    return render_to_response('app/upload.html',
                            { 
                                'jpk': jpk,
                                'storage': storage,
                                'FIRMA': settings.FIRMA,
                                'firma': jpk._firma(),
                                'delay': int(delay)*2,
                            }, 
                            context_instance= RequestContext(request))


def jpk_statusy(request):
    """
    Do contaba dodać wywołanie sprawdzania np. co 15 minut.
    """
    sprawdzane= []
    for jpk in Plik.objects.filter(stan='SPRAWDZANY', 
                                   utworzony__gte=datetime.datetime.now()- datetime.timedelta(days= 7)):
        
        storage= jpk.storage_set.all()[0]
        if storage and storage.reference:
            wyslij.WysylkaMF(jpk).status('krezusfk')
            sprawdzane.append('Sprawdzanie JPK {}'.format(jpk.id))
        
    return HttpResponse('<br/>'.join(sprawdzane))




@login_required
def jpk_vatpdf(request, jpk_id):
    """
    Wygenerowanie pdf deklaracji VAT.
    """

    # Pobranie pliku JPK w tym xml    
    jpk= get_object_or_404(Plik, pk= jpk_id)
    
    dek= DeklaracjaVAT(jpk)
    
    dek.wizualizacja_pdf()
    
    return HttpResponse('OK')


class Object(object):
    pass


def dekl_do_rozliczenia(jpk):

    dek= Object()
    
    dek.p37= Deklaracja.ustal(jpk, 37)
    dek.p38= Deklaracja.ustal(jpk, 38)
    dek.p39= Deklaracja.ustal(jpk, 39)
    
    dek.p48= Deklaracja.ustal(jpk, 48)

    dek.p49= Deklaracja.ustal(jpk, 49)
    dek.p50= Deklaracja.ustal(jpk, 50)
    dek.p51= Deklaracja.ustal(jpk, 51)
    dek.p52= Deklaracja.ustal(jpk, 52)
    dek.p53= Deklaracja.ustal(jpk, 53)
    dek.p54= Deklaracja.ustal(jpk, 54)

    dek.p55= Deklaracja.ustal(jpk, 55)
    dek.p56= Deklaracja.ustal(jpk, 56)
    dek.p57= Deklaracja.ustal(jpk, 57)
    dek.p58= Deklaracja.ustal(jpk, 58)

    dek.p59= Deklaracja.ustal(jpk, 59)    
    dek.p60= Deklaracja.ustal(jpk, 60)
    dek.p61= Deklaracja.ustal(jpk, 61)
    
    dek.p62= Deklaracja.ustal(jpk, 62)

    dek.p63= Deklaracja.ustal(jpk, 63)
    dek.p64= Deklaracja.ustal(jpk, 64)
    dek.p65= Deklaracja.ustal(jpk, 65)
    dek.p66= Deklaracja.ustal(jpk, 66)

    dek.p67= Deklaracja.ustal(jpk, 67)    
    
    dek.p68= Deklaracja.ustal(jpk, 68)
    dek.p69= Deklaracja.ustal(jpk, 69)
    dek.p70= Deklaracja.ustal(jpk, 70)
                                            
    if dek.p38.kwota > dek.p48.kwota:
        dek.p51.kwota= dek.p38.kwota - dek.p48.kwota - dek.p49.kwota - dek.p50.kwota
    else:
        dek.p51.kwota= 0

    if dek.p48.kwota > dek.p38.kwota:
        dek.p53.kwota= dek.p48.kwota - dek.p38.kwota + dek.p52.kwota
    else:
        dek.p53.kwota= 0

    dek.p62.kwota= dek.p53.kwota - dek.p54.kwota - dek.p60.kwota

    pozycje= {}
    wartosci= {}
    for a, v in dek.__dict__.items():
        pozycje['p_{}'.format(a[1:])]= v

        if v.rodzaj in ('1', '2'):
            wartosci['p_{}'.format(a[1:])]= v.kwota
        elif v.rodzaj == 'W':
            wartosci['p_{}'.format(a[1:])]= v.wybor
        else:
            wartosci['p_{}'.format(a[1:])]= v.tekst            

    return pozycje, wartosci



@login_required    
def deklaracja_form(request, jpk_id):
    """
    Edycja danych nieewidencyjnych do deklaracji VAT.
    """
    
    # Pobranie pliku JPK w tym xml    
    jpk= get_object_or_404(Plik, pk= jpk_id)

    pozycje, wartosci= dekl_do_rozliczenia(jpk)
    
    if request.method == 'POST':
        print('POST', request.POST)

        form= DeklaracjaForm(request.POST, pozycje, instance= jpk)
                
        if not form.is_valid():
            print('Błędy formularza deklracji')
            logger.warning(form)
        else:
            print('FORM VALID', form.cleaned_data)

            Deklaracja.zapisz(jpk, 39, form.cleaned_data['p_39'])            
            Deklaracja.zapisz(jpk, 49, form.cleaned_data['p_49'])
            Deklaracja.zapisz(jpk, 50, form.cleaned_data['p_50'])
            Deklaracja.zapisz(jpk, 52, form.cleaned_data['p_52'])
            Deklaracja.zapisz(jpk, 54, form.cleaned_data['p_54'])
            
            Deklaracja.zapisz(jpk, 55, form.cleaned_data['p_55'])
            Deklaracja.zapisz(jpk, 56, form.cleaned_data['p_56'])
            Deklaracja.zapisz(jpk, 57, form.cleaned_data['p_57'])
            Deklaracja.zapisz(jpk, 58, form.cleaned_data['p_58'])
            
            Deklaracja.zapisz(jpk, 59, form.cleaned_data['p_59'])
            Deklaracja.zapisz(jpk, 60, form.cleaned_data['p_60'])
            Deklaracja.zapisz(jpk, 61, form.cleaned_data['p_61'])
                        
            Deklaracja.zapisz(jpk, 63, form.cleaned_data['p_63'])
            Deklaracja.zapisz(jpk, 64, form.cleaned_data['p_64'])
            Deklaracja.zapisz(jpk, 65, form.cleaned_data['p_65'])
            Deklaracja.zapisz(jpk, 66, form.cleaned_data['p_66'])
            Deklaracja.zapisz(jpk, 67, form.cleaned_data['p_67'])
                        
            Deklaracja.zapisz(jpk, 68, form.cleaned_data['p_68'])
            Deklaracja.zapisz(jpk, 69, form.cleaned_data['p_69'])

            Deklaracja.zapisz(jpk, 70, form.cleaned_data['p_70'])
            
            # Aktualizacja deklaracji w XML                                                
            jpk.deklaracja_xml()
            
        pozycje, wartosci= dekl_do_rozliczenia(jpk)
    else:
        form= DeklaracjaForm(wartosci, pozycje, instance= jpk)
            
    return render_to_response('app/deklaracja_form.html', 
                              { 
                                'FIRMA': settings.FIRMA,   
                                'firma': jpk.firma.oznaczenie,                               
                                'jpk': jpk,
                                'form': form,
                                'dek': pozycje
                              }, 
                              context_instance= RequestContext(request))



@login_required    
def deklaracja_edit(request, jpk_id):
    """
    Edycja danych nieewidencyjnych do deklaracji VAT.
    """
    
    # Pobranie pliku JPK w tym xml    
    jpk= get_object_or_404(Plik, pk= jpk_id)
    
    return render_to_response('app/deklaracja.html', 
                              { 
                                'FIRMA': settings.FIRMA,   
                                'firma': jpk.firma.oznaczenie,                               
                                'jpk': jpk,
                              }, 
                              context_instance= RequestContext(request))
    


@login_required    
def deklaracja_view_pdf(request, jpk_id):
    """
    Wizualizacja deklaracji w formacie PDF (nieaktualne).
    """

    # Pobranie pliku JPK w tym xml    
    jpk= get_object_or_404(Plik, pk= jpk_id)
    
    dek= DeklaracjaVAT(jpk)
    pdf= dek.wizualizacja_pdf()
    
    response= HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition']= 'inline; filename="vat-7.pdf"'   
        
    return response 



def jpk_vat_wizualizacja(request, jpk_id, czesc= ''):
    """
    Wizualizacja pliku JPK_VAT lub jego cześci (sprzedaż, zakupy, deklaracja).
    """
    
    jpk= get_object_or_404(Plik, pk= jpk_id)
    czesc= czesc+'/' if czesc else ''

    response= HttpResponse(content_type= 'application/xhtml+xml')
    response['Content-Disposition']= '{}; filename="{}.xml"'.format('inline', jpk.kod.lower())
    
    xml= re.sub('<pf:JPK', '<?xml-stylesheet type="text/xsl" href="/xsl/styl-2020-05.xsl/{}/{}"?><pf:JPK'.format(jpk.id, czesc), jpk.xml)

    response.write(xml)
    
    return response


def jpk_vat_xsl(request, jpk_id, czesc= None):
    """
    Wysłanie pliku XSL dla JPK_VAT(4).
    Z ewentualną informacją, która część ma być pokazana.
    """
    CZESCI= {
        'deklaracja': 'Deklaracja',
    }
    
    jpk= get_object_or_404(Plik, pk= jpk_id)
    root= CZESCI.get(czesc, '')
    
    return render_to_response('app/xsl/styl-2020-05.xsl', { 
            'root': root,
            'jpk': jpk
        },
        content_type='application/xhtml+xml',
        context_instance= RequestContext(request)
    )
