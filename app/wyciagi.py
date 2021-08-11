# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import decimal
import logging
import re
import datetime

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response 
from django.template import RequestContext
from app.models import Wyciag

logger= logging.getLogger(__name__)


@login_required 
def wyciag_upload(request, bank):  
    """
    Wgranie pliku wyciągu bankowego.
    """
    
    if request.method == 'POST':
        uploaded_file= request.FILES.get('file')
        if uploaded_file:
            if bank.lower() == 'ing': importuj_ing(uploaded_file)
            if bank.lower() == 'mbank': importuj_mbank(uploaded_file)            
                
    return HttpResponseRedirect(reverse('home'))



@login_required
def wyciag_import(request, bank):  
    """
    Wgranie pliku wyciągu bankowego.
    """
    
    return render_to_response('app/wyciag.html', 
                            { 
                                'bank': bank
                            }, 
                            context_instance= RequestContext(request))


def strip(lines):
    for line in lines:
        line= line.replace('\r', '')
        line= line.rstrip()
        if line.strip() == '-':
            continue
        if line:
            yield line
        
def nowy_wyciag(op):
    dw= op['data_wyciagu']
    data= datetime.date(2000+int(dw[:2]), int(dw[2:4]), int(dw[4:]))
    stare= Wyciag.objects.filter(nr_rachunku= op['nr_rachunku'], nr_wyciagu= int(op['nr_wyciagu']), data= data)
    stare.delete()

    
def norms(s):
    return re.sub('\s+', ' ', s.strip()) if s else s


def zapisz(op):
    if op['kwota'] is not None and op['kod_operacji'] != 'S940':
        op['saldo']= op['saldo'] + op['kwota']
    
        Wyciag.objects.create(nr_rachunku= op['nr_rachunku'],
                              nr_wyciagu= op['nr_wyciagu'],
                              waluta= op['waluta'],
                              kod= op['kod_operacji'],
                              data= op['data'],
                              kwota= op['kwota'],
                              opis= norms(op['opis']),
                              podmiot= norms(op['podmiot']),
                              saldo= op['saldo']
                              )
    
    return {'nr_rachunku': op.get('nr_rachunku'), 
            'nr_wyciagu': op.get('nr_wyciagu'),
            'waluta': op.get('waluta'),
            'saldo': op.get('saldo'),
            'kwota': None}
            

def importuj_ing(plik):
    
    data= plik.read().decode('852')
        
    data= '\n'.join(strip(data.split('\n')))
    
    tag_re= re.compile(r'^:(?P<full_tag>(?P<tag>[0-9]{2})(?P<sub_tag>[A-Z])?):', re.MULTILINE)
    matches= list(tag_re.finditer(data))
    
    op= {}
    
    for i, match in enumerate(matches):
        tag= match.group('full_tag')
        
        if matches[i + 1:]:
            tag_data = data[match.end():matches[i + 1].start()].strip()
        else:
            tag_data = data[match.end():].strip()
        
        if tag == '25':
            if op.get('data'): op= zapisz(op)
            
            op['nr_rachunku']= tag_data[1:]
            
        if tag == '28C':
            if op.get('data'): op= zapisz(op)
            
            op['nr_wyciagu']= tag_data
        
        if tag == '60F':
            if op.get('data'): op= zapisz(op)  
            
            op['data_wyciagu']= tag_data[1:7]
            op['waluta']= tag_data[7:10]
            op['saldo']= decimal.Decimal(tag_data[10:].replace(',', '.'))
            nowy_wyciag(op)
            
            if tag_data[0] == 'D':
                op['saldo']= - op['saldo']
            
        if tag == '61':
            if op.get('data'): op= zapisz(op)
            
            op['data']= datetime.date(2000+int(tag_data[:2]), int(tag_data[6:8]), int(tag_data[8:10]))
            
            op['kwota']= decimal.Decimal(re.search('[\d,]{1,15}', tag_data[11:]).group(0).replace(',','.'))
            if tag_data[10] == 'D':
                op['kwota']= - op['kwota']
                
            op['kod_operacji']= re.search('S\d{3}', tag_data[12:]).group(0)
    
        if tag == '86':
            opis= re.sub('\n', '', tag_data).split('~')
            if len(opis)>1:
                opis_operacji= []
                nazwa_podmiotu= []
                for po in opis:
                    if po[:2] in ('20', '21', '22', '23', '24', '25', '26', '27', '28'):
                        opis_operacji.append(po[2:])
                    if po[:2] in ('32', '33', '62', '63'):
                        nazwa_podmiotu.append(po[2:])
                op['opis']= ''.join(opis_operacji)
                op['podmiot']= ''.join(nazwa_podmiotu)



def importuj_mbank(plik):
    data= plik.read().decode('ISO-8859-2')
    data= '\n'.join(strip(data.split('\n')))
    
    tag_re= re.compile(r'^:(?P<full_tag>(?P<tag>[0-9]{2})(?P<sub_tag>[A-Z])?):', re.MULTILINE)
    matches= list(tag_re.finditer(data))
    
    op= {}
    
    for i, match in enumerate(matches):
        tag= match.group('full_tag')
        
        if matches[i+1:]:
            tag_data= data[match.end():matches[i+1].start()].strip()
        else:
            tag_data= data[match.end():].strip()
        
        if tag == '25':
            if op.get('data'): op= zapisz(op)
            
            op['nr_rachunku']= tag_data
            
        if tag == '28C':
            if op.get('data'): op= zapisz(op)
            
            op['nr_wyciagu']= re.search('\d+', tag_data).group(0)
        
        if tag == '60F':
            if op.get('data'): op= zapisz(op)  
            
            op['data_wyciagu']= tag_data[1:7]
            op['waluta']= tag_data[7:10]
            op['saldo']= decimal.Decimal(tag_data[10:].replace(',', '.'))
            nowy_wyciag(op)
            
            if tag_data[0] == 'D':
                op['saldo']= - op['saldo']
            
        if tag == '61':
            if op.get('data'): op= zapisz(op)
            
            op['data']= datetime.date(2000+int(tag_data[:2]), int(tag_data[6:8]), int(tag_data[8:10]))
            
            op['kwota']= decimal.Decimal(re.search('[\d,]{1,15}', tag_data[11:]).group(0).replace(',','.'))
            if tag_data[10] == 'D':
                op['kwota']= - op['kwota']
                
            op['kod_operacji']= re.search('\n(\d+)-', tag_data[12:]).group(1)
    
        if tag == '86':
            opis= re.sub('\n', '', tag_data)

            kon_m= re.search(r'KONTRAHENT:(.*?); (.*?);', opis)
            if kon_m:
                op['podmiot']= kon_m.group(2)
            else:
                od_m= re.search(r'OD:(.*?);', opis, re.UNICODE)
                if od_m:
                    op['podmiot']= od_m.group(1)
                else:
                    op['podmiot']= opis
                                    
            tyt_m= re.search(r'TYT\.:(.*?);', opis, re.UNICODE)
            if tyt_m:                                    
                op['opis']= tyt_m.group(1)
            else:
                op['opis']= opis
              
    zapisz(op)
    