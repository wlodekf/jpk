# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import decimal
from . import access_control

from django.http import HttpResponse, JsonResponse

from app.models import Plik
from sf.models import Raport, Pozycja
from sf.api import views
from app.ctrl import sf as ctrl_sf 

import logging
logger= logging.getLogger(__name__)
logger_email= logging.getLogger('sf')


def pozycje(request, jpk_id, raport):

    if request.method == 'GET':
        if request.META.get('HTTP_ACCEPT') == 'application/json':
            return raport_pozycje(request, jpk_id, raport)
        else:
            return views.jpk_sf(request, jpk_id, raport)

    if request.method == 'PATCH':
        return raport_save(request, jpk_id, raport)
    
    return None
    
    
def raport_pozycje(request, jpk_id, raport):
    """
    Pozycje podanego raportu.
    """

    raport= Raport.objects.get(sprawozdanie__jpk_id= int(jpk_id), tabela= raport)
    
    pozycje_raportu= Pozycja.objects.filter(raport=raport)
    Pozycja.obliczenia_zalezne(pozycje_raportu)

    pozycje= [poz.to_json() for poz in pozycje_raportu]
#     print('\n'.join(['{} {} {} {} {}'.format(i, p.klu1, p.zalezne, p.oblicz or '', p.nazwa) for i, p in enumerate(pozycje_raportu)]))
        
    return access_control(JsonResponse({'raport': raport.to_json(), 'pozycje': pozycje}))


def raport_save(request, jpk_id, raport):
    """
    Zapisanie zmienionych pozycji podanego raportu.
    """
    PODSUM= {'Aktywa': 'Aktywa',
             'Pasywa': 'Pasywa',
             'RZiSKalk': 'O',
             'RZiSPor': 'L',
             'ZestZmianWKapitale': 'III',
             'PrzeplywyPosr': 'G',
             'PrzeplywyBezp': 'G'
            }
    
    # Sprawdzić czy metoda zapytania jest poprawna (PATCH)!
    # Sprawdzić poprawność jpk_id, raport?
    
    pozycje= request.JSON
    
    sum_el= None
    jpk= None
    raport= None
    ctrl= None
    
    formuly= False
    
    for poz in pozycje:
        
        poz_id= poz.get('id')
        kwota_a= round(float(poz.get('a', 0) or 0), 2)
        kwota_b= round(float(poz.get('b', 0) or 0), 2)
        
        pozycja= Pozycja.objects.get(id=poz_id)
        

        pozycja.kwota_a= kwota_a
        pozycja.kwota_b= kwota_b
        
        obl= poz.get('obl')
        if obl == '!@#':
            formuly= False
        else:
            formuly= True
            pozycja.oblicz= obl
            
        pozycja.save()
        
        if not sum_el:
            raport= Raport.objects.get(id=pozycja.raport_id)
            sum_el= PODSUM.get(raport.element)
            jpk= Plik.objects.get(id= raport.sprawozdanie.jpk_id)

        if sum_el == pozycja.el:
            ctrl= jpk.podsumowania.get(tabela= raport.tabela)
            ctrl.suma1= pozycja.kwota_a
            ctrl.suma2= pozycja.kwota_b
            
    
    if ctrl:        
        ctrl.save()
        
    if formuly:
        ctrl_sf.obliczenia(jpk, raport, ctrl)
        
    # PATCH powinien zwracać zaktualizowane dane, 
    # bo w czasie aktualizacji mogły się zmienić na serwerze 
    # (np. coś obliczone).
    
    return access_control(HttpResponse("OK"))

