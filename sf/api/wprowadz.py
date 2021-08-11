# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse

from app.models import Plik
from sf.models import Sprawozdanie, Wprowadzenie
from . import access_control, txt2data
from sf.api import views

import logging
logger= logging.getLogger(__name__)
logger_email= logging.getLogger('sf')


def wprowadz(request, jpk_id):
    if request.method == 'GET':
        if request.META.get('HTTP_ACCEPT') == 'application/json':
            return wprowadz_get(request, jpk_id)
        else:
            return views.jpk_sf(request, jpk_id, 'wprowadz')
    
    if request.method == 'PATCH':
        return wprowadz_save(request, jpk_id)
    
    return None


def wprowadz_get(request, jpk_id):
    """
    Dane wprowadzenie do sprawozdania.
    """

    # Pobranie pliku JPK w tym xml    
    jpk= get_object_or_404(Plik, pk= jpk_id)
    
    spraw= Sprawozdanie.objects.get(jpk= jpk)
    
    return access_control(JsonResponse({'form': spraw.to_json()}))


def wprowadz_save(request, jpk_id):
    """
    Pozycje podanego raportu.
    """

    if request.method == 'PATCH':
        
        w= json.loads(request.PATCH.get('data'))
        
        s= Sprawozdanie.objects.get(jpk_id=int(jpk_id))
    
        s.p0_data_sporzadzenia= txt2data(w.get('p0_data_sporzadzenia'))
        
        s.p1_nazwa_firmy= w['p1_nazwa_firmy']
        s.p1_wojewodztwo= w['p1_wojewodztwo']
        s.p1_powiat= w['p1_powiat']
        s.p1_gmina= w['p1_gmina']
        s.p1_miejscowosc= w['p1_miejscowosc']
        s.p1_kod_pocztowy= w['p1_kod_pocztowy']
        s.p1_poczta= w['p1_poczta']
        s.p1_ulica= w['p1_ulica']
        s.p1_nr_domu= w['p1_nr_domu']
        s.p1_nr_lokalu= w['p1_nr_lokalu']
        s.p1_pkd= w['p1_pkd']
        s.p1_nip= w['p1_nip']
        s.p1_krs= w['p1_krs']
        
        s.p2_data_od= txt2data(w.get('p2_data_od'))
        s.p2_data_do= txt2data(w.get('p2_data_do'))
        s.p2_data_do_opis= w.get('p2_data_do_opis')
 
        s.p3_data_od= txt2data(w.get('p3_data_od'))
        s.p3_data_do= txt2data(w.get('p3_data_do'))
             
        s.p4_laczne= w.get('p4_laczne')
        
        s.p5_kontynuacja= w.get('p5_kontynuacja')
        s.p5_brak_zagrozen= w.get('p5_brak_zagrozen')
        s.p5_opis_zagrozen= w.get('p5_opis_zagrozen')

        s.p6_po_polaczeniu= w.get('p6_po_polaczeniu')
        s.p6_metoda= w.get('p6_metoda')

        s.p7_zasady= w.get('p7_zasady', '-')
        s.p7_wycena= w.get('p7_wycena', '-')
        s.p7_wynik= w.get('p7_wynik', '-')
        s.p7_spraw= w.get('p7_spraw', '-')
        
        s.save()
        
        # Zapisanie wprowadzeń
        p8= w.get('p8')
        for w in p8:
            try:
                wpr= Wprowadzenie.objects.get(id= int(w.get('p8_id')))
            except Wprowadzenie.DoesNotExist:
                wpr= Wprowadzenie(sprawozdanie=s)
                
            wpr.nazwa= w.get('p8_nazwa')
            wpr.opis= w.get('p8_opis')
            wpr.save()
            
        # PATH powinien zwracać zaktualizowane dane
        
    return access_control(HttpResponse("OK"))


def p8(request, jpk_id, p8_id= None):
    if request.method == 'POST':
        return wprowadz_p8save(request, jpk_id, p8_id)
    if request.method == 'PATCH':
        return wprowadz_p8save(request, jpk_id, p8_id)
    if request.method == 'DELETE':
        return wprowadz_p8del(request, jpk_id, p8_id)
        
    return None


def wprowadz_p8save(request, jpk_id, p8_id):
    """
    Utworzenie nowego lub aktualizacja istniejącego wyjaśnienia
    """

    w= json.loads(getattr(request, request.method).get('data'))
    s= Sprawozdanie.objects.get(jpk_id=int(jpk_id))
    
    if request.method == 'POST' or request.method == 'PATCH':
        p8_id= int(p8_id) if p8_id else 0
        
        try:
            wpr= Wprowadzenie.objects.get(id= p8_id)
        except Wprowadzenie.DoesNotExist:
            wpr= Wprowadzenie(sprawozdanie=s)
            
        wpr.nazwa= w.get('p8_nazwa')
        wpr.opis= w.get('p8_opis')
        
        wpr.save()
        
        p8_id= wpr.id
        
        # POST, PUT, PATH powinien zwracać opis nowego/zaktualizowanego obiektu    
        return access_control(JsonResponse(wpr.to_json()))
    
    return None
        

def wprowadz_p8del(request, jpk_id, p8_id):
    """
    Wyświetlenie formularza do wprowadzania danych danego raportu.
    """

    # Pobranie pliku JPK w tym xml    
    jpk= get_object_or_404(Plik, pk= jpk_id)
    
    spraw= Sprawozdanie.objects.get(jpk= jpk)
    
    p8= Wprowadzenie.objects.get(sprawozdanie=spraw, id=int(p8_id))
    p8.delete()
    
    return access_control(JsonResponse({'status': 0}))
