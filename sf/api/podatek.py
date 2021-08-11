# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import decimal
import json

from django.http import HttpResponse, JsonResponse

from app.models import Plik
from sf.models import Podatek, Sprawozdanie
from sf.api import views
from . import access_control

import logging
from pip._vendor.requests.models import Response
logger= logging.getLogger(__name__)
logger_email= logging.getLogger('sf')


def podatek(request, jpk_id):
    if request.method == 'GET':
        if request.META.get('HTTP_ACCEPT') == 'application/json':
            return podatek_pozycje(request, jpk_id)
        else:
            return views.jpk_sf(request, jpk_id, 'podatek')
        
    if request.method == 'PATCH':
        return podatek_save(request, jpk_id)
    
    return None

    
def podatek_pozycje(request, jpk_id):
    """
    Pozycje rozliczenia różnicy podatkowej.
    """

    jpk_id= int(jpk_id)
    raport_podatku= Podatek.objects.filter(sprawozdanie__jpk_id= jpk_id).order_by('klucz')
#     Pozycja.obliczenia_zalezne(pozycje_raportu)
    
    pozycje= [poz.to_json() for poz in raport_podatku]
        
    return access_control(JsonResponse({'raport': {}, 'pozycje': pozycje }), True)


def podatek_save(request, jpk_id):
    """
    Pozycje podanego raportu.
    """

    pozycje= json.loads(request.PATCH.get('data'))
    sprawozdanie= Sprawozdanie.objects.get(jpk_id= int(jpk_id))
    
    for poz in pozycje:
        
        poz_id= poz.get('id')
        if poz_id:
            pozycja= Podatek.objects.get(id=poz_id)
        else:
            klucz= poz.get('klucz')
            pozycja= Podatek(id= 0, sprawozdanie= sprawozdanie, klucz= klucz, element='Pozostale' if klucz[-1]=='X' else 'PozycjaUzytkownika')

        if poz.get('deleted'):
            pozycja.delete()
            continue
        
        kwota_a= round(float(poz.get('a', 0) or 0), 2)
        kwota_b= round(float(poz.get('b', 0) or 0), 2)
        kwota_c= round(float(poz.get('c', 0) or 0), 2)

        _kwota_a= round(float(poz.get('_a', 0) or 0), 2)
        _kwota_b= round(float(poz.get('_b', 0) or 0), 2)
        _kwota_c= round(float(poz.get('_c', 0) or 0), 2)
                
        pozycja.rb_lacznie= kwota_a
        pozycja.rb_kapitalowe= kwota_b
        pozycja.rb_inne= kwota_c
        
        pozycja.pp_art= poz.get('ppa')
        pozycja.pp_ust= poz.get('ppb')
        pozycja.pp_pkt= poz.get('ppc')
        pozycja.pp_lit= poz.get('ppd')
        
        pozycja.rp_lacznie= _kwota_a
        pozycja.rp_kapitalowe= _kwota_b
        pozycja.rp_inne= _kwota_c
        
        pozycja.nazwa= poz.get('nazwa')
        pozycja.klucz= poz.get('klucz')
        
#         if pozycja.id:
        pozycja.save()
#         else:
#             pozycja= Podatek.objects.create(pozycja)
        
        if pozycja.element == 'P_ID_11':
            jpk= Plik.objects.get(id= int(jpk_id))
            ctrl= jpk.podsumowania.get(tabela= 'podatek')
            ctrl.suma1= pozycja.rb_lacznie
            ctrl.suma2= pozycja.rp_lacznie
            ctrl.save()
                    
#         pozycja= Podatek.objects.get(id=poz_id)
                
    return podatek_pozycje(request, jpk_id)

#     return access_control(HttpResponse("OK"))
        