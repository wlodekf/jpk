# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

from copy import copy

import datetime
import decimal

from django.conf import settings
from django import db

import logging
logger= logging.getLogger(__name__)

class OperacjaNiedozwolona(Exception):
    pass

def par_firmy(par= None):
    pf= settings.PAR_FIRMY[settings.FIRMA]
    return pf.get(par) if par else pf

def grosze(w):
    return decimal.Decimal(w).quantize(decimal.Decimal('.01'), rounding= decimal.ROUND_HALF_UP)

def zlote(w):
    return decimal.Decimal(w).quantize(decimal.Decimal('1.'), rounding= decimal.ROUND_HALF_UP)

def procent(kwota, proc):
    return grosze(kwota * decimal.Decimal(proc) / decimal.Decimal(100.0))

def stawka(vat):
    return decimal.Decimal(vat[:-1] if vat[-1] == '%' else 0)
    
def ss(t):
    return t.strip() if t else ''

def data_na_miesiac(data):
    return '{:04d}/{:02d}'.format(data.year, data.month)


def dictify(r,root=True):
    if root:
        return {r.tag : dictify(r, False)}
    d= copy(r.attrib)
    if r.text:
        d["text"]=r.text
    for x in r.findall("./*"):
        if x.tag not in d:
            d[x.tag]=[]
        d[x.tag].append(dictify(x,False))
    return d


def alert(request, message, klasa= 'info'):
    """
    Zapisanie alertu do wyświetlenia po załadowaniu strony.
    """
    
    alerts= request.session.get('alert', [])
    alerts.append({'message': message.replace('\n', '<br/>'), 'klasa': klasa})
    request.session['alert']= alerts
    

start= 0

def LOG_sql_reset():
    
    global start
    start= datetime.datetime.now()
    logger.debug(start)
    db.reset_queries()


def LOG_sql_show(opis, plik = "default"):
    """
    Zapisanie do loga i pliku informacji o liczbie zapytań i 
    listy wszystkich zapytań od LOG-sql_reset.
    """    
    def log_db(dbs):
        for c in db.connections:
            print(c, db.connections[c].queries)
            
        cnt= len(db.connections[dbs].queries)
        log= dbs+'.log'
        logger.debug("Liczba zapytań SQL/{}({}): {}".format(opis, log, cnt)) 
        with open(log, "w") as _file:
            print("liczna zapytań: ", cnt, file= _file)
            print(db.connections['default'].queries, file= _file)        
        
    global start
    logger.debug(datetime.datetime.now())
    logger.debug('czas: {}'.format(datetime.datetime.now()-start))
    
    log_db('default')
    log_db(settings.LAST_DBS)


def test_dbs(pola):
    """
    Ustalenie bazy testowej.
    """    
    dbs= settings.LAST_DBS
    if 'dbs' in pola:
        dbs= pola['dbs']
        del pola['dbs']
    return dbs
