# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
import decimal
import datetime
import re


class Record(object):
    def __init__(self, **kwargs):
        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])
            
    def __repr__(self):
        return str(self.netto)


def strip_tail_spaces(self, *args, **kwargs):
    atr= args[0]
    ss= True
    if len(atr)<=2: ss= False
    if atr[0] == '_': ss= False
    if atr[-1] == '_': ss= False
     
    if ss: 
        val= models.Model.__getattribute__(self, atr)
        return val.strip() if val else ''
    else:
        val= models.Model.__getattribute__(self, *args, **kwargs)
        return val


def poczatek_miesiaca(miesiac):
    rok= int(miesiac[:4])
    msc= int(miesiac[5:])
    return datetime.date(year= rok, day= 1, month= msc)
    
    
def koniec_miesiaca(miesiac):
    rok= int(miesiac[:4])
    msc= int(miesiac[5:])
    if msc == 12:    
        return datetime.date(year= rok, day= 31, month= 12)
    else:
        return datetime.date(year= rok, day= 1, month= msc+1) - datetime.timedelta(days=1)
    
    
def grosze(val):
    """
    Zaokrąglenie do groszy.
    """
    return decimal.Decimal(str(val)).quantize(decimal.Decimal('.01'), rounding= decimal.ROUND_HALF_UP)

    

def kwota_format(val): 
    val= '{:.2f}'.format(val)   
    val= val.replace('.',',')
    return '.'.join(re.findall('((?:\d+\,)?(?:\d{1,3}\-?))', val[::-1]))[::-1]

