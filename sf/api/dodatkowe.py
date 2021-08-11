# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import re

from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse

from app.models import Plik
from sf.models import Sprawozdanie, Dodatkowe
from sf.api import views
from . import access_control 

import logging
logger= logging.getLogger(__name__)
logger_email= logging.getLogger('sf')

    
def dodatkowe(request, jpk_id, id= None):
    
    if request.method == 'GET':
        if request.META.get('HTTP_ACCEPT') == 'application/json':
            if id:
                return dodatkowe_pozycja(request, jpk_id, id)
            else:
                return dodatkowe_pozycje(request, jpk_id)
        else:
            return views.jpk_sf(request, jpk_id, 'dodatkowe')
                    
    if request.method == 'POST':
        return dodatkowe_save(request, jpk_id)
    if request.method == 'PATCH':
        return dodatkowe_save(request, jpk_id, id)
    if request.method == 'DELETE':
        return dodatkowe_del(request, jpk_id, id)
        
    return None


def dodatkowe_pozycja(request, jpk_id, id):
    """
    Pozycje podanego raportu.
    """
    
    pozycja= Dodatkowe.objects.get(sprawozdanie__jpk_id= int(jpk_id), id= id)
    
    return access_control(JsonResponse(pozycja.to_json()))


def dodatkowe_pozycje(request, jpk_id, id= None):
    """
    Pozycje podanego raportu.
    """
    
    pozycje_dodatkowe= Dodatkowe.objects.filter(sprawozdanie__jpk_id= int(jpk_id)).order_by('id')
    
    pozycje= [poz.to_json() for poz in pozycje_dodatkowe]
        
    return access_control(JsonResponse({'pozycje': pozycje,}))


def dodatkowe_save(request, jpk_id, poz_id= None):
    """
    Pozycje podanego raportu.
    """

    jpk_id= int(jpk_id)

    form= getattr(request, request.method).get('form')
    form= json.loads(form) if form else {}
    
    if poz_id:
        pozycja= Dodatkowe.objects.get(id= int(poz_id))
        pozycja.opis= form.get('opis')
    else:
        sprawozdanie= Sprawozdanie.objects.get(jpk_id= jpk_id)
        pozycja= Dodatkowe(opis= form.get('opis'), sprawozdanie=sprawozdanie)
        
    uploaded_file= request.FILES.get('file')
    if uploaded_file:
        plik= uploaded_file.read()
        pozycja.zawartosc= plik
        pozycja.nazwa= str(uploaded_file)
        
        nazwa= pozycja.nazwa.translate(str.maketrans('ąćęłńóśźżĄĆĘŁŃÓŚŹŻ', 'acelnoszzACELNOSZZ'))
        nazwa= re.sub('[^a-zA-Z0-9_\.\-]', '_', nazwa)
        nazwa= re.sub('_+', '_', nazwa)
        
        # W razie gdyby nazwa była za długa tak ją obcinamy aby zachować
        # rozszerzenie bo jest ono istotne dla poprawnego działania 
        # pobierania załączników
        
        czesci= nazwa.split('.')
        nazwa= '.'.join(czesci[:-1])
        ext= czesci[-1]

        nazwa= nazwa[:55-len(ext)-1]
        pozycja.nazwa= nazwa+'.'+ext
        
    pozycja.save()
        
    return access_control(JsonResponse({'poz': pozycja.to_json(), 'status': 0}))


def dodatkowe_del(request, jpk_id, poz_id):
    """
    Wyświetlenie formularza do wprowadzania danych danego raportu.
    """

    # Pobranie pliku JPK w tym xml    
    jpk= get_object_or_404(Plik, pk= jpk_id)
    spraw= Sprawozdanie.objects.get(jpk= jpk)
    
    zalacznik= Dodatkowe.objects.get(sprawozdanie=spraw, id=int(poz_id))
    zalacznik.delete()
    
    return access_control(JsonResponse({'status': 0}))


def dodatkowe_plik(request, jpk_id, id):
    """
    Pobranie określonego załącznika.
    Już zbędna! 
    Załącznik pobierany jest bezpośrednio z XML przy pomocy data url.
    """

    jpk= get_object_or_404(Plik, pk= jpk_id)
    spraw= Sprawozdanie.objects.get(jpk= jpk)
    
    zalacznik= Dodatkowe.objects.get(sprawozdanie=spraw, id=int(id))
    
    import mimetypes
    content_type = mimetypes.guess_type(zalacznik.nazwa)

    response= HttpResponse(content_type= content_type[0])
    response['Content-Disposition']= 'attachment; filename="{}"'.format(zalacznik.nazwa)
 
    response.write(zalacznik.zawartosc)
    
    return response
