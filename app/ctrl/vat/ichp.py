# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from fk.models import MagDok, Zak
from app.utils import procent

from .vat import SprzedazVAT, SprzedazVATPozycjeFak, ZakupVAT, ZakupVATPozycjeZak

import datetime
import decimal
from django.conf import settings

import logging
logger= logging.getLogger(__name__)


class SprzedazICHP(SprzedazVAT):
    """
    Kontrola sprzedaży VAT.
    """
    
    def __init__(self, jpk):
        super(SprzedazICHP, self).__init__(jpk)
        
        baza= jpk.fkdbs('Sprzedaz.MagDok')
        self.elementy= [SprzedazIchpPozycjeFak(jpk, baza)]

        if baza != jpk.par_firmy('db_ostatnia'):
            self.elementy.append(SprzedazIchpPozycjeFak(jpk, jpk.par_firmy('db_ostatnia')))


class SprzedazIchpPozycjeFak(SprzedazVATPozycjeFak):
    
    def __init__(self, jpk, baza):
        super(SprzedazIchpPozycjeFak, self).__init__(
                        MagDok.objects.select_related('id_kli').using(baza).filter(
                            data_pod__gte= jpk.dataod, 
                            data_pod__lte= jpk.datado, 
                            symbol__in= ('FV','RU','EX','EK','FW','FP'), 
                            pid__isnull= True,
                            stat='D', 
                            dr_fisk__isnull= True).order_by('id')
                        )
                                                                
    def uwzglednij(self, fak):
        """
        Źródłem najpierw jest rejestr sprzedaży a później zakupów.
        """

        super(SprzedazIchpPozycjeFak, self).przygotuj(fak)
        
        fak.pod_rejestr= fak.rodz_te.strip()
             
        for stawka in fak.podsum.keys():
            netto= fak.podsum[stawka][0]
            vat= fak.podsum[stawka][1]
            
            if netto is None or vat is None: # pragma: no cover
                fak.jpk.blad('SPR', fak.nr_dokumentu, 'Nieokreślona wartość netto lub podatku należnego')
                            
            fak.podatek_nalezny += vat
            
            if fak.nr_dokumentu in ('EU0086/270/16', 'EU0087/270/16', 'EU0091/270/16'):
                fak.k_19 += netto
                fak.k_20 += vat                
            elif fak.rodz_tem('ET'):
                fak.k_21 += netto
            elif fak.rodz_tem('40'):
                fak.k_22 += netto
            elif fak.rodz_tem('UT'):
                fak.k_23 += netto
                fak.k_24 += vat
            elif fak.rodz_tem('UI'):
                fak.k_27 += netto 
                fak.k_28 += vat
            elif fak.rodz_tem('UU'):
                fak.k_29 += netto 
                fak.k_30 += vat                                   
            elif (fak.rodz_tem('29') or fak.rodz_tem('30')) and fak.rodzaj and 'O' in fak.rodzaj:
                fak.k_31 += netto 
            elif stawka == 'ZW.':
                fak.k_10 += netto
            elif stawka == 'NP.' or fak.rodz_tem('EU') or fak.nr_dokumentu == '800019/320/17':
                fak.k_11 += netto
                if fak.rodz_tem('EU') or fak.nr_dokumentu == '800019/320/17':
                    fak.k_12 += netto
            elif stawka == ' 0%':
                fak.k_13 += netto
            elif stawka in (' 5%', ' 3%'):
                fak.k_15 += netto
                fak.k_16 += vat
            elif stawka in (' 8%', ' 7%'):
                fak.k_17 += netto
                fak.k_18 += vat
            elif stawka in ('23%', '22%'):
                fak.k_19 += netto
                fak.k_20 += vat
            elif stawka == 'OO.':
                fak.k_10 += netto                
            else:
                fak.jpk.blad('SPR', fak.nr_dokumentu, 'Pozycja: rodzaj sprzedaży({})/stawka VAT({}) niezakwalifikowana do żadnego pola deklaracji'.format(fak.rodz_te, stawka))   

        self.sprawdzenie_nip_sprzedazy(fak)

        return True
    

    
class ZakupICHP(ZakupVAT):
    """
    Kontrola zakupu VAT.
    """
    
    def __init__(self, jpk):
        super(ZakupICHP, self).__init__(jpk)
        
        self.elementy= [ZakupIchpPozycjeZak(self,
                            Zak.objects.select_related('dostawca').using(jpk.fkdbs('Zakup.Zak')).filter(
                                d_ksieg__gte= jpk.dataod, 
                                d_ksieg__lte= jpk.datado)
                            .order_by('zak_id')),
                       ]
            
        # Korekty VAT majątku trwałego i prewspółczynnika dołączane są tylko dla pierwszej deklaracji
        # czyli JPK od 1 stycznia
        
        if jpk.dataod.month == 1 and jpk.dataod.day == 1:
            if self.pre_wsp[0] != self.pop_wsp[0] or self.pre_wsp[1] != self.pop_wsp[1]:
                # Jeżeli zmienił się któryś z prewspółczynników
                
                dataod= datetime.date(jpk.dataod.year-1, 1, 1)
                datado= datetime.date(jpk.dataod.year-1, 12, 31)
                
                logger.info('PRE daty: {} - {}'.format(dataod, datado))
                
                # Faktury zakupu z okresu pliku JPK z bieżącej bazy
                
                self.elementy.append((ZakupIchpPozycjePreLacznie if settings.KOREKTA_VAT_LACZNIE else ZakupIchpPozycjePre)(self,
                    Zak.objects.select_related('dostawca').using(jpk.fkdbs('Zakup.Zak', dataod= dataod)).filter(
                            d_ksieg__gte= dataod, 
                            d_ksieg__lte= datado)
                    .order_by('zak_id')
                ))
                
                    
class ZakupIchpPozycjeZak(ZakupVATPozycjeZak):
    
    def __init__(self, ctrl, *args, **kwargs):
        super(ZakupIchpPozycjeZak, self).__init__(*args, **kwargs)
        self.ctrl= ctrl
        
    def uwzglednij(self, zak):
        
        wsp= self.ctrl.pre_wsp
        
        # Sprawdzenie poprawności i ustalenie podstawowych danych
        super(ZakupIchpPozycjeZak, self).przygotuj(zak)
        
        pozycje= False
        for w in zak.wiersze.all():
            pozycje= True
            if w.zrv == 'BEZ': continue
              
            if w.ip == 'I':
                zak.k_43 += w.netto
                zak.k_44 += procent(w.vat, w.odlicz)
            else:
                zak.k_45 += w.netto
                zak.k_46 += procent(w.vat, w.odlicz)
        
        if not pozycje:
            zak.k_43= zak.sop_i_net + zak.soz_i_net
            zak.k_44= zak.sop_i_vat + procent(zak.soz_i_vat, wsp[0])
            
            zak.k_45= zak.sop_p_net + zak.soz_p_net
            zak.k_46= zak.sop_p_vat + procent(zak.soz_p_vat, wsp[0])
            
        zak.podatek_naliczony= zak.k_44 + zak.k_46
        
        zerowy= True
        for k in range(43, 51):
            if getattr(zak, 'k_{}'.format(k)) != decimal.Decimal(0.00):
                zerowy= False
                break
                    
        self.ctrl.vat_rozliczony(zak)

        self.sprawdzenie_nip_zakupow(zak)

        return not zerowy



class ZakupIchpPozycjePre(ZakupVATPozycjeZak):
    
    def __init__(self, ctrl, *args, **kwargs):
        super(ZakupIchpPozycjePre, self).__init__(*args, **kwargs)
        self.ctrl= ctrl
        
    def uwzglednij(self, zak):
        """
        Ustalanie korekty podatku naliczonego od pozostałych nabyć (K_48).
        Chodzi o korektę podatku naliczonego prewspółczynnikiem.
        Nie interesuje nas tutaj VAT od zakupów inwestycyjnych (K_47) ponieważ
        jest on ustalany na podstawie rejestru korekt VAT od majątku, gdzie
        korekta rozkładana jest na wiele lat.
        """
        
        super(ZakupIchpPozycjePre, self).przygotuj(zak)
        
        wsp= self.ctrl.pre_wsp
        pop= self.ctrl.pop_wsp
        
        pozycje= False
        for w in zak.wiersze.all():
            pozycje= True
            if not w.zrv[:2] == 'OZ': continue
            
            if w.ip == 'P':
                zak.k_48 -= procent(w.vat, w.odlicz)
                                
            odlicz= wsp[1] if w.zrv == 'OZN' else wsp[0]

            if w.ip == 'P':            
                zak.k_48 += procent(w.vat, odlicz)
        
        if not pozycje:
            zak.k_47 += procent(zak.soz_i_vat, decimal.Decimal(100.0)) - procent(zak.soz_i_vat, pop[0])            
            zak.k_48 += procent(zak.soz_p_vat, decimal.Decimal(100.0)) - procent(zak.soz_p_vat, pop[0])
                      
        zak.podatek_naliczony= zak.k_47 + zak.k_48

        # Sprawdzenie czy VAT jest w fakturze poprawnie rozliczony
        self.ctrl.vat_rozliczony(zak)
        
        # Jeżeli nie ma korekty to faktura nie jest uwzględniana w JPK         
        return zak.k_47 != decimal.Decimal(0.00) or zak.k_48 != decimal.Decimal(0.00)


class ZakupIchpPozycjePreLacznie(ZakupIchpPozycjePre):
    
    def __iter__(self):
        """
        Zsumowanie wszystkich pozycji i zwrócenie pojedynczego rekordu.
        """
        
        lacznie= Zak()

        lacznie.korekta_47= decimal.Decimal(0.0)
        lacznie.korekta_48= decimal.Decimal(0.0)        
        lacznie.jpk= self.ctrl.jpk
                
        for zak in super(ZakupIchpPozycjePreLacznie, self).__iter__():
            zak.jpk= self.ctrl.jpk 
            self.ctrl.uwzglednij(super(ZakupIchpPozycjePreLacznie, self), zak)
            lacznie.korekta_47 += zak.k_47
            lacznie.korekta_48 += zak.k_48
            
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
        zak.k_47= zak.korekta_47
        zak.k_48= zak.korekta_48

        zak.podatek_naliczony= zak.k_47 + zak.k_48
        
        return zak.k_47 != decimal.Decimal(0.0) or zak.k_48 != decimal.Decimal(0.0)
    