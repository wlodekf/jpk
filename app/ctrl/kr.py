# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import decimal

from app import ctrl, utils
from app.model_utils import poczatek_miesiaca, koniec_miesiaca
from fk.models import Syn, Ana, Ksi, Dow, Uzy, SysPar
from app.utils import data_na_miesiac

class ZOiS(ctrl.CtrlTabeli):
    """
    Kontrola zestawienie obrotów i sald.
    """
    
    def __init__(self, jpk):
        super(ZOiS, self).__init__(jpk)
        
        self.elementy= [Ana.objects.using(jpk.fkdbs('ZOiS.Ana')).all().order_by('numer_a')]    
        self.tabela= 'zois'

    def sumuj(self, i, element):
        self.suma1 += element.obroty_wn
        self.suma2 += element.obroty_ma
                
    def uwzglednij(self, i, ana):
        
        # Uwzględniamy tylko konta bilansowe
        if not ana.bilansowe() and not utils.par_firmy('wszystkie_konta'):
            return False
        
        ana.kod_konta= ana.numer_a
        if len(ana.numer_a.strip())>3:
            ana.kod_konta= '{}-{}'.format(ana.numer_a[:3], ana.numer_a[3:])
            
        ana.obroty_wn= ana.obroty('wn')
        ana.obroty_ma= ana.obroty('ma')
        ana.narasta_wn= ana.narasta('wn')
        ana.narasta_ma= ana.narasta('ma')
        ana.saldo_wn= ana.saldo('wn')
        ana.saldo_ma= ana.saldo('ma')
        
        rc= False
        if ana.wn_0 != 0 or ana.ma_0 != 0: rc= True
        if ana.obroty_wn != 0 or ana.obroty_ma != 0: rc= True
        if ana.narasta_wn != 0 or ana.narasta_ma != 0: rc= True
        if ana.saldo_wn != 0 or ana.saldo_ma != 0: rc= True
        if ana.byl_ruch(): rc= True
        
        if not rc:
            return False
        
        if not ana.nazwa_a or len(ana.nazwa_a.strip())==0:
            ana.jpk.blad('ZOiS', ana.konto_ladnie(), 'Brak nazwy konta')
        if not ana.typ_konta() or len(ana.typ_konta().strip())==0: # pragma: no cover
            ana.jpk.blad('ZOiS', ana.konto_ladnie(), 'Nieokreślony typ konta')
        if not ana.opis_zespolu() or len(ana.opis_zespolu().strip())==0: # pragma: no cover
            ana.jpk.blad('ZOiS', ana.konto_ladnie(), 'Nieokreślony opis zespołu kont')
        if not ana.opis_kategorii() or len(ana.opis_kategorii().strip())==0:
            ana.jpk.blad('ZOiS', ana.konto_ladnie(), 'Nieokreślony opis kategorii kont (syntetyki)')  

        return True        



class Dziennik(ctrl.CtrlTabeli):
    """
    Kontrola dziennika księgowań.
    """
    
    def __init__(self, jpk):
        super(Dziennik, self).__init__(jpk)
        
        self.elementy= [Dow.objects.using(jpk.fkdbs('Dziennik.Dow')).filter(miesiac__gte= jpk.od_msc(), miesiac__lte= jpk.do_msc()).order_by('miesiac', 'lp_dzi')]
        self.tabela= 'dziennik'
        self.dbs= jpk.fkdbs('Dziennik.init')
        
        par_dzi= SysPar.get_wartosc('DZI', jpk.fkdbs('DZI'), current= True)
        if  par_dzi < jpk.do_msc():
            jpk.blad('Dziennik', par_dzi, 'Dziennik jest ponumerowany tylko do {}'.format(par_dzi))              
            
    def sumuj(self, i, element):
        self.suma1 += element.suma

    def uwzglednij(self, i, dow):
        if dow.lp_dzi is None:
            return False
        
        if not dow.rodzaj_dowodu_nazwa() or len(dow.rodzaj_dowodu_nazwa())==0:
            dow.jpk.blad('Dziennik', dow.nr_dowodu, 'Nieokreślony rodzaj dowodu księgowego')
                    
        dow.kod_operatora= Uzy.kod_operatora(dow.kto, self.dbs)
        
        if dow.d_operacji is None or dow.d_dowodu is None:
            dow.ustal_zrodlowe()
            
        # W ICHP np. data w nagłówku dowodu czasami nie jest podawana!!!
        if not dow.d_wyst:
            dow.d_wyst= koniec_miesiaca(dow.miesiac)
             
        # Ustalenie daty operacji
        # W przypadku sprzedaży i zakupów ustalane z odpowiedniego rejestru
        if dow.d_operacji is None:
            dow.d_operacji= dow.d_wyst
        dow.msc_operacji= data_na_miesiac(dow.d_operacji)
            
        # Ustalanie daty dowodu (faktury)
        # W przypadku sprzedaży i zakupów ustalana z odpowiedniego rejestru
        if dow.d_dowodu is None:
            dow.d_dowodu= dow.d_wyst
        dow.msc_dowodu= data_na_miesiac(dow.d_dowodu)
            
        # Ustalenie daty księgowania
        dow.d_ksiegowania= dow.d_wyst
        dow.msc_ksiegowania= data_na_miesiac(dow.d_wyst)
        if dow.msc_ksiegowania < dow.miesiac:
            dow.d_ksiegowania= poczatek_miesiaca(dow.miesiac)
        if dow.msc_ksiegowania > dow.miesiac:
            dow.d_ksiegowania= koniec_miesiaca(dow.miesiac)
        dow.msc_ksiegowania= data_na_miesiac(dow.d_ksiegowania) 
        
        if not dow.d_operacji:
            dow.jpk.blad('Dziennik', dow.nr_dowodu, 'Brak daty operacji gospodarczej')                   
        if not dow.d_dowodu:
            dow.jpk.blad('Dziennik', dow.nr_dowodu, 'Brak daty dowodu księgowego') 
        if not dow.d_ksiegowania:
            dow.jpk.blad('Dziennik', dow.nr_dowodu, 'Brak daty księgowania') 
        if not dow.kod_operatora or len(dow.kod_operatora)==0:
            dow.jpk.blad('Dziennik', dow.nr_dowodu, 'Brak kodu operatora') 
        if not dow.opis() or len(dow.opis())==0:
            dow.jpk.blad('Dziennik', dow.nr_dowodu, 'Brak opisu operacji gospodarczej') 
        if dow.suma is None:
            dow.jpk.blad('Dziennik', dow.nr_dowodu, 'Brak kwoty operacji')             
                                                        
        return True
    

class KontoZapis(ctrl.CtrlTabeli):
    """
    Kontrola zapisów na kontach.
    """
    
    def __init__(self, jpk):
        super(KontoZapis, self).__init__(jpk)
        
        do_dziennika= Ksi.objects.using(jpk.fkdbs('KontoZapis.Ksi')).filter(miesiac__gte= jpk.od_msc(), miesiac__lte= jpk.do_msc(), glowna__isnull= True).order_by('miesiac', 'lp_dzi', 'ksi_id')
        if not utils.par_firmy('wszystkie_konta'):
            do_dziennika= do_dziennika.filter(lp_dzi__isnull= False)
            
        self.elementy= [do_dziennika]
            
        self.tabela= 'konto_zapis'
            
    def sumuj(self, i, element):
        self.suma1 += element.wn_kwota
        self.suma2 += element.ma_kwota
        
    def uwzglednij(self, i, ksi):
        
        ksi_opi= ksi.ksi_opi()
        if ksi.opis:
            ksi_opi= ksi.opis.strip()+ (', '+ksi_opi if ksi_opi else '')
            
        if ksi.strona == 'W':
            ksi.wn_konto= ksi.konto
        elif ksi.d2 == 'T':
            ksi.wn_konto= ksi.przeciwne
        else:
            ksi.wn_konto= None
        
        if ksi.wn_konto and (Syn.bilansowe(ksi.wn_konto, self.jpk) or utils.par_firmy('wszystkie_konta')):
            if len(ksi.wn_konto.strip())>3:
                ksi.wn_konto= '{}-{}'.format(ksi.wn_konto[:3], ksi.wn_konto[3:])
            ksi.wn_kwota= ksi.kwota
            ksi.wn_kwota_wal= ksi.k2
            ksi.wn_kod_wal= ksi.waluta
            ksi.wn_opis= ksi_opi
        else:
            ksi.wn_konto= 'null'
            ksi.wn_kwota= decimal.Decimal(0)
            ksi.wn_kwota_wal= ksi.wn_kod_wal= ksi.wn_opis= None
        
        if ksi.strona == 'M':
            ksi.ma_konto= ksi.konto
        elif ksi.d2 == 'T':
            ksi.ma_konto= ksi.przeciwne
        else:
            ksi.ma_konto= None
            
        if ksi.ma_konto and (Syn.bilansowe(ksi.ma_konto, self.jpk) or utils.par_firmy('wszystkie_konta')):
            if len(ksi.ma_konto.strip())>3:            
                ksi.ma_konto= '{}-{}'.format(ksi.ma_konto[:3], ksi.ma_konto[3:])
            ksi.ma_kwota= ksi.kwota
            ksi.ma_kwota_wal= ksi.k2
            ksi.ma_kod_wal= ksi.waluta
            ksi.ma_opis= ksi_opi
        else:
            ksi.ma_konto= 'null'
            ksi.ma_kwota= decimal.Decimal(0)
            ksi.ma_kwota_wal= ksi.ma_kod_wal= ksi.ma_opis= None
            
        if ksi.wn_konto == 'null' and ksi.ma_konto == 'null':
            return False
        
        if not ksi.lp_dzi:
            ksi.jpk.blad('KontoZapis', '{}[{}]'.format(ksi.nr_dowodu, ksi.ksi_id), 'Brak numeru dziennika')          
             
        return True            
