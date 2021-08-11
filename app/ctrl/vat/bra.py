# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from fk.models import MagDok, Zak
from app import utils
from .vat import SprzedazVAT, SprzedazVATPozycjeFak, ZakupVAT, ZakupVATPozycjeZak

import datetime
import decimal
import itertools

import logging
logger= logging.getLogger(__name__)


                    
class SprzedazBRA(SprzedazVAT):
    """
    Część dotyczyąca podatku należnego do deklaracji w BRA tworzona jest 
    na podstawie zapisów z rejestru sprzedaży i zakupów.
    """
    
    def __init__(self, jpk):
        super(SprzedazBRA, self).__init__(jpk)
        
        self.elementy= []
        if jpk.firma.oznaczenie == 'gdf':
            self.elementy.append(SprzedazGDFPozycjeFak(jpk))
        else:
            self.elementy.append(SprzedazBRAPozycjeFak(jpk))


class SprzedazBRAPozycjeFak(SprzedazVATPozycjeFak):
    
    def __init__(self, jpk):
        super(SprzedazBRAPozycjeFak, self).__init__(
            MagDok.objects.select_related('id_kli').using(jpk.fkdbs('Sprzedaz.MagDok')).filter(
                data_pod__gte= jpk.dataod, 
                data_pod__lte= jpk.datado, 
                symbol__in=('FV',), 
                stat='D', 
                dr_fisk__isnull= True).order_by('id')
        )


    def uwzglednij(self, fak):
        """
        Podatek należny z rejestru sprzedaży BRA.
        fak.podsum zawiera podsumowanie pozycji stawkami VAT.
        """

        super(SprzedazBRAPozycjeFak, self).przygotuj(fak)
        
        fak.pod_rejestr= fak.symbol
        
        # Podrejestr sprzedaży będący podstawą (obook stawki VAT) 
        # kwalifikowania sprzedaży do pozycji deklaracji VAT/JPK  
        rejestr= fak.rodz_te.strip() 
             
        for stawka in fak.podsum.keys():
            
            netto= fak.podsum[stawka][0]
            vat= fak.podsum[stawka][1]
            
            if netto is None or vat is None: # pragma: no cover
                # Nie za bardzo wiadomo w jakich okolicznościach taki przypadek mógłby się pojawić
                fak.jpk.blad('SPR', fak.nr_dokumentu, 'Nieokreślona wartość netto lub podatku należnego')

            fak.podatek_nalezny += vat
            
            stawka= stawka[0:2]
            
            if stawka == 'ZW':
                fak.k_10 += netto
                
            elif rejestr == 'PR' and stawka == 'NP':
                fak.k_11 += netto
                if fak.id_kli.nipue(): 
                    fak.k_12 += netto
                    
            elif rejestr in ('PR', 'PU', 'PT') and stawka == ' 0':
                fak.k_13 += netto
                
            elif rejestr in ('PR', 'PU', 'PT') and stawka in (' 5', ' 3'):
                fak.k_15 += netto
                fak.k_16 += vat
                
            elif rejestr in ('PR', 'PU', 'PT') and stawka in (' 8', ' 7'):
                fak.k_17 += netto
                fak.k_18 += vat
                
            elif rejestr in ('PR', 'PU', 'PT') and stawka in ('23', '22'):
                fak.k_19 += netto
                fak.k_20 += vat
                
            elif rejestr == 'DT':
                fak.k_21 += netto
                
            elif rejestr == 'NT':
                fak.k_23 += netto
                fak.k_24 += vat

            elif rejestr == 'OZ':
                fak.k_25 += netto
                fak.k_26 += vat
                                
            elif rejestr == 'IP':
                fak.k_27 += netto
                fak.k_28 += vat
                
            elif rejestr == 'IE':
                fak.k_29 += netto
                fak.k_30 += vat
                
            elif rejestr == 'OS':
                fak.k_31 += netto
                
            elif rejestr == 'ON':
                fak.k_34 += netto
                fak.k_35 += vat
                                
            else:
                fak.k_32 += netto
                fak.k_33 += vat
                
                fak.jpk.blad('SPR', fak.nr_dokumentu, 'Rodzaj sprzedaży {} i/lub stawka VAT {} niezakwalifikowane do żadnego pola deklaracji (tymczasowo wpisane do 34/35)'.format(rejestr, stawka))                

        self.sprawdzenie_nip_sprzedazy(fak)

        return True



class SprzedazGDFPozycjeFak(SprzedazVATPozycjeFak):

    def __init__(self, jpk):
        super(SprzedazGDFPozycjeFak, self).__init__(
                        MagDok.objects.select_related('id_kli').using(jpk.fkdbs('Sprzedaz.MagDok')).filter(
                            data_pod__gte= jpk.dataod, 
                            data_pod__lte= jpk.datado, 
                            symbol__in= ('FV','RU','EX','EK','FW','FP'), 
                            stat='D', 
                            dr_fisk__isnull= True).order_by('id')
                        )

    def uwzglednij(self, fak):
        """
        Źródłem najpierw jest rejestr sprzedaży.
        """

        super(SprzedazGDFPozycjeFak, self).przygotuj(fak)

        fak.pod_rejestr= fak.rodz_te.strip()

        for stawka in fak.podsum.keys():
            netto= fak.podsum[stawka][0]
            vat= fak.podsum[stawka][1]

            if netto is None or vat is None: # pragma: no cover
                fak.jpk.blad('SPR', fak.nr_dokumentu, 'Nieokreślona wartość netto lub podatku należnego')

            fak.podatek_nalezny += vat

            if stawka == 'ZW.':
                fak.k_10 += netto
            elif stawka == ' 0%':
                fak.k_13 += netto
            elif stawka in (' 5%', '05%', ' 3%', '03%'):
                fak.k_15 += netto
                fak.k_16 += vat
            elif stawka in (' 8%', '08%', ' 7%', '07%'):
                fak.k_17 += netto
                fak.k_18 += vat
            elif stawka in ('23%', '22%'):
                fak.k_19 += netto
                fak.k_20 += vat
            else:
                fak.jpk.blad('SPR', fak.nr_dokumentu, 'Pozycja: rodzaj sprzedaży({})/stawka VAT({}) niezakwalifikowana do żadnego pola deklaracji'.format(fak.rodz_te, stawka))

        return True


class ZakupBRA(ZakupVAT):
    """
    Kontrola zakupu VAT.
    """
    
    def __init__(self, jpk):
        super(ZakupBRA, self).__init__(jpk)
        
        self.elementy= [
                        # Faktury zakupu z okresu pliku JPK z bieżącej bazy 
                        ZakupBRAPozycjeZak(self, 
                                # Pozycje z bieżącego miesiąca
                                Zak.objects.select_related('dostawca').prefetch_related('pozycje').using(jpk.fkdbs('Zakup.Zak')).
                                    filter(msc_roz__gte= utils.data_na_miesiac(jpk.dataod),
                                           msc_roz__lte= utils.data_na_miesiac(jpk.datado)). 
                                    order_by('zak_id')                                
                        ),
                       ]
        
        

class ZakupBRAPozycjeZak(ZakupVATPozycjeZak):
    
    def __init__(self, ctrl, *args, **kwargs):
        super(ZakupBRAPozycjeZak, self).__init__(*args, **kwargs)
        self.ctrl= ctrl
        
    def uwzglednij(self, zak):
        
        # Sprawdzenie poprawności i ustalenie podstawowych danych
        super(ZakupBRAPozycjeZak, self).przygotuj(zak)
        
        for p in zak.pozycje.all():
              
            p_roz= p.p_roz.strip()
            
            if p_roz == 'OI':
                zak.k_43 += p.p_netto
                zak.k_44 += p.p_vat
                
            if p_roz == 'OP':
                zak.k_45 += p.p_netto
                zak.k_46 += p.p_vat

        zak.podatek_naliczony= zak.k_44 + zak.k_46
        
        zerowy= True
        for k in range(43, 51):
            if getattr(zak, 'k_{}'.format(k)) != decimal.Decimal(0.00):
                zerowy= False
                break
                    
#         self.ctrl.vat_rozliczony(zak)

        self.sprawdzenie_nip_zakupow(zak)
        
        return not zerowy

