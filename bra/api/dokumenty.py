from __future__ import unicode_literals

import datetime
import re
import requests

from django.conf import settings
from django.db.models import Max

from fk.models import Kon


class Dokumenty():
    """
    Import faktur zakupowych z API GDFIT (BBConnector) do FK.
    """

    HEADERS = {
        "Authorization": "a1f8c399ee60499ea2d2182bbcbf5859",
        "API-Version": "1.0",
        "ERP-Name": "noERP",
        "Content-Type": "application/json",
    }

    def __init__(self, firma):
        self.HEADERS['Authorization']= firma.api_auth
        self.firma= firma
        self.baza= firma.oznaczenie
        self.wczytaj_sposoby_platnosci() # do ustalania liczby dni na zapłatę
        self.numery= {}
        self.api_kon_id= 0
        self.api_kon= None
        self.imp= None
        self.raport= []



    def ustal_kon(self, k):
        """
        Odszukanie dostawcy w rejestrze kontrahentów lub
        utworzenie nowego. 
        """

        # Szukamy w kon pozycji z tym samym NIP oraz
        # nazwa, kod, miejsc, ulica

        nip= k['nip']
        nip= re.sub('-', '', nip)
        
        nazwa= k['nazwa1']
        if k['nazwa2']: 
            nazwa += k['nazwa2']
        if nazwa: nazwa= nazwa.upper()
        
        kod= k['kodPocztowy']
        kod= '-'.join(re.findall(r'\d+', kod))
        
        miejsc= k['miasto']
        if miejsc: miejsc= miejsc.upper()
        
        ulica= k['ulica']
        if ulica: ulica= ulica.upper()

        # Jeżeli jakiekolwiek dane kontrahenta zostały zmienione to 
        # tworzona jest nowa pozycja

        for kon in Kon.objects.using(settings.DBS(self.baza)).filter(id= nip).order_by('-kon_id'):
            return kon
        
        return self.nowy_kon(nip, nazwa, kod, miejsc, ulica, k)


    def nowy_kon(self, nip, nazwa, kod, miejsc, ulica, k):
        """
        Utworzenie nowego kontrahenta na podstawie danych z rejestru kontrahentów API.
        """

        print('NOWY_KON', k)
        
        kon= Kon(kon_id= 0, id= nip, nazwa= nazwa, kod= kod, miejsc= miejsc, ulica= ulica)

        kon.kraj= nip[:2] if re.match('[A-Z][A-Z]', nip) else 'PL'
        kon.idtyp= 'NIPUE' if re.match('[A-Z][A-Z]', nip) else 'NIP'

        # Wyznaczenie numeru nowego kontrahenta (z uwzględnieniem zagranicznych)        
        if kon.kraj == 'PL':
            nr_kon= Kon.objects.using(settings.DBS(self.baza)).filter(nr_kon__startswith= '0').aggregate(Max('nr_kon'))
            kon.nr_kon= '{:05d}'.format(int(nr_kon['nr_kon__max'].strip())+1)
        else:
            nr_kon= Kon.objects.using(settings.DBS(self.baza)).filter(nr_kon__startswith= 'Z').aggregate(Max('nr_kon'))
            kon.nr_kon= 'Z{:04d}'.format(int(nr_kon['nr_kon__max'][1:].strip())+1)         

        kon.skrot= k['nazwaSkrocona']
        if kon.skrot: kon.skrot= kon.skrot.upper()
        
        kon.tel= k['telefon'] 
        kon.e_mail= k['email'] 
        kon.fax= k['faks']
        kon.konto= k['bank']
        
        kon.www= k['www']
        if kon.www: kon.www= kon.www[:40].upper()
        
        kon.kto= 1
        kon.kiedy= datetime.date.today()

        kon.save(using= settings.DBS(self.baza))
        
        self.imp.ile_kon += 1

        return kon

                 
    def daj_api_kon(self, k):
        """
        Pobranie danych kontrahenta z API.
        """

        id_kontrahenta= k['idKontrahenta']
        
        # Sprawdzenie czy kontrahent nie został już wczytany

        if id_kontrahenta == self.api_kon_id:
            return self.api_kon

        # Pobranie danych kontrahenta z API (NIP)
                
        response = requests.get(
                self.firma.api_url+'/Kontrahenci',
                params= {
                    'id': id_kontrahenta,
                },
                headers = self.HEADERS,
                timeout=15
        )

        kon= self.api_json_decode(response.json())

        # Zbuforowanie wywołania API
                
        self.api_kon_id= id_kontrahenta
        self.api_kon= kon

        return kon
    
    

    def api_json_decode(self, data):
        """
        Wykasowanie znaków które się nie konwertują do bazy danych.
        """
        
        def decode(s):
            s= re.sub('\u2010', '-', s)
            s= re.sub('\u2013', '-', s)
            s= re.sub('\u2015', '-', s)
            
            s= re.sub('\u2019', "'", s)
            s= re.sub('\u201D', '"', s)
            return s
        
        if data:
            for (k,v) in data.items():
                if type(v) is str:
                    data[k]= decode(v)
        else:
            data= {}
        
        return data



    def kontrahenci(self):
        """
        Listing kontrahentów
        """
        response = requests.get(
                self.firma.api_url+'/Kontrahenci?fields=id,nip,nazwa1',
                headers = self.HEADERS,
                timeout=15
        )

        ile= 0
        for kon in response.json():
            ile += 1
            print(kon['id'], kon['nip'], kon['nazwa1'])
        print('ILE', ile)
        


    def rodzaje_dokumentow_kosztowych(self):
        """
        Listing rodzajów rokumentów kosztowych
        """
        response = requests.get(
                self.firma.api_url+'/RDK',
                headers = self.HEADERS,
                timeout=15
        )

        for rdk in response.json():
            print('{},{},{}'.format(rdk['identyfikatorWewnetrzny'], rdk['nazwaSkrocona'], rdk['nazwaPelna']))
            
            
            
    def listing_kosztow(self):
        """
        Wyświetlenie danych dokumentów kosztowych.
        """

        print('Pobieranie kosztow')

        response = requests.get(
            self.firma.api_url+'/Przychody/',
            params= {
                'dataod': '2019-11-01',
                'datado': '2019-11-30'
            },
            headers= self.HEADERS,
            timeout= 30
        )
        
        for k in response.json():
            print(k)

    
       
    def wczytaj_sposoby_platnosci(self):
        """
        Wczytanie słownika sposobów płatności do ustalania liczby dni na zapłatę.
        """

        print('Pobieranie sposobów płatności')
        print('URL', self.firma.api_url+'/SposobyPlatnosci/')
        print('HEADERS', self.HEADERS)

        response = requests.get(
            self.firma.api_url+'/SposobyPlatnosci/',
            params= {
            },
            headers= self.HEADERS,
            timeout= 30
        )
        
        print("RESP", response)
        print('JSON', response.json())

        self.platnosci= {}
        for s in response.json():
            self.platnosci[s['identyfikatorWewnetrzny']]= s
            
