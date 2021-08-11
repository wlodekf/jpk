# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.conf import settings

from app.models import Plik
from sf.models import Sprawozdanie, Raport, Pozycja 
from . import GO_HOME, RZYM

import logging
logger= logging.getLogger(__name__)
logger_email= logging.getLogger('sf')

    
@login_required
def jpk_sf(request, jpk_id, raport):
    """
    Wyświetlenie formularza do wprowadzania danych danego raportu.
    """
    # Pobranie pliku JPK w tym xml    
    jpk= get_object_or_404(Plik, pk= jpk_id)

    if jpk.xml:
        return HttpResponseRedirect(reverse('jpk-sf-xml', args= [jpk_id, raport]))
    
    spraw= Sprawozdanie.objects.get(jpk= jpk)
    nazwa, wersja, okres= '', '', jpk.datado.year
    tabela= raport
    
    if raport in ('aktywa', 'pasywa', 'rzis', 'kapital', 'przeplywy'):
        spraw= Raport.objects.get(sprawozdanie= spraw, tabela= raport)
        nazwa= spraw.nazwa
        wersja= None
        nazwy= nazwa.split('(')
        if len(nazwy)>1 and raport!='kapital': 
            nazwa= nazwy[0]
            wersja= nazwy[1].replace(')', '').strip()
        raport= 'raport'

    return render_to_response('app/sf/{}.html'.format(raport), 
                              { 
                                    'firma': jpk._firma(),
                                    'FIRMA': settings.FIRMA,
                                    'nazwa': nazwa,
                                    'wersja': wersja,
                                    'okres': okres,
                                    'tabela': tabela
                              }, 
                              context_instance= RequestContext(request))
    
    
def init_pozycji(request, raport_id):
    """
    Ustalenie poziomu i klu1 (do sortowania).
    Poziom raczej nie jest potrzebny bo wynika z klu1/klu3 (suma długości).
    """
    
    raport_id= int(raport_id)
    
    for poz in Pozycja.objects.filter(raport_id=raport_id).order_by('el'):
        
        wyl= poz.el.split("_")
        poz.poziom= len(wyl)
        poz.klu1= ''
        for w in wyl:
            if w in RZYM:
                k= str(RZYM[w])
            else:
                k= w[0]
            poz.klu1 += k
            
        # Korekta
        if poz.klu1 == 'PB331':
            poz.klu1= 'PB33I'
            
        poz.wyliczenie= wyl[-1]
        
        print("el: '{}', klucz: '{}', wyliczenie: '{}', nazwa: '{}'".format(poz.el, poz.klu1, poz.wyliczenie, poz.nazwa))
        poz.save()

    return HttpResponse('Zrobione')


def sf_pozycje(request):

    WYROZNIENIA= [
        ['UB', 'UBS', 'B'], # Aktywa
        ['UB', 'UBS', 'B'], # Pasywa
        ['UBS'], # RZiSKalk
        ['UBS'], # RZiSPor
        ['UBS', 'B'], # ZestZmianWKapitale
        ['UBS', 'B'], # PrzeplywyBezp
        ['UBS', 'U']  # PrzeplywyPosr
    ]
    
    rap_id= 2

    wyr= WYROZNIENIA[rap_id-1]
    
    for poz in Pozycja.objects.filter(raport_id__in=(rap_id,)):
        poz_wyr= 'wyr{}'.format(wyr[len(poz.klu1)-1]) if len(poz.klu1) <= len(wyr) else ''  
        print(
            '<xsd:enumeration value="{}"><xsd:annotation xml:klu="{}" xml:aaa="{}"><xsd:documentation>{}</xsd:documentation></xsd:annotation></xsd:enumeration>'
            .format(poz.el, (len(poz.klu1)-1)*10, poz_wyr, poz.nazwa)
        )

    return HttpResponse('OK')



def jpk_sf_generuj(request, jpk_id):
    """
    Utworzenie pliku XML dla sprawozdania finansowego po wybraniu w menu "Generuj plik XML"
    na podstawie wcześniej ustalonych i zapamiętanych danych wszystkich elementów sprawozdania.
    """
    jpk= get_object_or_404(Plik, pk= jpk_id)
    sprawozdanie= get_object_or_404(Sprawozdanie, jpk_id=int(jpk_id))
    
    context= {'jpk': jpk, 's': sprawozdanie}
     
    xml_wariant= jpk.kod.lower() + (jpk.wariant if jpk.wariant != '1' else '')
    jpk.xml= render_to_string('app/xml/{}.xml'.format(xml_wariant), context)
    
    jpk.save()
    
    return GO_HOME(jpk)


def jpk_sf_edit(request, jpk_id):
    
    jpk= get_object_or_404(Plik, pk= jpk_id)
    
    jpk.xml= None
    jpk.save()
    
    return GO_HOME(jpk)


@login_required
def jpk_sf_view(request, jpk_id, czesc= None, wydruk= True):
    """
    Wyświetlenie wizualizacji sprawozdania finansowego.
    """

    jpk= get_object_or_404(Plik, pk= jpk_id)
    
    czesc= czesc+'/' if czesc else ''

    response= HttpResponse(content_type= 'application/xhtml+xml')
    response['Content-Disposition']= '{}; filename="{}.xml"'.format('inline' if wydruk else 'attachment', jpk.kod.lower())
    
    xml= jpk.xml
    if wydruk:
        wariant= jpk.wariant if jpk.wariant != '1' else ''
        xml= re.sub('<([^/<]{0,20}\:)JednostkaInna', '<?xml-stylesheet type="text/xsl" href="/sf{}.xsl/{}"?><\\1JednostkaInna'.format(wariant, czesc), xml)            

    response.write(xml)
    
    return response


def sf_xsl(request, czesc= None, wariant= ''):
    CZESCI= {'wprowadz': 'WprowadzenieDoSprawozdaniaFinansowego',
             'aktywa': 'Bilans',
             'pasywa': 'Bilans',
             'rzis': 'RZiS',
             'kapital': 'ZestZmianWKapitale',
             'przeplywy': 'RachPrzeplywow',
             'podatek': 'DodatkoweInformacjeIObjasnieniaJedn{}stkaInna'.format('o' if wariant != '1' else ''),
             'dodatkowe': 'DodatkoweInformacjeIObjasnieniaJedn{}stkaInna'.format('o' if wariant != '1' else '')
            }
    
    root= CZESCI.get(czesc, '')
    
    return render_to_response('app/sf/sf{}.xsl'.format(wariant), 
                          { 
                                'root': root
                          },
                          content_type='application/xhtml+xml',
                          context_instance= RequestContext(request))

    
def test(request):
    return render_to_response('app/sf/embed.xml', 
                              {}, 
                              content_type='application/xhtml+xml',
                              context_instance= RequestContext(request))
