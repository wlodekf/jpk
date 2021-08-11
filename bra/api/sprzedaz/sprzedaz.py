# -*- coding: utf-8 -*-

"""
Informacje w dokumencie przychodowym
------------------------------------------------------
'identyfikatorNaglowka': 381,
'identyfikatorPozycji': 737,
'idKontrahenta': 10938,
'idEtapuProjektu': -1,
'idMetodyPlatnosci': 5,

'rodzajDokumentu': 'Faktura',
'numerDokumentu': '2019/11/14',

'dataWystawienia': '2019-11-28T00:00:00',
'dataWykonanieUslugiDostawy': '2019-11-28T00:00:00',
'dataEwidencji': '2019-11-28T00:00:00',
'terminPlatnosci': '2019-12-28T00:00:00',

'dokumentRazemNetto': 32201.5,
'dokumentRazemVat': 7406.34,
'dokumentRazemBrutto': 39607.84,

'dekretNetto': 32201.5,
'dekretVat': 7406.34,
'dekretBrutto': 39607.84,

'dekretIlosc': 1.0,
'dekretJednostkaMiary': 'szt.',
'dekretCenaZaJednostke': 32201.5,

'metodaPlatnosci': 'Przelew 30 dni',
'zaplacony': 'T',

'grupaSyntetyczna': '501 - Koszty projektowe',
'kontoSyntetyczne': '01 - Przygotowanie projektu'
'kontoAnalityczne': '01 - Rekrutacja',
'projekt': '19902 - Launch Bydgoszcz, Toruń, ulotkowanie różne miasta - Uber Eats',
'etapProjektu': '11 - Listopad 2019',
'numerKonta': '19902-11-501-01-01',

'uwagi': '19902',
'dekretTresc': 'Flyering in new city Rzeszów PO371267',

'kontrahentNazwa1': 'UBER / Uber Poland Sp. z o.o.',
'kontrahentNazwa2': '',
'kontrahentNIP': '7010406919',
'kontrahentUlica': 'Inflancka 4',
'kontrahentNumerDomu': '',
'kontrahentKodPocztowy': '00-189',
'kontrahentMiasto': 'Warszawa',

'osobaKontaktowa': 'Łukasz Rysak',
'wystawca': 'Anna Miroszewska',

'plastnoscRachunekNrRachunku': '88105010251000002340483375',
'plastnoscRachunekNazwaBanku': 'ING 01 Główny',

'adresWysylkiDokumentu': '',
'anulowany': False,
'ostatni': False,
'dokumentPowiazany': -1,

"""

from __future__ import unicode_literals

import datetime
import re
import requests

from django.conf import settings
from django.db.models import Max

from bra.models import ApiSprzedaz
from fk.models import MagDok, MagWiersz, MagNumer

from bra.api.sprzedaz import xls
from bra.api.dokumenty import Dokumenty


class Sprzedaz(Dokumenty):
    """
    Import faktur przychodowych z API GDFIT (BBConnector) do rejestru sprzedaży FK.
    """

    def importuj_sprzedaz(self, od_daty, do_daty, kto):
        """
        Import faktur sprzedaży.
        """

        # Pobranie przychodów z danego okresu i posortowanie wg daty

        przychody= self.api_przychody(od_daty, do_daty)
        przychody= sorted(przychody, key= lambda x: x['dataWystawienia'])

        # Inicjalizacja informacji o imporcie

        self.imp= ApiSprzedaz.objects.create(
            firma= self.firma,
            od_daty= od_daty,
            do_daty= do_daty,
            kto= kto
        )

        # Przetwarzanie kolejnych pozycji z grupowaniem w dokumenty/faktury
                
        self.duplikaty= []
        pop_nag= 0
        
        for k in przychody: 
            
            k= self.api_json_decode(k)
            fak= None
            
            status= self.pominac_fakture(k)
            
            print(k)

            if status == 'duplikat':
                continue
            
            if status == 'import':
                print(k)
                
                id_nag= k['identyfikatorNaglowka']
                
                if id_nag != pop_nag:
                    # Nowa faktura
                    fak= self.naglowek_faktury(id_nag, k)
                    pop_nag= id_nag
    
                self.pozycja_faktury(fak, k)
            
            k['status']= status

            self.raport.append((k, fak))
    
        # Zapisanie ostatniego numeru
        
        self.zapisz_stan_numeracji()
        
        # Utworzenie i zapamiętanie raportu kontrolnego

        self.imp.xls= xls.raport_kontrolny(self.imp, self.raport)
        self.imp.save()


                    
    def naglowek_faktury(self, id_nag, k):
        """
        Utworzenie nowego nagłówka faktury sprzedaży.
        """
        
        fak= MagDok()
        
        # Zapamiętanie źródła danej faktury
        
        fak.numer_abs= id_nag
        
        self.ustal_sprzedawce(fak, k)
        self.zeruj_fak(fak)

        fak.nr_dok= k['numerDokumentu']
        if fak.nr_dok: fak.nr_dok= fak.nr_dok.upper()

        fak.data= datetime.datetime.strptime(k['dataWystawienia'][:10], '%Y-%m-%d') 
        fak.data_sp= datetime.datetime.strptime(k['dataWykonanieUslugiDostawy'][:10], '%Y-%m-%d')

        # Ustalenie daty podatku analogicznie jak w systemie FK

        data_sp7= fak.data_sp + datetime.timedelta(days= 7)
        if fak.data < data_sp7:
            fak.data_pod= fak.data
        else:
            fak.data_pod= data_sp7

        fak.rodz_te= 'PU'
        fak.numer= self.ustal_numer(fak.rodz_te, fak.data)
            
        fak.sp_zapl= k['metodaPlatnosci'][:1]    
        fak.dni_na_zapl= self.platnosci.get(k['idMetodyPlatnosci'], {}).get('liczbaDni', 0)
        fak.term_zapl= datetime.datetime.strptime(k['terminPlatnosci'][:10], '%Y-%m-%d') 

        fak.uwagi= k['dekretTresc']
        if fak.uwagi: 
            fak.uwagi= re.sub('\s+', ' ', fak.uwagi.upper().strip())

        fak.wystawil= 1
        fak.data_rej= datetime.date.today()

        fak.symbol= 'FV'
        fak.korekta= 'D'
        
#         fak.pz= self.imp.id
        
        fak.save(using= settings.DBS(self.baza))
        
        # Zapisanie statystyk importu

        if not self.imp.od_fak_id:
            self.imp.od_fak_id= fak.id
        self.imp.do_fak_id= fak.id
        self.imp.ile_faktur += 1

        return fak



    def pozycja_faktury(self, fak, k):
        """
        Utworzenie pozycji faktury sprzedaży
        """
        
        netto= k['dekretNetto']
        vat= k['dekretVat']
        brutto= k['dekretBrutto']

        fak.wart_bru += brutto
        
        fak.save(using= settings.DBS(self.baza))
        
        # Inicjalizacja wiersza faktury

        poz= MagWiersz(id_dok= fak)
        
        poz.il_dysp= - float(k['dekretIlosc'])
        poz.il_real= poz.il_dysp
        
        poz.cena_real= netto
        poz.cena_ewid= vat
        poz.wartosc= brutto

        poz.upust= 0
        poz.vat= self.ustal_stawke(netto, vat)
        poz.zaliczka= 0
        poz.znak='-'
        poz.jm= k['dekretJednostkaMiary'][:3]
        poz.konto= self.ustal_konto(k, poz.vat)
        poz.rodzaj= '01'
        
        poz.save(using= settings.DBS(self.baza))
        
        self.imp.ile_wierszy += 1



    def ustal_sprzedawce(self, fak, k):
        """
        Ustalenie kontrahenta / dostawcy faktury sprzedaży.
        Kontrahent może już istnieć w FK lub trzeba go utworzyć.
        """

        # Pobranie danych kontrahenta z API

        kon= self.daj_api_kon(k)

        # Odszukanie kontrahenta w FK lub utworzenie nowego

        kon= self.ustal_kon(kon)

        # Przepisanie danych kontrahenta do faktury
        
        fak.id_kli= kon
        fak.nip= kon.id
        


    def pominac_fakture(self, fak):
        """
        Sprawdzenie czy dana faktura powinna być pominięta w tym imporcie.
        """
        
        id_nag= fak['identyfikatorNaglowka']
        id_poz= fak['identyfikatorPozycji']

        # Eliminacja doplikatów pozycji
        
        id_dup= '{}-{}'.format(id_nag, id_poz)
        if id_dup in self.duplikaty:
            print('Pomijam - duplikat pozycji')
            return 'duplikat'


        self.duplikaty.append(id_dup)
        
        k= self.daj_api_kon(fak)
        fak['kon']= k  
        
        # Interesują nas tylko faktury VAT
        
        rodzaj= fak['rodzajDokumentu']
        print('Dokument', id_nag, id_poz, rodzaj)
        
        if rodzaj != 'Faktura':
            print('Pomijam - rodzaj faktury', rodzaj)
            self.imp.ile_nie_fa += 1
            return 'rodzaj'

        # Czy faktura jest już zaimportowana
        
        if self.juz_zaimportowane(id_nag):
            print('Pomijam - zaimportowana')
            self.imp.ile_lp_roz += 1
            return 'wczesniej'
        
        # Sprawdzenie czy podobna faktura jest już w rejestrze sprzedaży
        # na przykład wprowadzona ręcznie

        faktura= fak['numerDokumentu']
        if faktura: faktura= faktura.upper()
        
        d_wyst= datetime.datetime.strptime(fak['dataWystawienia'][:10], '%Y-%m-%d')
        
        nip= fak['kontrahentNIP']
        nip= re.sub('-', '', nip)

        # Sprawdzenie na podstawie NIP zapisanego w rejestrze sprzedaży, numeru faktury i daty

        if MagDok.objects.using(settings.DBS(self.baza)).filter(nr_dok= faktura, data= d_wyst, nip= nip, numer_abs__isnull= True).count() > 0:
            print('Pomijam - istnieje podobna', faktura, d_wyst, nip)
            self.imp.ile_podobne += 1
            return 'podobna'

        # Sprawdzenie na podstawie NIP zapisanego w rejestrze kontrahentów, numeru faktury i daty
                
        if MagDok.objects.using(settings.DBS(self.baza)).filter(nr_dok= faktura, data= d_wyst, id_kli__id= nip, numer_abs__isnull= True).count() > 0:
            print('Pomijam - istnieje podobna', faktura, d_wyst, nip)
            self.imp.ile_podobne += 1
            return 'podobna'
        
        return 'import'
    
    
    
    def ustal_numer(self, rodz_te, data):
        """
        Ustalenie numeru lp faktury w rejestrze.
        Numeracja jest w obrębie (miesiac, rodz_te)
        """
        
        # Sprawdzenie czy ostatni numeru nie jest już zbuforowany
        
        miesiac= '{:d}{:02d}'.format(data.year % 100, data.month)
        max_lp= self.numery.get((miesiac, rodz_te))
        
        if not max_lp:
            # Odczytanie maksymalnego numeru z bazy danych
            
            y= data.year
            m= data.month
            
            max_lp= MagDok.objects.using(settings.DBS(self.baza)).filter(data__year= y, data__month= m, rodz_te=rodz_te).aggregate(Max('numer'))
            
            if not max_lp or not max_lp['numer__max']:
                max_lp= 0
            else:
                max_lp= max_lp['numer__max']
        
        # Wyznaczenie następnego numeru
        
        max_lp += 1
        
        # Zapamiętanie aby nie czytać za każdym razem
        
        self.numery[(miesiac, rodz_te)]= max_lp
        
        return max_lp



    def ustal_stawke(self, netto, vat):
        """
        Ustalenie stawki VAT na podstawie kwoty VAT i netto.
        To nie zawsze jest poprawna wartość.
        """
        stawka= '{:02d}'.format(int(round(vat * 100 / netto, 0)))
        if stawka == '00':
            stawka= 'ZW'
        return stawka



    def ustal_konto(self, k, stawka):
        """
        Ustalenie numeru konta 550 lub 501 na podstawie danych źródłowych.
        """
        projekt= k['projekt']
        konto= None
        
        try:
            konto= "7021" + projekt[1:5] + "01" + stawka
        except:
            konto= None
            
        k['fk_konto']= konto
        return konto


        
    def juz_zaimportowane(self, id_nag):
        """
        Sprawdzenie czy dany dokument przychodowy API został już zaimportowany.
        """
        return MagDok.objects.using(settings.DBS(self.baza)).filter(numer_abs= id_nag).count() > 0;



    def zapisz_stan_numeracji(self):
        """
        Zapisanie stanu numeracji dokumentów (następnego numeru) w mag_numer
        """
        for ((miesiac, dzial), numer) in self.numery.items():
            MagNumer.ostatni(self.baza, dzial, 'FR', 'D', miesiac, numer+1)



    def api_przychody(self, od_daty, do_daty):
        """
        Pobranie dokumentów przychodowych z BBConnector API.
        """
        print('Pobieranie dokumentów przychodowych')

        response = requests.get(
            self.firma.api_url+'/Przychody/',
            params= {
                'dataod': od_daty,
                'datado': do_daty
            },
            headers= self.HEADERS,
            timeout= 30
        )

        print('Odpowiedz', response.status_code)
        print('RESP', response)
        print('JSON', response.json())

        return response.json()



    def zeruj_fak(self, fak):
        """
        Wyzerowanie pól kwotowych w nagłówku faktury.
        """
        fak.upust_sp= 0
        fak.upust_gt= 0
        fak.wart_det= 0
        fak.wart_bru= 0
        fak.zaplata= 0
        fak.zaplacone= 0

