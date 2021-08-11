# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import re

from django.template.defaultfilters import stringfilter
from django import template

register= template.Library()

import locale
locale.setlocale(locale.LC_ALL, 'pl_PL.UTF-8')

@register.filter
@stringfilter
def tkwotowy(val):
    val= '{:.2f}'.format(float(val or 0.0))   
    return val


@register.filter
@stringfilter
def tkwotowy_zl(val):
    val= '{:.0f}'.format(float(val or 0.0))   
    return val


@register.filter
@stringfilter
def kwotac(val):
    if isinstance(val, str):
        val= val.replace(' ', '')
    val= '{:,.0f}'.format(float(val)).replace(',',' ') if val else ''  
    if val == '0':
        val= '' 
    return val


@register.filter
@stringfilter
def kwota(val):
    val= '{:,.2f}'.format(float(val or 0.0))   
    return val


@register.filter
@stringfilter
def tznakowy(val):
    if not val or len(val) == 0: 
        return '-'
    return val if len(val)<=256 else val[:256]


@register.filter
@stringfilter
def tznakowy_brak(val):
    if not val or len(val) == 0: 
        return 'BRAK'
    return val if len(val)<=256 else val[:256]


@register.filter
@stringfilter
def ttekstowy(val):
    if not val or len(val) == 0 or str(val).startswith('<memory'):
        return '-'
    return val if len(val)<=3500 else val[:3500]


@register.filter
@stringfilter
def kwota_pl(val):
    val= '{:.2f}'.format(float(val or 0.0))
    val= val.replace('.', ',')   
    return '.'.join(re.findall('((?:\d+\,)?(?:\d{1,3}\-?))', val[::-1]))[::-1]


@register.filter
@stringfilter
def tilosci(val):
    val= '{:.6f}'.format(float(val or 0.0))   
    return val 


@register.filter
@stringfilter
def liczba_pl(val):
    val= '{}'.format(int(val or 0))   
    return ' '.join(re.findall('((?:\d+\,)?(?:\d{1,3}\-?))', val[::-1]))[::-1]


@register.filter
@stringfilter
def tnrnip(val):
    return val
    if val[1:3] == '00': 
        val= '{}1{}'.format(val[:2], val[3:])
    if len(val)<10:
        val= val+('0'*(10-len(val)))
    return val[:10] 


@register.filter
@stringfilter
def do1spacji(text):
    return re.sub(r'\s+', ' ', text)


@register.filter
@stringfilter
def czas_trwania(czas):
    return str(czas)[:7]


@register.filter
@stringfilter
def stawka(vat):
    if vat == 'ZW.': return 'zw'
    if vat == 'OO.': return 'oo'
    if vat == 'NO.': return 'np'
    
    return re.sub('\D', '', vat)


@register.filter
@stringfilter
def pop_poczatek(dummy):
    dzis= datetime.date.today()
    ten_pierwszy= datetime.date(dzis.year, dzis.month, 1)
    pop_ostatni= ten_pierwszy - datetime.timedelta(days= 1)
    return datetime.date(pop_ostatni.year, pop_ostatni.month, 1)

@register.filter
@stringfilter
def pop_koniec(dummy):
    dzis= datetime.date.today()
    ten_pierwszy= datetime.date(dzis.year, dzis.month, 1)
    return ten_pierwszy - datetime.timedelta(days= 1)
    

@register.filter   
def element(raport, element):
    return raport.el(element)

