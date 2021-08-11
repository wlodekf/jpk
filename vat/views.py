# -*- coding: utf-8 -*- 

from __future__ import unicode_literals

import datetime
import traceback
import zeep
import requests

from django.http import HttpResponse

from .models import KonVat, KonKrs

WSDL_URL= 'https://sprawdz-status-vat.mf.gov.pl?wsdl'

client_mf= None
# try:
#     transport = zeep.transports.Transport(timeout=20, operation_timeout=10)
#     client_mf= zeep.Client(WSDL_URL, transport= transport)
# except:
#     traceback.print_exc()


def mf_sprawdz_nip(nip):
    """
    Ustalenie statusu aktywności VAT (czy jest czynny) kontrahenta o podanym NIP.
    """
    global client_mf

    nip= nip.strip()
    status_kod= "?"
    start= datetime.datetime.now()
    result= ''

    try:
        if client_mf is None:
            transport = zeep.transports.Transport(timeout=20, operation_timeout=10)
            client_mf= zeep.Client(WSDL_URL, transport=transport)

        result= client_mf.service.SprawdzNIP(nip)
        status_kod= result['Kod']
        
        print('Status podatnika VAT {}:{}, czas={}'.format(nip, status_kod, (datetime.datetime.now()-start).microseconds/1000))
    except (zeep.exceptions.XMLSyntaxError, zeep.exceptions.TransportError) as e1:
        print('SprawdzNIP exception: {0} {1!r}'.format(e1, e1.args))
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e2:
        print('SprawdzNIP błąd połączenia: {0} {1!r}'.format(type(e2), e2.args)) 
    except Exception as e:
        print('An exception of type {0} occurred. Arguments:\n{1!r}'.format(type(e), e.args))
        print('mf_czynny_nip Error: result={}'.format(result))
#       traceback.print_exc()

    return status_kod

    
def kon_nip_status(nip):
    """
    Sprawdzenie w rejestrze MF czy podatnik o podanym numerze VAT jest czynnym podatnikiem VAT.
    Zapisanie wyniku w kon_vat.
    """

    nip= nip.replace('-', '').replace(' ', '')
    
    vat= "?"
    try:    
        vat= mf_sprawdz_nip(nip)
        
        kon_vat= KonVat.objects.filter(nip= nip, aktualny='T')
        if kon_vat:
            kon_vat= kon_vat[0]

            if vat == kon_vat.vat:
                # Status bez zmian, aktualizujemy liczbę sprawdzeń i datę ostatniego sprawdzenia
                kon_vat.ostatnio= datetime.datetime.now()
                kon_vat.sprawdzany += 1
            else:
                # Zmiana statusu, dezaktywujemy poprzedni
                kon_vat.aktualny= 'N'
                kon_vat.save()
                # Tworzymy nowe info o statusie
                kon_vat= KonVat(nip=nip, vat=vat)
        else:
            # Nie był dotychczas sprawdzany - tworzymy nowy wpis
            kon_vat= KonVat(nip=nip, vat=vat)
            
        kon_vat.save()
        
    except:
        traceback.print_exc()
         
    return vat


def msg_statusu_nip(status):
    msg, level= None, 'warn'
    if status == 'N': msg= 'Podmiot o podanym NIP {} nie jest zarejestrowany jako podatnik VAT'
    if status == 'Z': msg= 'Podmiot o podanym NIP {} jest zarejestrowany jako podatnik VAT zwolniony'
    if status == 'I': msg, level= 'Nieprawidłowy NIP {}', 'error'
    return msg, level


def czynny(request, nip):
    """
    Sprawdzenie w rejestrze MF czy podatnik o podanym numerze VAT jest czynnym podatnikiem VAT.
    Zapisanie wyniku w kon_vat.
    """

    return HttpResponse(kon_nip_status(nip))


def krs(request, nip):
    """
    Ustalenie danych (nazwy, adresu, emaila) podmiotu w rejestrze KRS (strona mojepanstwo.pl) 
    na podstawie numeru NIP. 
    """
    def kon_skrot(skrot):
        if skrot.count('"') == 2:
            skrot= skrot.split('"')[1]
        return skrot

    def nazwa_fmt(nazwa, fmt, fmt2= None):
        if not fmt2:
            fmt2= fmt
        sa= nazwa.find(fmt)

        if sa > 0:
            n= nazwa.split(fmt)
            if sa > 80 and sa <= 120:
                nazwa= '{:120s}{} {}'.format(n[0], fmt2, n[1])
            elif sa > 40 and sa <= 80:
                nazwa= '{:80s}{} {}'.format(n[0], fmt2, n[1])
            elif sa < 40:
                nazwa= '{:40s}{} {}'.format(n[0], fmt2, n[1])
        return nazwa
    
    def kon_nazwa(nazwa):
        nazwa= nazwa_fmt(nazwa, 'SPÓŁKA AKCYJNA')
        nazwa= nazwa_fmt(nazwa, 'SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ', 'SP. Z O.O.')
        return nazwa
    
                                            
    url= 'https://api-v3.mojepanstwo.pl/dane/krs_podmioty.json?conditions[krs_podmioty.nip]='+nip
    
    r= requests.get(url)
    
    data= r.json()['Dataobject']
    if len(data) == 0:
        return HttpResponse('not found')
    
    try:
        data= data[0]['data']
        
        krs= KonKrs.objects.filter(nip= nip)
        if not krs:
            krs= KonKrs()
            krs.nip= nip
        else:
            krs= krs[0]
        
        krs.nazwa= kon_nazwa(data["krs_podmioty.nazwa"])
        krs.skrot= kon_skrot(data["krs_podmioty.nazwa_skrocona"])

        krs.ulica= data["krs_podmioty.adres_ulica"].upper()+" "+data["krs_podmioty.adres_numer"]
        if len(data["krs_podmioty.adres_lokal"]) > 0:
            krs.ulica += '/'+data["krs_podmioty.adres_lokal"]

        krs.kod=  data["krs_podmioty.adres_kod_pocztowy"]
        krs.miejscowosc= data["krs_podmioty.adres_miejscowosc"].upper()

        krs.wojewodztwo= '{:02d}'.format(int(data["krs_podmioty.wojewodztwo_id"]))
        krs.kraj= 'PL'
        krs.email= data["krs_podmioty.email"].lower()

        krs.save()

    except:
        traceback.print_exc()
         
    return HttpResponse(krs.nazwa)        

