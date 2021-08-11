# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
import logging
import json
import re

from app.models import Firma
from fk.models import Ana

from .forms import SprzedazPlikiForm, SprzedazRejestrForm
from .models import Faktura, ImportSprzedazy
from .sprzedaz import SprzedazImporter, SprzedazRejestrVAT
from . import xls

logger= logging.getLogger(__name__)


@login_required
def bra_sprzedaz_pliki(request, firma= None): 
    """
    Import faktur sprzedaży do JPK i ewentualnie do rejestru sprzedaży.
    """
    
    firma= get_object_or_404(Firma, oznaczenie= firma)
            
    if request.method == 'POST':
        
        form= SprzedazPlikiForm(request.POST, request.FILES)
        if form.is_valid():
            
            sprzedaz= SprzedazImporter(firma= firma)
            sprzedaz.sprzedaz_importuj(form, request)
            
            return render_to_response('bra/sprzedaz/akceptacja.html', 
                                      { 
                                        'FIRMA': settings.FIRMA,
                                        'firma': firma.oznaczenie,
                                        'spr': sprzedaz,
                                        'imp': sprzedaz.imp,
                                        'ws_host': settings.WS_HOST
                                      }, 
                                      context_instance= RequestContext(request))  
        else:
            logger.warning(form)
                        
    else:
        form= SprzedazPlikiForm(initial= {})
            
    return render_to_response('bra/sprzedaz/pliki.html', 
                              { 
                                'FIRMA': settings.FIRMA,
                                'firma': firma.oznaczenie,
                                'form': form,
                                'ws_host': settings.WS_HOST                                
                              }, 
                              context_instance= RequestContext(request))    


@login_required
def bra_sprzedaz_akceptuj(request, imp_id= None): 
    """
    Import faktur sprzedaży do JPK i ewentualnie do rejestru sprzedaży.
    """
    
    imp= get_object_or_404(ImportSprzedazy, id= int(imp_id))
    sprzedaz= SprzedazImporter(imp= imp)
            
    if request.method == 'POST':
        
        if 'rezygnuj' in request.POST:
            imp.delete()
            return HttpResponseRedirect(reverse('bra-sprzedaz-importuj', args= [imp.firma.oznaczenie]))            
            
        sprzedaz.sprzedaz_akceptuj()
        
        return render_to_response('bra/sprzedaz/do_rejestru.html', 
                                  { 
                                    'FIRMA': settings.FIRMA,
                                    'firma': imp.firma.oznaczenie,
                                    'form': SprzedazRejestrForm(imp.firma.oznaczenie, instance= imp, initial= {'rejestr': 'PU'}),
                                    'spr': sprzedaz, 
                                    'imp': sprzedaz.imp,
                                    'ws_host': settings.WS_HOST                                    
                                  }, 
                                  context_instance= RequestContext(request))  
            
    return render_to_response('bra/sprzedaz/akceptacja.html', 
                              { 
                                'FIRMA': settings.FIRMA,
                                'firma': imp.firma.oznaczenie,
                                'form': SprzedazRejestrForm(imp.firma.oznaczenie, instance= imp),                                
                                'spr': sprzedaz, 
                                'imp': sprzedaz.imp,
                                'ws_host': settings.WS_HOST                                
                              }, 
                              context_instance= RequestContext(request))  
    
@login_required
def bra_sprzedaz_do_rejestru(request, imp_id= None): 
    """
    Import faktur sprzedaży do JPK i ewentualnie do rejestru sprzedaży.
    """
    
    imp= get_object_or_404(ImportSprzedazy, id= int(imp_id))
    rejestr= SprzedazRejestrVAT(imp= imp)
            
    if request.method == 'POST':
        
        form= SprzedazRejestrForm(imp.firma.oznaczenie, request.POST)
        if form.is_valid():
            
            rejestr.do_rejestru(form)
            
            return render_to_response('bra/sprzedaz/koniec.html', 
                                      { 
                                        'FIRMA': settings.FIRMA,
                                        'firma': imp.firma.oznaczenie, 
                                        'form': form,                                        
                                        'spr': rejestr,
                                        'imp': imp
                                      }, 
                                      context_instance= RequestContext(request))  
    else:
        form= SprzedazRejestrForm(imp.firma.oznaczenie, instance= imp)
                    
    return render_to_response('bra/sprzedaz/do_rejestru.html', 
                              { 
                                'FIRMA': settings.FIRMA,
                                'firma': imp.firma.oznaczenie,
                                'form': form,
                                'spr': rejestr, 
                                'imp': imp,
                                'ws_host': settings.WS_HOST                                
                              }, 
                              context_instance= RequestContext(request))  
    

@login_required
def bra_sprzedaz_koniec(request, imp_id= None): 
    """
    Import faktur sprzedaży do JPK i ewentualnie do rejestru sprzedaży.
    """
    
    imp= get_object_or_404(ImportSprzedazy, id= int(imp_id))
    rejestr= SprzedazRejestrVAT(imp= imp)
            
    if request.method == 'POST':
        return HttpResponseRedirect(reverse('bra-sprzedaz-importy', args= [imp.firma.oznaczenie]))
    else:
        form= SprzedazRejestrForm(imp.firma.oznaczenie, instance= imp)
                    
    return render_to_response('bra/sprzedaz/koniec.html', 
                                  { 
                                    'FIRMA': settings.FIRMA,
                                    'firma': imp.firma.oznaczenie, 
                                    'form': form,                                        
                                    'spr': rejestr,
                                    'imp': imp
                                  }, 
                                  context_instance= RequestContext(request))  
    
@login_required
def bra_ajax_rozwin(request, imp_id):
    """
    Pobranie rozwinięcia informacji o imporcie.
    """
    
    imp= get_object_or_404(ImportSprzedazy, pk= imp_id)
    
    return render_to_response('bra/sprzedaz/rozwin.html',
                        { 
                                'imp': imp,
                        }, 
                        context_instance= RequestContext(request))
    
    
def bra_sprzedaz_importy(request, firma):
    """
    Lista plików JPK.
    """
    return render_to_response('bra/sprzedaz/importy.html', 
                              { 
                                'FIRMA': settings.FIRMA,
                                'firma': firma,
                              }, 
                              context_instance= RequestContext(request))
    
    
def bra_ajax_importy(request, firma):
    
    return HttpResponse(json.dumps(
                        {'data': [imp.to_json() for imp in ImportSprzedazy.objects.filter(firma__oznaczenie= firma).order_by('-id')]}
                    ), content_type='application/json')
    

def bra_faktury(request):
    """
    Lista plików JPK.
    """
    return render_to_response('bra/faktury.html', 
                              { 
                                'FIRMA': settings.FIRMA,
                                'firma': 'jet',
                              }, 
                              context_instance= RequestContext(request))
    
    
def bra_ajax_faktury(request):
    
    return HttpResponse(json.dumps(
                        {'data': [fak.to_json() for fak in Faktura.objects.all().order_by('id')]}
                    ), content_type='application/json')


def bra_ajax_konto(request, firma, konto):
    data= {'nazwa': ''}
    
    if konto:
        konto= re.sub('-', '', konto)
        
    if len(konto)>0:
        try:
            ana= Ana.objects.using(settings.DBS(firma)).get(numer_a= konto)
            data['nazwa']= ana.nazwa_a.strip()
        except:
            data['errors']= 'Nie ma konta o podanym numerze'
            data['nazwa']= data['errors']
    
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def bra_sprzedaz_xlsx(request, imp_id):
    """
    Wyświetlenie zeszytu z wszystkimi arkuszami kontrolnymi pliku JPK.
    """

    # Pobranie pliku JPK w tym xml    
    imp= get_object_or_404(ImportSprzedazy, pk= imp_id)
    
    xlsx= xls.raport_kontrolny(imp)
        
    response= HttpResponse(content_type= 'application/vnd.ms-excel')
    response['Content-Disposition']= 'attachment; filename="{}.xlsx"'.format('{} Import Sprzedazy {}'.format(imp.firma.oznaczenie.upper(), imp.id))
    response.write(xlsx)
    
    return response
