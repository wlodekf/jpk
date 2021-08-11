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
from bra.models import ApiSprzedaz

from .forms import ApiSprzedazForm
from .sprzedaz import Sprzedaz

logger= logging.getLogger(__name__)


@login_required
def sprzedaz_importuj(request, firma= None): 
    """
    Import dokumentów przychodowych i zapisanie ich w rejestrze sprzedaży VAT. 
    """
    
    firma= get_object_or_404(Firma, oznaczenie= firma)

    if request.method == 'POST':
        form= ApiSprzedazForm(firma, request.POST)
        
        if form.is_valid():
            sprzedaz= Sprzedaz(firma)
            sprzedaz.importuj_sprzedaz(form.cleaned_data['od_daty'], form.cleaned_data['do_daty'], request.user.username)
            return HttpResponseRedirect(reverse('api-sprzedaz-importy', args= [firma.oznaczenie]))        
        else:
            logger.warning(form)
                        
    else:
        form= ApiSprzedazForm(firma, initial= {})

    return render_to_response('api/sprzedaz/import.html', 
                              { 
                                'FIRMA': settings.FIRMA,
                                'firma': firma.oznaczenie,
                                'form': form,
                                'ws_host': settings.WS_HOST
                              }, 
                              context_instance= RequestContext(request))  



def sprzedaz_importy(request, firma):
    """
    Lista importów zakupów.
    """
    return render_to_response('api/sprzedaz/importy.html', 
                              { 
                                'FIRMA': settings.FIRMA,
                                'firma': firma,
                              }, 
                              context_instance= RequestContext(request))



def sprzedaz_importy_ajax(request, firma):
    
    return HttpResponse(json.dumps(
                        {'data': [imp.to_json() for imp in ApiSprzedaz.objects.filter(firma__oznaczenie= firma).order_by('-id')]}
                    ), content_type='application/json')

    
 
@login_required
def sprzedaz_rozwin_ajax(request, imp_id):
    """
    Pobranie rozwinięcia informacji o imporcie zakupów.
    """
    
    imp= get_object_or_404(ApiSprzedaz, pk= imp_id)
    
    return render_to_response('api/sprzedaz/rozwin.html',
                        { 
                                'imp': imp,
                        }, 
                        context_instance= RequestContext(request))
    


@login_required
def sprzedaz_xlsx(request, imp_id):
    """
    Wyświetlenie zeszytu z wszystkimi arkuszami kontrolnymi pliku JPK.
    """

    # Pobranie pliku JPK w tym xml    
    imp= get_object_or_404(ApiSprzedaz, pk= imp_id)
    
    response= HttpResponse(content_type= 'application/vnd.ms-excel')
    response['Content-Disposition']= 'attachment; filename="{}-{}.xlsx"'.format("import_sprzedazy", imp_id)

    response.write(imp.xls)
    
    return response

