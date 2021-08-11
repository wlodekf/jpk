# -*- coding: utf-8 -*-

"""
Informacje w dokumencie kosztowym
------------------------------------------------------
'identyFikatorNaglowka': 35518,
'identyfikatorPozycji': 69827,
'idKontrahenta': 1643,
'idRodzajDokumentuKosztowego': 4,
'idWystawcy': -1,
'idMetodyPlatnosci': 4,
'idBeneficjenta': -1,

'numerDokumentuZewnetrznego': '1912/SM/0027',
'wartoscNetto': 32000.0,
'wartoscVAT': 7360.0,
'wartoscBrutto': 39360.0,

'pelnaNazwaBeneficjenta': None, 
'dataWyciaguBankowego': '1900-01-01T00:00:00', 
'dekretWartoscNetto': 32000.0, 
'kontrahentMiasto': 'Warszawa', 
'pozostalaKwota': 0.0, 
'kwotaDoBanku': 0.0, 
'dataKsiegowosc': '2020-01-23T00:00:00', 
'wystawca': None, 
'kwotaDoZaplaty': 39360.0, 
'kontrahentUlica': 'gen. K.S. Rudnickiego 1/U2', 
'kontrahentNumerDomu': '', 

'grupaSyntetyczna': '550-Koszty stałe',
'syntetyka': '550-4-Reklama i Marketing',
'analityka': '550-4-5-Koszty New Business',
'numerKonta': '88105010251000002340483375', 
'projekt': '19002-BTL Materiały POS'
'etapProjektu': '11-Listopad 2019', 

'rodzajDokumentuKosztowegoNazwaSkrocona': 'FA', 
'rodzajDokumentuKosztowegoNazwaPelna': 'Faktura VAT zewnętrzna/obca',

'wartoscKilometrowki': 0.0, 
'statusWystawcy': -1, 
'nazwaWlascicielaRachunku': 'SG Marketing Sp. z o.o. ', 
'dekretWartoscVat': 7360.0, 
'dekretWartoscBrutto': 39360.0, 
'dataDokumentuZewnetrznego': '2019-12-31T00:00:00', 
'beneficjentImie': None, 

'dataPaczkiBanku': '1900-01-01T00:00:00', 
'kontrahentKodPocztowy': '01 – 858', 
'uwagi': '', 
'numerDokumentu': '1879', 

'opis': '1912/SM/0027', 
'kontrahentNazwa2': '', 
'dataEwidencji': '2020-01-21T00:00:00', 
'beneficjentNazwisko': None, 
'nazwaBanku': 'ING 01 Główny', 
'kontrahentNazwa1': 'San Markos / San Markos Sp. z o.o.',

"""

from __future__ import unicode_literals

import datetime
import re
import requests

from django.conf import settings
from django.db.models import Max

from fk.models import Zak, ZakPoz, ZakKos, DefNum

from bra.models import ImportZakupow

from bra.api.zakupy import xls
from bra.api.dokumenty import Dokumenty


class Zakupy(Dokumenty):
    """
    Import faktur zakupowych z API GDFIT (BBConnector) do FK.
    """

    def importuj_zakupy(self, od_daty, do_daty, kto):
        """
        Import faktur zakupowych.
        """

        print('Pobieranie dokumentów kosztowych')

        response = requests.get(
            self.firma.api_url+'/Koszty/',
            params= {
                'dataod': od_daty,
                'datado': do_daty
            },
            headers= self.HEADERS,
            timeout= 30
        )

        print('Odpowiedz', response.status_code)
        
        self.duplikaty= []
        pop_nag= 0
    
        self.imp= ImportZakupow.objects.create(
            firma= self.firma,
            od_daty= od_daty,
            do_daty= do_daty,
            kto= kto
        )
            
        for k in sorted(response.json(), key= lambda x: x['dataDokumentuZewnetrznego']):
            
            k= self.api_json_decode(k)
            k['platnosc']= self.platnosci.get(k['idMetodyPlatnosci'], {}).get('nazwaSkrocona', '')
            zak= None
            
            status= self.pominac_fakture(k)
            
            if status == 'duplikat':
                continue
            
            if status == 'import':
                print(k)
                
                id_nag= k['identyFikatorNaglowka']
                
                if id_nag != pop_nag:
                    # Nowa faktura
                    zak= self.naglowek_faktury(id_nag, k)
                    pop_nag= id_nag
    
                self.pozycja_faktury(zak, k)
            
            k['status']= status

            self.raport.append((k, zak))
    
        self.zapisz_stan_numeracji()

        self.imp.xls= xls.raport_kontrolny(self.imp, self.raport)
        self.imp.save()



    def naglowek_faktury(self, id_nag, k):
        """
        Utworzenie nowego nagłówka faktury zakupu.
        """
        
        # Mapowanie danych z API do FK

        zak= Zak()
        
        # Zapamiętanie źródła danej faktury
        
        zak.lp_roz= id_nag
        
        self.ustal_dostawce(zak, k)
        self.zeruj_zak(zak)
        
        zak.faktura= k['numerDokumentuZewnetrznego']
        if zak.faktura: zak.faktura= zak.faktura.upper()

        zak.rodzaj= 'AG' if k['idMetodyPlatnosci'] == 1 else 'AF'
        
        zak.d_zak= datetime.datetime.strptime(k['dataDokumentuZewnetrznego'][:10], '%Y-%m-%d') 
        zak.d_wyst= zak.d_zak
        zak.d_otrzym= zak.d_zak

        zak.msc_fak= '{:04d}/{:02d}'.format(zak.d_zak.year, zak.d_zak.month)
        
        # Miesiąc rozliczenia VAT
        
        zak.msc_roz= '{:04d}/{:02d}'.format(zak.d_zak.year, zak.d_zak.month)
        
        zak.lp= self.ustal_lp(zak.msc_fak, zak.rodzaj)
                
        zak.l_dni= self.platnosci.get(k['idMetodyPlatnosci'], {}).get('liczbaDni', 0)
        zak.termin= zak.d_zak + datetime.timedelta(days= zak.l_dni)

        zak.uwagi= k['uwagi']
        if zak.uwagi: 
            zak.uwagi= re.sub('\s+', ' ', zak.uwagi.upper().strip())

        zak.kto_rej= 1
        zak.d_rej= datetime.date.today()
        zak.kto= 1
        zak.kiedy= datetime.date.today()

        zak.symbol= 'FV'
        zak.korekta= 'D'
        zak.pz= self.imp.id
        
        zak.save(using= settings.DBS(self.baza))
        
        # Zapisanie statystyk importu

        if not self.imp.od_zak_id:
            self.imp.od_zak_id= zak.zak_id
        self.imp.do_zak_id= zak.zak_id
        self.imp.ile_faktur += 1
        
        return zak


        
    def pozycja_faktury(self, zak, k):
        """
        Utworzenie pozycji faktury
        """
        
        netto= k['wartoscNetto']
        vat= k['wartoscVAT']
        brutto= k['wartoscBrutto']

        zak.netto += netto 
        zak.vat += vat
        zak.brutto += brutto
        
        zak.save(using= settings.DBS(self.baza))

        
        poz= ZakPoz(zak= zak)
        
        poz.p_netto= netto
        poz.p_vat= vat
        poz.p_brutto= brutto
        poz.p_stawka= self.ustal_stawke(netto, vat)
        poz.p_roz= 'OP'
        poz.konto= self.ustal_konto(k)
        poz.zlecenie= self.ustal_zlecenie(k)
        
        poz.save(using= settings.DBS(self.baza))

        
        kos= ZakKos(zak= zak, poz= poz)
        kos.kwota= poz.p_netto
        kos.konto= poz.konto
        kos.zlecenie= poz.zlecenie
        kos.konto5= poz.konto5

        kos.save(using= settings.DBS(self.baza))


        self.imp.ile_wierszy += 1


        
    def ustal_dostawce(self, zak, k):
        """
        Ustalenie kontrahenta / dostawcy faktury zakupu.
        Kontrahent może już istnieć w FK lub trzeba go utworzyć.
        """

        # Pobranie danych kontrahenta z API

        kon= self.daj_api_kon(k)

        # Odszukanie kontrahenta w FK lub utworzenie nowego

        kon= self.ustal_kon(kon)

        # Przepisanie danych kontrahenta do faktury
           
        zak.dostawca= kon 
        zak.nip= kon.id
        zak.d_nazwa= kon.nazwa



    def pominac_fakture(self, fak):
        """
        Sprawdzenie czy dana faktura powinna być pominięta w tym imporcie.
        """

        k= self.daj_api_kon(fak)
        fak['kon']= k
        
        id_nag= fak['identyFikatorNaglowka']
        id_poz= fak['identyfikatorPozycji']

        # Eliminacja doplikatów pozycji
        
        id_dup= '{}-{}'.format(id_nag, id_poz)
        if id_dup in self.duplikaty:
            print('Pomijam - duplikat pozycji')
            return 'duplikat'

        self.duplikaty.append(id_dup)
        
        # Interesują nas tylko faktury VAT
        
        rodzaj= fak['rodzajDokumentuKosztowegoNazwaSkrocona']
        print('RODZAJ', id_nag, id_poz, rodzaj)
        
        if rodzaj != 'FA':
            print('Pomijam - rodzaj faktury', rodzaj)
            self.imp.ile_nie_fa += 1
            return 'rodzaj'

        # Czy faktura jest już zaimportowana (zak.lp_roz)
        
        if self.juz_zaimportowane(id_nag):
            print('Pomijam - zaimportowana lp_roz')
            self.imp.ile_lp_roz += 1
            return 'wczesniej'
        
        # Sprawdzenie czy podobna faktura jest już w rejestrze zakupów
        # na przykład wprowadzona ręcznie

        faktura= fak['numerDokumentuZewnetrznego']
        if faktura: faktura= faktura.upper()
        
        d_wyst= datetime.datetime.strptime(fak['dataDokumentuZewnetrznego'][:10], '%Y-%m-%d')
        
        nip= k['nip']
        nip= re.sub('-', '', nip)

        if Zak.objects.using(settings.DBS(self.baza)).filter(faktura= faktura, d_wyst= d_wyst, nip= nip, lp_roz__isnull= True).count() > 0:
            print('Pomijam - istnieje podobna', faktura, d_wyst, nip)
            self.imp.ile_podobne += 1
            return 'podobna'
            
        return 'import'



    def ustal_lp(self, msc_fak, rodzaj):
        """
        Ustalenie numeru lp faktury w rejestrze.
        Numeracja jest w obrębie (msc_fak, rodzaj)
        """
        
        # Sprawdzenie czy ostatni numeru nie jest już zbuforowany
        
        max_lp= self.numery.get((msc_fak, rodzaj))
        
        if not max_lp:
            
            # Odczytanie maksymalnego numeru z bazy danych
            
            max_lp= Zak.objects.using(settings.DBS(self.baza)).filter(msc_fak= msc_fak, rodzaj=rodzaj).aggregate(Max('lp'))
            
            if not max_lp or not max_lp['lp__max']:
                max_lp= 0
            else:
                max_lp= max_lp['lp__max']
        
        # Wyznaczenie następnego numeru
        
        max_lp += 1
        
        # Zapamiętanie aby nie czytać za każdym razem
        
        self.numery[(msc_fak, rodzaj)]= max_lp
        
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



    def ustal_konto(self, k):
        """
        Ustalenie numeru konta 550 lub 501 na podstawie danych źródłowych.
        """
        analityka= k['analityka']
        projekt= k['projekt']
        konto= None
         
        try:
            if analityka[:3] == '550':
                konto= '55010'+analityka[4]+'0'+analityka[6]
            elif projekt and analityka:
                konto= '501'+projekt[:5]+'0'+analityka[:3]
        except:
            konto= None
            
        k['fk_konto']= konto
        return konto



    def ustal_zlecenie(self, k):
        """
        Ustalenie numeru zlecenia.
        """
        
        zlecenie= k['numerDokumentu']

        try:
            if not zlecenie:
                projekt= k['projekt']
                zlecenie= projekt[1:5]
        except:
            zlecenie= None

        k['fk_zlecenie']= zlecenie
        return zlecenie
     

        
    def juz_zaimportowane(self, id_nag):
        """
        Sprawdzenie czy dana pozycja kosztów API została już zaimportowana.
        """
        return Zak.objects.using(settings.DBS(self.baza)).filter(lp_roz= id_nag).count() > 0;
        
            

    def zapisz_stan_numeracji(self):
        """
        Zapisanie stanu numeracji dokumentów (następnego numeru) w mag_numer
        """
        for ((miesiac, rodzaj), numer) in self.numery.items():
            DefNum.ostatni(self.baza, 'ZAK', 'NR', rodzaj, 'D', miesiac, numer)



    def zeruj_zak(self, zak):
        """
        Zainicjalizowanie / wyzerowanie kwot w fakturze zakupu.
        """

        zak.brutto= 0
        zak.netto= 0
        zak.vat= 0
             
        zak.zakup= 0
        zak.clo= 0
        zak.pimport= 0
        zak.akcyza= 0
        zak.manip= 0
        zak.sop_i_net= 0
        zak.sop_i_vat= 0
        zak.sop_p_net= 0
        zak.sop_p_vat= 0
        zak.kos_w_net= 0
        zak.kos_w_vat= 0
        zak.soz_i_net= 0
        zak.soz_i_vat= 0
        zak.soz_p_net= 0
        zak.soz_p_vat= 0
        zak.bez_i_net= 0
        zak.bez_i_vat= 0
        zak.bez_p_net= 0
        zak.bez_p_vat= 0
