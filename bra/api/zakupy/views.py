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

from app.models import Firma
from bra.models import ImportZakupow

from .forms import ApiZakupyForm
from .zakupy import Zakupy

logger= logging.getLogger(__name__)


@login_required
def zakupy_importuj(request, firma= None): 
    """
    Import dokumentów kosztowych i zapisanie ich w rejestrze zakupów VAT. 
    """
    
    firma= get_object_or_404(Firma, oznaczenie= firma)

    if request.method == 'POST':
        form= ApiZakupyForm(firma, request.POST)
        
        if form.is_valid():
            zakupy= Zakupy(firma)
            zakupy.importuj_zakupy(form.cleaned_data['od_daty'], form.cleaned_data['do_daty'], request.user.username)
            return HttpResponseRedirect(reverse('api-zakupy-importy', args= [firma.oznaczenie]))        
        else:
            logger.warning(form)
                        
    else:
        form= ApiZakupyForm(firma, initial= {})

    return render_to_response('api/zakupy/import.html', 
                              { 
                                'FIRMA': settings.FIRMA,
                                'firma': firma.oznaczenie,
                                'form': form,
                                'ws_host': settings.WS_HOST
                              }, 
                              context_instance= RequestContext(request))  


   
def zakupy_importy(request, firma):
    """
    Lista importów zakupów.
    """
    return render_to_response('api/zakupy/importy.html', 
                              { 
                                'FIRMA': settings.FIRMA,
                                'firma': firma,
                              }, 
                              context_instance= RequestContext(request))


def zakupy_importy_ajax(request, firma):
    
    return HttpResponse(json.dumps(
                        {'data': [imp.to_json() for imp in ImportZakupow.objects.filter(firma__oznaczenie= firma).order_by('-id')]}
                    ), content_type='application/json')
 
 
 
@login_required
def zakupy_rozwin_ajax(request, imp_id):
    """
    Pobranie rozwinięcia informacji o imporcie zakupów.
    """
    
    imp= get_object_or_404(ImportZakupow, pk= imp_id)
    
    return render_to_response('api/zakupy/rozwin.html',
                        { 
                                'imp': imp,
                        }, 
                        context_instance= RequestContext(request))


 
@login_required
def zakupy_xlsx(request, imp_id):
    """
    Wyświetlenie zeszytu z wszystkimi arkuszami kontrolnymi pliku JPK.
    """

    # Pobranie pliku JPK w tym xml    
    imp= get_object_or_404(ImportZakupow, pk= imp_id)
    
    response= HttpResponse(content_type= 'application/vnd.ms-excel')
    response['Content-Disposition']= 'attachment; filename="{}.xlsx"'.format("raport_kontrolny.xlsx")

    response.write(imp.xls)
    
    return response

