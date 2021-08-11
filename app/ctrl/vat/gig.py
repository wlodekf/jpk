# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from fk.models import MagDok, Zak, SrtVat, SysPar
from app.utils import procent
from app import ctrl

from .vat import SprzedazVAT, SprzedazVATPozycjeFak, ZakupVAT, ZakupVATPozycjeZak
from .. import Pozycje

import datetime
import decimal
import itertools
import re
from django.conf import settings

import logging
logger= logging.getLogger(__name__)



class SprzedazGIG(SprzedazVAT):
    """
    Część dotyczyąca podatku należnego do deklaracji w GIG tworzona jest 
    na podstawie zapisów z rejestru sprzedaży i zakupów.
    """
    
    def __init__(self, jpk):
        super(SprzedazGIG, self).__init__(jpk)
        
        self.elementy= [
                        SprzedazGIGPozycjeFak(jpk),
                        SprzedazGIGPozycjeZak(jpk)
                       ]


class SprzedazGIGPozycjeFak(SprzedazVATPozycjeFak):
    
    def __init__(self, jpk):
        super(SprzedazGIGPozycjeFak, self).__init__(
            MagDok.objects.select_related('id_kli').using(jpk.fkdbs('Sprzedaz.MagDok')).filter(
                data_pod__gte= jpk.dataod, 
                data_pod__lte= jpk.datado, 
                symbol__in=('FV','RU','FW','ZD'), 
                stat='D', 
                dr_fisk__isnull= True).order_by('id')
        )


    def uwzglednij(self, fak):
        """
        Podatek należny z rejestru sprzedaży GIG.
        fak.podsum zawiera podsumowanie pozycji stawkami VAT.
        """

        super(SprzedazGIGPozycjeFak, self).przygotuj(fak)
        
        fak.pod_rejestr= fak.symbol
             
        for stawka in fak.podsum.keys():
            netto= fak.podsum[stawka][0]
            vat= fak.podsum[stawka][1]

            if netto is None or vat is None: # pragma: no cover
                # Nie za bardzo wiadomo w jakich okolicznościach taki przypadek mógłby się pojawić
                fak.jpk.blad('SPR', fak.nr_dokumentu, 'Nieokreślona wartość netto lub podatku należnego')

            fak.podatek_nalezny += vat
            
            if stawka == 'ZW.':
                fak.k_10= netto
            elif stawka == 'NO.':
                fak.k_11= netto
                if fak.id_kli.nipue(): fak.k_12= netto
            elif stawka == ' 0%' or stawka == 'K0%':
                fak.k_13= netto
            elif stawka in (' 5%', ' 3%'):
                fak.k_15 += netto
                fak.k_16 += vat
            elif stawka in (' 8%', ' 7%'):
                fak.k_17 += netto
                fak.k_18 += vat
            elif stawka in ('23%', '22%'):
                fak.k_19 += netto
                fak.k_20 += vat
            elif stawka == 'W0%':
                fak.k_21= netto
            elif stawka == 'E0%':
                fak.k_22= netto
            elif stawka == 'OO.':
                fak.k_31= netto
            else:
                fak.jpk.blad('SPR', fak.nr_dokumentu, 'Stawka VAT {} niezakwalifikowana do żadnego pola deklaracji'.format(stawka))                

        self.sprawdzenie_nip_sprzedazy(fak)

        return True


        
class SprzedazGIGPozycjeZak(Pozycje):
    
    def __init__(self, jpk):
        super(SprzedazGIGPozycjeZak, self).__init__(
            Zak.objects.select_related('dostawca').using(jpk.fkdbs('Sprzedaz.Zak')).filter(
                d_ksieg__gte= jpk.dataod, 
                d_ksieg__lte= jpk.datado, 
                rodzaj__in= ('WNT', 'IU', 'PN', 'OO'))
        )
        
         
    def uwzglednij(self, zak):
        """
        Podatek należny ewidencjonowany w rejestrze zakupów 
        (importy, odwrotne obciążenie, podatnikiem jest nabywca). 
        """
        
        zak.data_sprzedazy= zak.d_zak
        zak.nip_kon= zak.nr_id()
            
        zak.nr_dokumentu= zak.faktura
        if not zak.nr_dokumentu:
            zak.jpk.blad('SPR/ZAK', zak.zak_id, 'Nieokreślony numer dokumentu/faktury zakupu')
        
        zak.data_wystawienia= zak.d_wyst
        if not zak.data_wystawienia:
            zak.jpk.blad('SPR/ZAK', zak.nr_dokumentu, 'Nieokreślona data wystawienia faktury zakupu')
            
        zak.pod_rejestr= zak.rodzaj
        
        zak.podatek_nalezny += zak.vat
        if zak.netto is None or zak.vat is None: # pragma: no cover
            zak.jpk.blad('SPR/ZAK', zak.nr_dokumentu, 'Nieokreślona wartość netto lub podatku VAT faktury zakupu')        
                
        if zak.dostawca.not_nipue():
            zak.jpk.blad('SPR/ZAK', zak.nr_dokumentu, 'NIP kontrahenta ({}) wygląda na NIPUE ale nie jest tak oznaczony'.format(zak.dostawca.nr_kon.strip()))   
                        
        zak.rodzaj= zak.rodzaj.strip()
        if zak.rodzaj == 'WNT':
            zak.k_23, zak.k_24= zak.netto, zak.vat
        elif zak.rodzaj == 'IU' and not zak.dostawca.nipue():
            zak.k_27, zak.k_28= zak.netto, zak.vat
        elif zak.rodzaj == 'IU' and zak.dostawca.nipue():
            zak.k_29, zak.k_30= zak.netto, zak.vat
        elif zak.rodzaj == 'PN':
            if zak.jpk.wariant >= '4':
                zak.k_31, zak.k_32= zak.netto, zak.vat
            else:
                zak.k_32, zak.k_33= zak.netto, zak.vat
        elif zak.rodzaj == 'OO':
            if zak.jpk.wariant >= '4':
                pass
            else:
                zak.k_34, zak.k_35= zak.netto, zak.vat
        else: # pragma: no cover
            # Filtr uniemożliwia istnienie takich przypadków
            zak.jpk.blad('SPR/ZAK', zak.nr_dokumentu, 'Nieznany rodzaj zakupów')            
                                
        return True
    

    
class ZakupGIG(ZakupVAT):
    """
    Kontrola zakupu VAT.
    """
    
    def __init__(self, jpk):
        super(ZakupGIG, self).__init__(jpk)
        
        self.elementy= [
                        # Faktury zakupu z okresu pliku JPK z bieżącej bazy 
                        ZakupGIGPozycjeZak(self, 
                            Zak.objects.select_related('dostawca').prefetch_related('wiersze').using(jpk.fkdbs('Zakup.Zak')).
                                filter(d_ksieg__gte= jpk.dataod,
                                       d_ksieg__lte= jpk.datado).
                                order_by('zak_id')),
                        
                        # Faktury zakupu z okresu pliku JPK z poprzedniej bazy (starego roku) ale wykazywane w bieżącym roku
                        ZakupGIGPozycjeZak(self,
                            Zak.objects.select_related('dostawca').prefetch_related('wiersze').using(jpk.fkdbs_1('Zakup.Zak_1')).
                                filter(d_ksieg__gte= jpk.dataod, 
                                       d_ksieg__lte= jpk.datado, 
                                       msc_roz__lt= jpk.rok_01()).
                                order_by('zak_id'))
                       ]
        
        # Korekty VAT majątku trwałego i pozostałych zakupów liczonych prewspółczynnikiem 
        # dołączane są tylko dla pierwszej deklaracji czyli JPK od 1 stycznia
        
        if jpk.dataod.month == 1 and jpk.dataod.day == 1:
            
            self.elementy.append((ZakupGIGPozycjeMkvLacznie if settings.KOREKTA_VAT_LACZNIE else ZakupGIGPozycjeMkv)(jpk))
            
            if self.pre_wsp[0] != self.pop_wsp[0] or self.pre_wsp[1] != self.pop_wsp[1]:
                # Jeżeli zmienił się któryś z prewspółczynników
                
                dataod= datetime.date(jpk.dataod.year-1, 1, 1)
                datado= datetime.date(jpk.dataod.year-1, 12, 31)
                
                logger.info('PRE daty: {} - {}'.format(dataod, datado))
                
                self.elementy.append((ZakupGIGPozycjePreLacznie if settings.KOREKTA_VAT_LACZNIE else ZakupGIGPozycjePre)(self, itertools.chain( # union
                                        # Faktury zakupu z okresu pliku JPK z bieżącej bazy 
                                        Zak.objects.select_related('dostawca').prefetch_related('wiersze').using(jpk.fkdbs('pre/Zakup.Zak', dataod= dataod))
                                            .filter(d_ksieg__gte= dataod,
                                                    d_ksieg__lte= datado)
                                            .order_by('zak_id'),
                
                                        # Faktury zakupu z okresu pliku JPK z poprzedniej bazy (starego roku) 
                                        # ale wykazywane w bieżącym roku
                                        Zak.objects.select_related('dostawca').prefetch_related('wiersze').using(jpk.fkdbs_1('pre/Zakup.Zak_1', dataod= dataod))
                                            .filter(d_ksieg__gte= dataod, 
                                                    d_ksieg__lte= datado, 
                                                    msc_roz__lt= jpk.rok_01(dataod= dataod))
                                            .order_by('zak_id')
                                    )))
            
        

class ZakupGIGPozycjeZak(ZakupVATPozycjeZak):

    def __init__(self, ctrl, *args, **kwargs):
        super(ZakupGIGPozycjeZak, self).__init__(*args, **kwargs)
        self.ctrl= ctrl
        
    def uwzglednij(self, zak):
        
        wsp= self.ctrl.pre_wsp
        
        # Sprawdzenie poprawności i ustalenie podstawowych danych
        super(ZakupGIGPozycjeZak, self).przygotuj(zak)
        
        pozycje= False
        for w in zak.wiersze.all():
            pozycje= True
            if w.zrv == 'BEZ': continue
              
            if w.ip == 'I':
                zak.k_43 += procent(w.netto, w.odlicz)
                zak.k_44 += procent(w.vat, w.odlicz)
            else:
                print(zak.zak_id, zak.faktura, w.netto, w.odlicz)
                zak.k_45 += procent(w.netto, w.odlicz)
                zak.k_46 += procent(w.vat, w.odlicz)
        
        if not pozycje:
            zak.k_43= zak.sop_i_net + procent(zak.soz_i_net, wsp[0]) + procent(zak.kos_i_net, wsp[1])
            zak.k_44= zak.sop_i_vat + procent(zak.soz_i_vat, wsp[0]) + procent(zak.kos_i_vat, wsp[1])
            
            zak.k_45= zak.sop_p_net + procent(zak.soz_p_net, wsp[0]) + procent(zak.kos_w_net, wsp[1])
            zak.k_46= zak.sop_p_vat + procent(zak.soz_p_vat, wsp[0]) + procent(zak.kos_w_vat, wsp[1])
            
        zak.podatek_naliczony= zak.k_44 + zak.k_46
        
        zerowy= True
        for k in range(43, 51):
            if getattr(zak, 'k_{}'.format(k)) != decimal.Decimal(0.00):
                zerowy= False
                break
                    
        self.ctrl.vat_rozliczony(zak)
        
        self.sprawdzenie_nip_zakupow(zak)
        
        return not zerowy



class ZakupGIGPozycjeMkv(Pozycje):
    """
    Korekta podatku naliczonego od nabycia środków trwałych.  
    """
    
    def __init__(self, jpk):
        super(ZakupGIGPozycjeMkv, self).__init__(
            SrtVat.objects.using(jpk.fkdbs('Zakup.SrtVat')).filter(rok= jpk.dataod.year)
        )
        
    def uwzglednij(self, vat):
        
        if vat.korekta_vat == decimal.Decimal(0.0):
            return False
        
        vat.nazwa_kon= vat.mkv.nazwa or '?'
        vat.adres_kon= vat.mkv.uwagi or '?'
        vat.nr_id= vat.mkv.nr_inw or '?'
        vat.nr_faktury= vat.mkv.nr_faktury or '?'
        vat.data_wplywu= vat.mkv.data_ot
        vat.data_zakupu= vat.data_wplywu
        vat.pod_rejestr= "KVM"
        
        vat.k_47= vat.korekta_vat
                    
        vat.podatek_naliczony= vat.k_47
        
        return True
             

    
class ZakupGIGPozycjeMkvLacznie(ZakupGIGPozycjeMkv):
    """
    Korekta podatku naliczonego od nabycia środków trwałych 
    łącznie jedną pozycją.
    """
    
    def __init__(self, jpk):
        super(ZakupGIGPozycjeMkvLacznie, self).__init__(jpk)
        self.jpk= jpk
        
    def __iter__(self):
        """
        Zsumowanie wszystkich pozycji i zwrócenie pojedynczego rekordu.
        """
        vat= SrtVat()
        vat.korekta_vat= decimal.Decimal(0.0)
                
        for poz in super(ZakupGIGPozycjeMkvLacznie, self).__iter__():
            vat.korekta_vat += poz.korekta_vat
            
        f= self.jpk.par_firmy()
        
        vat.nazwa_kon= f['nazwa']
        vat.adres_kon= '{} {}, {} {}'.format(f['miejscowosc'], f['kod_pocztowy'], f['ulica'], f['nr_domu'])
        vat.nr_id= f['nip']
        vat.nr_faktury= 'KOREKTA ROCZNA'
        vat.data_wplywu= self.jpk.dataod
        vat.data_zakupu= vat.data_wplywu
        vat.pod_rejestr= "KOR-T"
        
        return [vat].__iter__()

    def uwzglednij(self, vat):
        # Pola podatek_naliczony i k_47 zostaną wyzerowane przed wywolaniem uwzglednij
        # dlatego odtwarzana jest ich wartość
        vat.podatek_naliczony= vat.k_47= vat.korekta_vat
        
        return vat.k_47 != decimal.Decimal(0.0)
            
    
             
class ZakupGIGPozycjePre(ZakupVATPozycjeZak):
    
    def __init__(self, ctrl, *args, **kwargs):
        super(ZakupGIGPozycjePre, self).__init__(*args, **kwargs)
        self.ctrl= ctrl
        
    def uwzglednij(self, zak):
        """
        Ustalanie korekty podatku naliczonego od pozostałych nabyć (K_48).
        Chodzi o korektę podatku naliczonego prewspółczynnikiem.
        Nie interesuje nas tutaj VAT od zakupów inwestycyjnych (K_47) ponieważ
        jest on ustalany na podstawie rejestru korekt VAT od majątku, gdzie
        korekta rozkładana jest na wiele lat.
        """
        
        super(ZakupGIGPozycjePre, self).przygotuj(zak)
        
        wsp= self.ctrl.pre_wsp
        pop= self.ctrl.pop_wsp
        
        pozycje= False
        for w in zak.wiersze.all():
            pozycje= True
            if not w.zrv[:2] == 'OZ': continue
            # minusujemy poprzednio naliczoną wartość
            if w.ip == 'P':
                zak.k_48 -= procent(w.vat, w.odlicz)
                                
            # współczynnik ostateczny
            odlicz= wsp[1] if w.zrv == 'OZN' else wsp[0]
            # zamiast tego wstawiamy ostateczną wartość
            if w.ip == 'P':            
                zak.k_48 += procent(w.vat, odlicz)
        
        if not pozycje:
            zak.k_48 += procent(zak.soz_p_vat, wsp[0]) - procent(zak.soz_p_vat, pop[0]) + \
                        procent(zak.kos_w_vat, wsp[1]) - procent(zak.kos_w_vat, pop[1])
                      
        zak.podatek_naliczony= zak.k_48

        # Sprawdzenie czy VAT jest w fakturze poprawnie rozliczony
        self.ctrl.vat_rozliczony(zak)
        
        # Jeżeli nie ma korekty to faktura nie jest uwzględniana w JPK   
        return zak.k_48 != decimal.Decimal(0.00)
            


class ZakupGIGPozycjePreLacznie(ZakupGIGPozycjePre):
    
    def __iter__(self):
        """
        Zsumowanie wszystkich pozycji i zwrócenie pojedynczego rekordu.
        """
        
        lacznie= Zak()

        lacznie.korekta_vat= decimal.Decimal(0.0)
        lacznie.jpk= self.ctrl.jpk
                
        for zak in super(ZakupGIGPozycjePreLacznie, self).__iter__():
            zak.jpk= self.ctrl.jpk 
            self.ctrl.uwzglednij(super(ZakupGIGPozycjePreLacznie, self), zak)
            lacznie.korekta_vat += zak.k_48
            
        f= self.ctrl.jpk.par_firmy()
        
        lacznie.nazwa_kon= f['nazwa']
        lacznie.adres_kon= '{} {}, {} {}'.format(f['miejscowosc'], f['kod_pocztowy'], f['ulica'], f['nr_domu'])
        lacznie.nr_id= f['nip']
        lacznie.nr_faktury= 'KOREKTA ROCZNA'
        lacznie.data_wplywu= self.ctrl.jpk.dataod
        lacznie.data_zakupu= lacznie.data_wplywu
        lacznie.pod_rejestr= "KOR-P"
        
        return [lacznie].__iter__()
            
    def uwzglednij(self, zak):
        # Pola podatek_naliczony i k_48 zostaną wyzerowane przed wywolaniem uwzglednij
        # dlatego odtwarzana jest ich wartość
        zak.podatek_naliczony= zak.k_48= zak.korekta_vat
        
        return zak.k_48 != decimal.Decimal(0.0)

