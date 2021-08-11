# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from fk.models import MagDok, MagWiersz, Spo
from app.utils import grosze, stawka
from app import ctrl
from app.templatetags import utils

import decimal
import re


class Faktura(ctrl.CtrlTabeli):
    """
    Kontrola sprzedaży VAT.
    """
    
    def __init__(self, jpk):
        super(Faktura, self).__init__(jpk)
        
        self.elementy= [
                        MagDok.objects.select_related('id_kli').using(jpk.fkdbs('Faktura.MagDok')).filter(data__gte= jpk.dataod, data__lte= jpk.datado, symbol__in=('FV','RU','FW'), stat='D', dr_fisk__isnull= True).order_by('id'),
                       ]
        self.tabela= 'faktura'
            
    def sumuj(self, i, element):
        self.suma1 += element.brutto


    def uwzglednij(self, i, fak):
        """
        Faktury sprzedaży
        """
        
        fak.czy_wewnetrzna= (fak.symbol == 'FW')
        fak.czy_odwrotne= 'false'
        fak.rodzaj_faktury= 'VAT'
        
        if fak.korekta == 'K':
            fak.rodzaj_faktury= 'KOREKTA'
            fak.przyczyna_korekty= fak.podstawa_korekty()
            
            try:
                fak.nr_korygowanej= fak.korygowana.nr_fak() 
                fak.okres_korygowanej= fak.korygowana.data
            except MagDok.DoesNotExist:
                fak.jpk.blad('Faktura', fak.nr_fak(), 'Nie znaleziono faktury korygowanej')
                fak.nr_korygowanej= ''
                fak.okres_korygowanej= ''
            
        # Czytamy wszystkie pozycje i liczymy podsumowanie faktury wg stawek VAT
        # tak samo jak na wydruku faktury
        
        fak.zal_zaplata= decimal.Decimal(0)
        fak.zal_podatek= decimal.Decimal(0)
        
        # Zaliczka z wartości brutto wszystkich pozycji faktury
        # Dla przypadku gdy faktura jest zaznaczona jako zaliczkowa ale nie 
        # podano wartości zaliczki w pozycjach faktury,
        # wtedy cała faktura traktowana jest jako zaliczkowa
        zal_zaplata= decimal.Decimal(0)
        zal_podatek= decimal.Decimal(0)
        zal_wiersze= False
        
        podsum= {}
        for w in fak.wiersze.all():
            w.wartosc_wiersza(fak)
            
            w_vat= w.vat # do grupowania w podsumowaniu stawkami
            
            if w.vat == '22%': w_vat= '23%'
            if w.vat == ' 7%': w_vat= ' 8%'
            if w.vat == ' 3%': w_vat= ' 5%'
            
            if fak.oo(w): w_vat= 'OO.'
            if fak.np(w): w_vat= 'NP.'
                
            # Pozostałe stawki na 0%
            if not w_vat in ('23%', ' 8%', ' 5%', ' 0%', 'ZW.', 'OO.', 'NP.'):
                w_vat= ' 0%'
                
            st= podsum.get(w_vat)
            if not st:
                podsum[w_vat]= [w.p_netto, w.p_vat, w.p_brutto]
            else:
                st[0] += w.p_netto
                st[1] += w.p_vat
                st[2] += w.p_brutto

            if fak.ciagla == 'T': # faktura zaliczkowa            
                zal_zaplata += w.p_brutto
                zal_podatek += grosze(w.p_brutto * stawka(w.vat) / (decimal.Decimal(100)+stawka(w.vat)))
                                        
                if w.zaliczka and w.zaliczka != 0.0:
                    zal_wiersze= True
                    fak.zal_zaplata += w.zaliczka
                    fak.zal_podatek += grosze(w.zaliczka * stawka(w.vat) / (decimal.Decimal(100)+stawka(w.vat)))


        if fak.ciagla == 'T': # faktura zaliczkowa
            fak.rodzaj_faktury= 'ZAL'
            if not zal_wiersze:
                # Cała faktura jako zaliczkowa 
                fak.zal_zaplata= zal_zaplata
                fak.zal_podatek= zal_podatek
            
        zera= [decimal.Decimal(0.0) for i in range(3)]    
        
        fak.netto23= podsum.get('23%', zera)[0]
        fak.vat23= podsum.get('23%', zera)[1]
        
        fak.netto8= podsum.get(' 8%', zera)[0]
        fak.vat8= podsum.get(' 8%', zera)[1]        
        
        fak.netto5= podsum.get(' 5%', zera)[0]
        fak.vat5= podsum.get(' 5%', zera)[1]

        fak.netto_oo= podsum.get('OO.', zera)[0]
        fak.vat_oo= podsum.get('OO.', zera)[1]
        
        fak.netto_np= podsum.get('NP.', zera)[0] 
        fak.vat_np= podsum.get('NP.', zera)[1]
                
        fak.netto0= podsum.get(' 0%', zera)[0]
        fak.nettoZW= podsum.get('ZW.', zera)[0]
           
        if fak.waluta:
            
            # Zapisanie wartości w złotych do wykazanie w polach *_W
            
            fak.vat23_zl= fak.vat23
            fak.vat8_zl= fak.vat8
            fak.vat5_zl= fak.vat5
            fak.vat_oo_zl= fak.vat_oo
            
            # Przeliczenie kwot w zł na kwoty w walucie
            
            fak.netto23= fak.na_walute(fak.netto23)
            fak.vat23= fak.na_walute(fak.vat23)
            
            fak.netto8= fak.na_walute(fak.netto8)
            fak.vat8= fak.na_walute(fak.vat8)
            
            fak.netto5= fak.na_walute(fak.netto5)
            fak.vat5= fak.na_walute(fak.vat5)
    
            fak.netto_oo= fak.na_walute(fak.netto_oo)
            fak.vat_oo= fak.na_walute(fak.vat_oo)
            
            fak.netto_np= fak.na_walute(fak.netto_np) 
            fak.vat_np= fak.na_walute(fak.vat_np)
                
            fak.netto0= fak.na_walute(fak.netto0)
            fak.nettoZW= fak.na_walute(fak.nettoZW)
            
            if fak.kurs and fak.w_walucie: 
                fak.wart_bru= fak.w_walucie 

        # Do sumy kontrolnej w ctrl (sumowanie kwot w różnych walutach)
        fak.brutto= fak.wart_bru
      
        fak.p16= fak.p17= fak.p18= fak.p19= fak.p20= fak.p21= fak.p22= fak.p23= 'false'
        fak.p18a= 'false'
        
        for rodzaj in re.findall('[A-Z]\d*', fak.rodzaj or ''):
            lit= rodzaj[0]
            par= rodzaj[1:]
            if lit == 'K':
                fak.p16= 'true'
            if lit == 'S':
                fak.p17= 'true'
            if lit == 'O':
                fak.p18= 'true'
            if lit == 'Z':
                fak.p19= 'true'
                fak.p19a= Spo.nazwa_pozycji('SPPOD', par, self.jpk)
            if lit == 'E': 
                fak.p20= 'true'
            if lit == 'I':
                fak.p21= 'true'
            if lit == 'T':
                fak.p23= 'true'
         
        fak.adres_kon= fak.id_kli.adres_kon(jpk= fak.jpk)
        
        if not fak.data:
            fak.jpk.blad('Faktura', fak.nr_fak(), 'Brak daty wystawienia faktury')
        if not fak.nr_fak():
            fak.jpk.blad('Faktura', fak.id, 'Brak numeru faktury')
        if not fak.id_kli.nazwa_kon() or len(fak.id_kli.nazwa_kon())==0:
            fak.jpk.blad('Faktura', fak.nr_fak(), 'Brak nazwy nabywcy')
        if not fak.adres_kon or len(fak.adres_kon)==0:
            fak.jpk.blad('Faktura', fak.nr_fak(), 'Brak adresu nabywcy')  
        if fak.korekta == 'K':
            if not fak.przyczyna_korekty or len(fak.przyczyna_korekty.strip())==0:
                fak.jpk.blad('Faktura', fak.nr_fak(), 'Nieznana przyczyna korekty faktury')              
            if not fak.nr_korygowanej or len(fak.nr_korygowanej.strip())==0:
                fak.jpk.blad('Faktura', fak.nr_fak(), 'Nieznany numer faktury korygowanej') 
            if not fak.okres_korygowanej:
                fak.jpk.blad('Faktura', fak.nr_fak(), 'Nieznany okres faktury korygowanej') 
                                                        
        return True


class Wiersz(ctrl.CtrlTabeli):
    """
    Kontrola sprzedaży VAT.
    """
    
    def __init__(self, jpk):
        super(Wiersz, self).__init__(jpk)
        
        self.elementy= [
                        MagWiersz.objects.select_related('id_dok__id_kli').using(jpk.fkdbs('Wiersz.MagWiersz')).filter(id_dok__data__gte= jpk.dataod, id_dok__data__lte= jpk.datado, id_dok__symbol__in=('FV','RU','FW'), id_dok__stat='D', id_dok__dr_fisk__isnull= True).order_by('id_dok__id', 'id'),
                       ]
        self.tabela= 'faktura_wiersz'
            
    def sumuj(self, i, element):
        self.suma1 += element.netto

    def uwzglednij(self, i, w):
        """
        Faktury sprzedaży
        """
        w.wartosc_wiersza(w.id_dok)
        w.daj_opi()
        
        w.nazwa= ' '.join(x.strip() for x in w.opia)
        w.nazwa= re.sub('\s+', ' ', w.nazwa)
        
        if w.wsk_wyc == 'B':
            w.cena_bru= w.c_bru
            w.brutto= w.p_brutto
        else:
            w.cena_net= w.c_net
        
        w.netto= w.p_netto
        
        fak= w.id_dok
        if fak.waluta:
            if w.wsk_wyc == 'B':
                w.cena_bru= fak.na_walute(w.cena_bru)
                w.brutto= fak.na_walute(w.brutto)
            else:
                w.cena_net= fak.na_walute(w.cena_net)
                w.p_netto= fak.na_walute(w.p_netto)
            w.netto= fak.na_walute(w.netto)

        nr_fak= w.id_dok.nr_fak()
        
        if not nr_fak or len(nr_fak)==0:
            w.jpk.blad('Wiersz', w.id_dok, 'Brak numer faktury') 
        if not w.nazwa or len(w.nazwa)==0:
            w.jpk.blad('Wiersz', nr_fak, 'Brak nazwy (rodzaju) towaru lub usługi') 
        if not w.jm or len(w.jm)==0:
            w.jm= 'jdn'
        if w.il_real is None:
            w.jpk.blad('Wiersz', nr_fak, 'Brak ilości (liczby) dostarczonych towarów lub zakresu wykonanych usług') 
        if not w.jm or len(w.jm)==0:
            w.jpk.blad('Wiersz', nr_fak, 'Brak jednostki miary') 

        st_vat= utils.stawka(w.vat)
        if st_vat and not st_vat in ('23', '22', '8', '7', '5', '4', '3', '0', 'zw', 'oo', 'np'):
            w.jpk.blad('Wiersz', nr_fak, 'Niepoprawna stawka VAT ({}/{})'.format(w.vat, st_vat)) 
                                                                                         
        return True
