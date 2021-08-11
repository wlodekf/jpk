# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from app.models import Plik, Firma


@login_required
def jpk_lista(request, firma):

    # Pomijamy pola tekstowe ponieważ ich pobieranie/dekompresja stanowi duży narzut
    pliki= Plik.objects.filter(firma__oznaczenie=firma).order_by('-id').only('id', 'utworzony', 'kod', 'dataod', 'datado', 'nazwa', 'rachunek', 'magazyn', 'wariant', 'cel_zlozenia', 'stan', 'odkad', 'czesc', 'utworzony_user', 'task')
    data= [jpk.to_json() for jpk in pliki]

    return HttpResponse(json.dumps({'data': data}),
                        content_type='application/json')


@login_required
def lista_firm(request):
    
    return render_to_response('app/ajax/lista_firm.json', 
                              { 
                                'firmy': Firma.firmy()
                              }, 
                              context_instance= RequestContext(request),
                              content_type='application/json')
