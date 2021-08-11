# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.six import string_types
from django.db import models
from django.conf import settings

from operator import itemgetter
 
import decimal
import datetime
import re

from app import utils

                 
PREFIKSY_KRAJOW= ('AT', 'BE', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'EL', 'ES', 
                  'NL', 'IE', 'LT', 'LU', 'LV', 'MT', 'DE', 'PL', 'PT', 'SK', 
                  'SI', 'SE', 'HU', 'GB', 'IT')

TYPY_DOKUMENTOW= ('RO', 'WEW', 'FP')

PROCEDURY= ['SW', 'EE', 'TP', 'TT_WNT', 'TT_D', 'MR_T', 'MR_UZ', 'I_42', 'I_63', 'B_SPV', 'B_SPV_DOSTAWA', 'B_MPV_PROWIZJA', 'MPP', 'KPO']
PROCEDURY_MAP= {'KPO': 'KorektaPodstawyOpodt'}


class Ana(models.Model):
    
    anal_id= models.AutoField(primary_key= True)
    numer_a= models.CharField(max_length= 20)
    nazwa_a= models.CharField(max_length= 80)
    
    wn_0= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    wn_1= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    wn_2= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    wn_3= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    wn_4= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    wn_5= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    wn_6= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    wn_7= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    wn_8= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    wn_9= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)            
    wn_10= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    wn_11= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    wn_12= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    
    ma_0= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    ma_1= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    ma_2= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    ma_3= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    ma_4= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    ma_5= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    ma_6= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    ma_7= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    ma_8= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    ma_9= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    ma_10= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    ma_11= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)
    ma_12= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0)    
                
    class Meta:
        managed= False
        db_table= 'ana'
        
    def bilansowe(self):
        return Syn.bilansowe(self.numer_a, self.jpk)
    
    def obroty(self, strona):
        obroty= decimal.Decimal(0.0)
        for m in range(self.jpk.dataod.month, self.jpk.datado.month+1):
            obroty += getattr(self, '{}_{}'.format(strona, m))
        return obroty
    
    def narasta(self, strona):
        obroty= decimal.Decimal(0.0)
        for m in range(0, self.jpk.datado.month+1):
            obroty += getattr(self, '{}_{}'.format(strona, m))
        return obroty
    
    def saldo(self, strona):
        wn= self.narasta_wn
        ma= self.narasta_ma
        if strona == 'wn':
            return wn-ma if wn>ma else 0.0
        else:
            return ma-wn if ma>wn else 0.0            
        
    def byl_ruch(self):
        if not hasattr(self.jpk, '_ruch') or self.jpk._ruch is None:
            self.jpk._ruch= [x.strip() for x in Ksi.objects.using(self.jpk.fkdbs('byl_ruch')).filter(miesiac__lte= utils.data_na_miesiac(self.jpk.datado)).values_list('konto', flat=True).distinct()]
        return self.numer_a.strip() in self.jpk._ruch
#         return Ksi.objects.using(self.jpk.fkdbs()).filter(konto=self.numer_a, miesiac__lte= data_na_miesiac(self.jpk.datado)).exists()
        
    def typ_konta(self):
        typy= []
        typy.append('bilansowe' if Syn.bilansowe(self.numer_a, self.jpk) else 'pozabilansowe')
        
        if Syn.rozliczeniowe(self.numer_a, self.jpk):
            typy.append('rozliczeniowe')
            
        return ', '.join(typy)
    
    def kod_zespolu(self):
        return self.numer_a[0]
    
    def opis_zespolu(self):
        return {'0': 'MAJĄTEK TRWAŁY',
                '1': 'ŚRODKI PIENIĘŻNE',
                '2': 'ROZRACHUNKI I ROSZCZENIA',
                '3': 'MATERIAŁY I TOWARY',
                '4': 'KOSZTY WG RODZAJU',
                '5': 'KOSZTY WG TYPÓW DZIAŁALNOŚCI',
                '6': 'PRODUKTY',
                '7': 'PRZYCHODY',
                '8': 'FUNDUSZE I KAPITAŁY',
                '9': 'POZABILANSOWE'
                }.get(self.numer_a[0])
                
    def kod_kategorii(self):
        return Syn.kod_kategorii(self.numer_a, self.jpk)
    
    def opis_kategorii(self):
        return Syn.opis_kategorii(self.numer_a, self.jpk)
    
    def konto_ladnie(self):
        return self.numer_a[:3]+'-'+self.numer_a[3:]
    
    @staticmethod
    def testowe(*args, **kwargs):
        pola= {}
        pola.update(dict(zip(('numer_a', 'nazwa_a'), args)))
        pola.update(kwargs)
        
        return Ana.objects.using(utils.test_dbs(pola)).create(**pola)
    


class DefZrv(models.Model):
    
    zrv_id= models.AutoField(primary_key= True)
    kod= models.CharField(max_length= 10)
    zrv= models.CharField(max_length= 3)
    odlicz= models.DecimalField(null= False, max_digits=6, decimal_places=2, blank= False, default= 0)
    uwagi= models.CharField(max_length= 100)
    rok= models.SmallIntegerField()

    class Meta:
        managed= False        
        db_table= 'def_zrv'
        ordering= ['zrv_id']
       
    @staticmethod      
    def pre_wsp(fkdbs, rok):
        """
        Ustalenie domyślnych wartości prewspółczynników OZ, OZN dla roku, dla którego tworzony jest JPK
        """
        def_zrv= DefZrv.objects.using(fkdbs).filter(kod__in= ('OZ', 'OZN'), rok= rok)
        wsp= [None, None]
        for zrv in def_zrv:
            if zrv.kod.strip() == 'OZ':
                wsp[0]= zrv.odlicz
            if zrv.kod.strip() == 'OZN':
                wsp[1]= zrv.odlicz
        return wsp
    
    @staticmethod
    def testowe(*args, **kwargs):
        pola= {}
        pola.update(dict(zip(('rok', 'zrv', 'odlicz'), args)))
        pola['kod']= pola['zrv'] # wartość domyślna dla roku
        pola.update(kwargs)
        
        return DefZrv.objects.using(utils.test_dbs(pola)).create(**pola)
    
    
        
class Syn(models.Model):
    
    synt_id= models.AutoField(primary_key= True)
    numer_s= models.CharField(max_length= 3)
    nazwa_s= models.CharField(max_length= 40)
    bilans= models.CharField(max_length= 1)
    spec= models.CharField(max_length= 1)

    class Meta:
        managed= False
        db_table= 'syn'
    
    @staticmethod
    def syntetyki(jpk):    
        if not hasattr(jpk, '_syntetyki') or not jpk._syntetyki:
            jpk._syntetyki= {syn.numer_s: syn for syn in Syn.objects.using(jpk.fkdbs('Syn.syntetyki')).all()}
        return jpk._syntetyki
            
    @staticmethod
    def syntetyka(numer_a, jpk):
        syntetyka= Syn.syntetyki(jpk).get(numer_a[0:3])
        if not syntetyka:
            syntetyka= Syn(numer_s= '', nazwa_s= '', bilans= 'P', spec= 'N')
        return syntetyka
            
    @staticmethod
    def bilansowe(numer_a, jpk):
        syntetyka= Syn.syntetyka(numer_a, jpk)
        return syntetyka.bilans == 'B'
    
    @staticmethod
    def rozliczeniowe(numer_a, jpk):
        syntetyka= Syn.syntetyka(numer_a, jpk)
        return syntetyka.spec in ('D', 'K')
        
    @staticmethod
    def kod_kategorii(numer_a, jpk):
        syntetyka= Syn.syntetyka(numer_a, jpk)
        return syntetyka.numer_s
        
    @staticmethod
    def opis_kategorii(numer_a, jpk):
        syntetyka= Syn.syntetyka(numer_a, jpk)
        return syntetyka.nazwa_s

    @staticmethod
    def testowe(*args, **kwargs):
        pola= {'bilans': 'B'}
        pola.update(dict(zip(('numer_s', 'nazwa_s'), args)))
        pola.update(kwargs)
        
        return Syn.objects.using(utils.test_dbs(pola)).create(**pola)
    
            
        
class Dow(models.Model):
    
    dow_id= models.AutoField(primary_key= True, db_column= 'dow_id')
    nr_dowodu= models.CharField(max_length= 10)
    miesiac= models.CharField(max_length= 7)
    d_wyst= models.DateField()
    d_ksieg= models.DateField()
    suma= models.DecimalField(max_digits= 16, decimal_places= 2)
    rodzaj= models.CharField(max_length= 2)
    numer= models.IntegerField()
    lpoz= models.SmallIntegerField()
    kto= models.ForeignKey('Uzy', db_column= 'kto')
    kiedy= models.DateField()
    lp_dzi= models.IntegerField(null= True)
    opis_operacji= models.CharField(max_length= 100)
    d_operacji= models.DateField()
    d_dowodu= models.DateField()
        
    class Meta:
        managed= False
        db_table= 'dow'
    
    def rodzaj_dowodu(self):
        """
        Ustalenie rodzaju danego dowodu księgowego.
        """
        rodzaj= self.nr_dowodu
        
        if SysPar._gig():
            # Może zrobić podobnie jak w ICHP?
            rodzaj= re.sub(r'[\d-].*$', '', self.nr_dowodu)
            if len(rodzaj) == 0:
                rodzaj= self.nr_dowodu
        
        if SysPar._ichp():
            rex= '|'.join(self.jpk.slownik(utils.par_firmy('rdok')).keys())
            m= re.match(rex, self.nr_dowodu)
            if m:
                rodzaj= m.group(0)
        
        return rodzaj
    
    def rodzaj_dowodu_nazwa(self):
        """
        Kod rodzaju dowodu i nazwa ze słownika.
        """
        rodzaj= self.rodzaj_dowodu()
        nazwa= Spo.nazwa_pozycji(utils.par_firmy('rdok'), rodzaj, self.jpk)
        return nazwa or rodzaj
    
    def opis(self):
        if self.opis_operacji:
            return self.opis_operacji.strip()
        else:
            rodzaj= self.rodzaj_dowodu()
            return Spo.nazwa_pozycji(utils.par_firmy('rdok'), rodzaj, self.jpk)
                
    def ustal_zrodlowe(self):
        """
        Ustalenie danych (dat, opisu) dokumentu źródłowego (sprzedaży lub zakupów)
        """
        fak= None
        if (SysPar._gig() and self.rodzaj_dowodu() == 'S') or (SysPar._ichp() and self.rodzaj_dowodu()[0] == '7'):
            fak= MagDok.objects.using(self.jpk.fkdbs('Dow.ustal_zrodlowe1')).filter(rodz_te=self.nr_dowodu[1:3], numer=int(re.sub('\D','',self.nr_dowodu[3:7])), data=self.d_wyst)
            
        if fak:
            fak= fak[0]
            self.d_operacji= fak.data_sp
            self.d_dowodu= fak.data
            self.opis_operacji= 'SPRZEDAŻ, {}{:04d}/{}/{:02d}, {}'.format(fak.rodz_te.strip(), fak.numer, fak.kod_wydz.strip(), (fak.data.year%100), fak.uwagi or '')
            return
                
        zak= None
        if SysPar._gig() and self.rodzaj_dowodu() in ('ZAG', 'ZFU', 'ZFM', 'ZRU', 'ZRM'):
            if self.rodzaj_dowodu()[1] == 'R':
                zak= Zak.objects.using(self.jpk.fkdbs('Dow.ustal_zrodlowe2')).filter(dow_roz=self.nr_dowodu, msc_roz=self.miesiac, d_otrzym=self.d_wyst)
                if not zak:
                    zak= Zak.objects.using(self.jpk.fkdbs('Dow.ustal_zrodlowe3')).filter(dow_roz=self.nr_dowodu, msc_roz=self.miesiac)
            else:
                zak= Zak.objects.using(self.jpk.fkdbs('Dow.ustal_zrodlowe4')).filter(dow_fak=self.nr_dowodu, msc_fak=self.miesiac, d_otrzym=self.d_wyst)
                if not zak:
                    zak= Zak.objects.using(self.jpk.fkdbs('Dow.ustal_zrodlowe5')).filter(dow_fak=self.nr_dowodu, msc_fak=self.miesiac)                
        
        if SysPar._ichp() and self.rodzaj_dowodu() in ('41', '20', '31', '90', '98', '84'):        
            zak= Zak.objects.using(self.jpk.fkdbs('Dow.ustal_zrodlowe4')).filter(dow_fak=self.nr_dowodu, msc_fak=self.miesiac, d_zak=self.d_wyst)
            if not zak:
                zak= Zak.objects.using(self.jpk.fkdbs('Dow.ustal_zrodlowe5')).filter(dow_fak=self.nr_dowodu, msc_fak=self.miesiac)                
 
        if zak:
            zak= zak[0]
            self.d_operacji= zak.d_zak
            self.d_dowodu= zak.d_wyst
            self.opis_operacji= 'ZAKUP, {}, {}'.format(zak.faktura, zak.uwagi)

    @staticmethod
    def testowe(*args, **kwargs):
        pola= {}
        pola.update(dict(zip(('nr_dowodu', 'miesiac', 'd_wyst', 'lp_dzi', 'suma'), args)))
        pola.update(kwargs)
        
        return Dow.objects.using(utils.test_dbs(pola)).create(**pola)
    
            
                
class Ksi(models.Model):
    
    ksi_id= models.AutoField(primary_key= True, db_column= 'ksi_id')
    
    dowod= models.ForeignKey('Dow', db_column= 'dowod')
    nr_dowodu= models.CharField(max_length= 10)
    miesiac= models.CharField(max_length= 7)
    d_wyst= models.DateField(null= True)
    d_ksieg= models.DateField()
    d_kto= models.IntegerField(null= True)
    
    konto= models.CharField(max_length= 20)
    strona= models.CharField(max_length= 1)
    kwota= models.DecimalField(max_digits= 16, decimal_places= 2)
    
    opis= models.CharField(max_length= 30, null= True)
    glowna= models.OneToOneField('Ksi', db_column= 'glowna', null= True)
    data= models.DateField(null= True)
    lp_dzi= models.IntegerField(null= True)
    k2= models.DecimalField(max_digits= 16, decimal_places= 2, null= True)    
    waluta= models.CharField(max_length= 3, null= True)   
    przeciwne= models.CharField(max_length= 20, null= True)
    d2= models.CharField(max_length= 1, null= True)
    
    class Meta:
        managed= False
        db_table= 'ksi'
    
    def ksi_opi(self):
        ksi_id= self.glowna.ksi_id if self.glowna else self.ksi_id
        try:
            uwagi= KsiOpi.objects.using(self.jpk.fkdbs('Ksi.ksi_opi')).get(ksi_id= ksi_id, zaksieg='T').uwagi
        except:
            uwagi= ''
        return uwagi
        
    @staticmethod
    def testowe(*args, **kwargs):
        pola= {'d_ksieg': '2016-07-31', }
        pola.update(dict(zip(('dowod', 'nr_dowodu', 'miesiac', 'd_wyst', 'lp_dzi', 'konto', 'strona', 'kwota', 'opis'), args)))
        pola.update(kwargs)
        
        return Ksi.objects.using(utils.test_dbs(pola)).create(**pola)
    
    
        
class KsiOpi(models.Model):
    
    ksi_id= models.AutoField(primary_key= True)
    zaksieg= models.CharField(max_length= 1)
    uwagi= models.CharField(max_length= 100)

    class Meta:
        managed= False
        db_table= 'ksi_opi'
        
            
        
class Uzy(models.Model):
    
    uzy_id= models.AutoField(primary_key= True)
    nr_uzy= models.CharField(max_length= 10)

    class Meta:
        managed= False
        db_table= 'sys_uzy'
        
        
    @staticmethod
    def operatorzy(dbs):
        if not hasattr(Uzy, '_operatorzy') or not Uzy._operatorzy:   
            Uzy._operatorzy= {uzy.uzy_id:uzy.nr_uzy.strip() for uzy in Uzy.objects.using(dbs).all()}
        return Uzy._operatorzy
    
    @staticmethod
    def kod_operatora(uzy, dbs):
        if uzy:
            return Uzy.operatorzy(dbs).get(uzy.uzy_id)
        else:
            return uzy
    
    
    @staticmethod
    def testowe(*args, **kwargs):
        pola= {}
        pola.update(dict(zip(('nr_uzy',), args)))
        pola.update(kwargs)
        
        return Uzy.objects.using(utils.test_dbs(pola)).create(**pola)
    
        
                        
class MagDok(models.Model):
    
    id = models.AutoField(primary_key= True)
    korygowana = models.ForeignKey('MagDok', db_column= 'id_na_podst', null=True, blank=True)
    stat = models.CharField(max_length=1, blank=True, default= 'D')
    korekta = models.CharField(max_length=1, blank=True, default= 'D')
    dzial = models.CharField(max_length=3, blank=True, default= 'USL')
    skad = models.ForeignKey('MagDzial', db_column= 'skad', max_length=3, null= True, blank=True)
    dokad = models.CharField('MagDzial', db_column= 'dokad', max_length=3, null= True, blank=True)
    symbol = models.CharField(max_length=2, blank=True)
    symbol2 = models.CharField(max_length=2, blank=True, null= True)
    numer = models.IntegerField(null=True, blank=True)
    numer2 = models.IntegerField(blank=True, null= True)
    numer_abs = models.IntegerField(null=True, blank=True)
    rodz_te = models.CharField(max_length=3, blank=True, null= True)
    kod_wydz = models.CharField(max_length=3, blank=True, null= True)
    nr_dok = models.CharField(max_length=15, blank=True, null= True)
    data = models.DateField(null=True, blank=True)
    data2 = models.DateField(null=True, blank=True)
    data_sp = models.DateField(null=True, blank=True)
    nr_dysp = models.IntegerField(null=True, blank=True)
    data_dysp = models.DateField(null=True, blank=True)
    dzial_dysp = models.CharField(max_length=3, blank=True, null= True)
    wystawil = models.IntegerField(null=True, blank=True)
    zrealizowal = models.IntegerField(null=True, blank=True)
    id_kli = models.ForeignKey('Kon', db_column= 'id_kli', blank=True, null= True)
    nip = models.CharField(max_length=20, blank=True, null= True)
    kat_sprz = models.CharField(max_length=1, blank=True, null= True)
    upust_sp = models.DecimalField(null=True, max_digits=2, decimal_places=0, blank=True)
    upust_gt = models.DecimalField(null=True, max_digits=1, decimal_places=0, blank=True)
    sp_zapl = models.CharField(max_length=1, blank=True, null= True)
    term_zapl = models.DateField(null=True, blank=True)
    zamow = models.CharField(max_length=20, blank=True, null= True)
    data_zam = models.DateField(null=True, blank=True)
    uwagi = models.CharField(max_length=120, blank=True, null= True)
    tty = models.CharField(max_length=3, blank=True, null= True)
    wsk_druk = models.CharField(max_length=1, blank=True, null= True)
    wart_det = models.DecimalField(null=True, max_digits=12, decimal_places=2, blank=True)
    wart_bru = models.DecimalField(null=True, max_digits=12, decimal_places=2, blank=True)
    zaplata = models.DecimalField(null=True, max_digits=12, decimal_places=2, blank=True)
    nr_kp = models.IntegerField(null=True, blank=True)
    data_pod = models.DateField(null=True, blank=True)
    nr_dow = models.CharField(max_length=15, blank=True, null= True)
    nr_dow2 = models.CharField(max_length=15, blank=True, null= True)
    wsk_wyc = models.CharField(max_length=1, blank=True, null= True)
    podpis = models.CharField(max_length=60, blank=True, null= True)
    ldzien = models.CharField(max_length=10, blank=True, null= True)
    rodzaj = models.CharField(max_length=10, blank=True, null= True)
    nr_fisk = models.IntegerField(null=True, blank=True)
    dr_fisk = models.CharField(max_length=1, blank=True, null= True)
    data_fisk = models.DateTimeField(null=True, blank=True)
    wyroznik = models.CharField(max_length=2, blank=True, null= True)
    data_rej = models.DateTimeField(null=True, blank=True)
    zatwierdzil = models.IntegerField(null=True, blank=True)
    wycenil = models.IntegerField(null=True, blank=True)
    id_kor = models.IntegerField(null=True, blank=True)
    id_odb = models.IntegerField(null=True, blank=True)
    pid = models.IntegerField(null=True, blank=True)
    dni_na_zapl = models.IntegerField(null=True, blank=True)
    zaplacone = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True)
    data_zapl = models.DateField(null=True, blank=True)
    miesiac = models.CharField(max_length=7, blank=True, null= True)
    lp_ksi = models.IntegerField(null=True, blank=True)
    w_walucie = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True)
    waluta = models.CharField(max_length=3, blank=True, null= True)
    kurs = models.DecimalField(null=True, max_digits=16, decimal_places=6, blank=True)
    zak_id = models.IntegerField(null=True, blank=True)
    ciagla = models.CharField(max_length=1, blank=True, null= True)
    oznacz_jpk = models.CharField(max_length=40, blank=True, null= True, db_column="jpk")
        
    class Meta:
        managed= False        
        db_table = 'mag_dok'
        
#     __getattribute__ = model_utils.strip_tail_spaces
            
    def __str__(self):
        return 'Dok[id:{}, id_kli:{}, rodz_te:{}, numer:{}, dzial:{}]'.format(self.id, self.id_kli_id, self.rodz_te, self.numer, self.dzial)
                
    def nazwa_kon(self):
        return self.id_kli.nazwa_kon()
    
    def adres_kon(self):
        return self.id_kli.adres_kon()
    
    def nip_kon(self):
        return self.id_kli.nip()
    
    def nip_kon4(self):
        """
        NIP lun TIN kontrahenta od wersji 4 JPK_VAT bez kodu kraju.
        """
        nip= self.id_kli.nip()
        if nip and re.match('[A-Z][A-Z].*', nip):
            nip= nip[2:]
        return nip
    
    def kraj_tin(self):
        """
        Kraj TIN kontrahenta zagranicznego.
        """
        nip= self.id_kli.nip()
        if nip and re.match('[A-Z][A-Z].*', nip):
            return nip[:2]
        return None    
        
    def nr_fak(self):
        if SysPar._bra():
            # A co w przypadku GDF?
            _nr_fak= self.nr_dok
        else:
            _nr_fak= '{}{:04d}/{}/{:02d}'.format(self.rodz_te.strip(),
                                                 self.numer,
                                                 self.kod_wydz.strip() if self.kod_wydz else '',
                                                 self.data.year % 100 # co w przypadku gdy data jest nieokreślona?
                                                 )
        return _nr_fak
    
    def krajowy(self):
        return True
    
    def rodz_tem(self, rodz_te):
        rt= self.rodz_te.strip()
        return rt == rodz_te if rodz_te else rt
    
    def mag_nr(self):
        return '{} {}/{}/{}'.format(self.symbol, self.numer, self.dzial, self.data.year%100)
    
    def mag_nr2(self):
        return '{} {}/{}/{}'.format(self.symbol2, self.numer2, self.dzial, self.data2.year%100)
        
    def ustal_zak_pz(self):
        """
        Ustalenie numeru faktury do PZ.
        
        Jedna faktura może być powiązana z więcej niż jednym PZ.
        Jeżeli jest więcej niż 1 PZ do faktury to w rejestrze zakupów pozostałe 
        numery PZ wpisuje się w polu na numer PZ w formacie nr/mag lub mag/nr.
        
        Ponieważ teoretycznie dany numer PZ (MAG+numer) może się pojawić w więcej niż
        jednej fakturze (ale z różnych lat) wybierana jest ta faktura, której data zakupu
        różni się najmniej i różnica jest nie większa od 30 (1 miesiąc).
        """
        
        mag= self.jpk.mag()[0:3]
        mags= (mag, mag[1:])
        
        pz= '{} '.format(self.numer)
        mag_pz= ' {}/{}'.format(mag, self.numer)
        pz_mag= ' {}/{}'.format(self.numer, mag)
        mag_pz_rok= ' {}/{}/{}'.format(mag, self.numer, self.data.year % 100)
        pz_mag_rok= ' {}/{}/{}'.format(self.numer, mag, self.data.year % 100)
                
        zakupy= Zak.objects.using(self.jpk.fkdbs('Faktury PZ')).filter(
                    models.Q(mag__in= mags, pz__startswith= pz, dostawca__in= (self.id_kli.nr_kon, '000000')) |
                    models.Q(pz__contains= pz_mag, dostawca__in= (self.id_kli.nr_kon, '000000')) |
                    models.Q(pz__contains= mag_pz, dostawca__in= (self.id_kli.nr_kon, '000000')) |
                    models.Q(pz__contains= pz_mag_rok, dostawca__in= (self.id_kli.nr_kon, '000000')) |
                    models.Q(pz__contains= mag_pz_rok, dostawca__in= (self.id_kli.nr_kon, '000000'))                                         
            )
        
        z= []
        if zakupy:
            for zak in zakupy:
                if abs(self.data-zak.d_zak) < datetime.timedelta(90):
                    z.append((abs(self.data-zak.d_zak), 
                              zak.faktura.strip(),
                              zak.d_wyst))
                
            if z:
                # Sortowanie wg różnicy w dacie pomiędzy PZ i fakturą
                z0= sorted(z, key= itemgetter(0))[0]
                
                self.fa_pz_numer= z0[1]
                self.fa_pz_data= z0[2]
                
        if not zakupy or not z:
            # Jeżeli nie znaleziono faktur lub są zbyt odległe w czasie
            self.fa_pz_numer= None
            self.fa_pz_data= None
     
    def dokad_kod_nazwa(self):
        dokad= Kon.objects.using(self.jpk.fkdbs('Nazwa dzialu')).filter(nr_kon=self.dokad)
        if dokad:
            return '{} {}'.format(self.dokad, dokad[0].nazwa.strip())
        else:
            return self.dokad
    
    def podstawa_korekty(self):
        """
        Przyczyna korekty faktury sprzedaży.
        """
        brak_przyczyny= self.uwagi if SysPar._ichp() else 'KOREKTA'
        
        res= FakRes.objects.using(self.jpk.fkdbs('Przyczyna korekty')).filter(id_dok= self.id)
        if not res: return brak_przyczyny 
        res= res[0]
        return res.przyczyna or brak_przyczyny
    
    def oo(self, w):
        """
        Sprawdzenie czy faktura dotyczy sprzedaży w procedurze odwrotnego obciążenia.
        """
        if SysPar._gig():
            return w.vat == 'OO.'
        else:
            return 'O' in (self.rodzaj or '')
          
    def np(self, w):
        """
        Sprawdzenie czy faktura dotyczy sprzedaży nie podlegającej opodatkowaniu.
        """
        if SysPar._gig():
            return w.vat == 'NO.'
        else:
            return w.vat == 'NP.' and not self.oo(w) 
    
        
    def nr_fa_zaliczkowej(self):
        """
        Ustalenie numerów faktur zaliczkowych.
        """
        zaliczkowe= self.zaliczkowe.all().values_list('numer', flat= True)
        zaliczkowe= ', '.join(x.strip() for x in zaliczkowe)
        return zaliczkowe


    def na_walute(self, kwota_zl):
        """
        Przeliczenie podanej kwoty w zł na wartość w walucie faktury.
        """
        if kwota_zl == self.wart_bru and self.w_walucie:
            # Jeżeli nie ma VAT to wartość w walucie jest wpisana w nagłówku faktury
            # nie ma więc potrzeby przeliczania
            wal= self.w_walucie
        else:
            if self.kurs:
                # Przeliczenie po podanym kursie
                wal= utils.grosze(kwota_zl / self.kurs)
            else:
                # Nie ma kursu nie ma przeliczania
                wal= kwota_zl

        return wal

        
    @staticmethod
    def testowe(*args, **kwargs):
        pola= {
                'stat': 'D', 'korekta': 'D', 'dzial': 'USL', 'symbol': 'FV', 'upust_sp': 0, 'upust_gt': 0, 'sp_zapl': 'P',
                'term_zapl': '2016-09-05', 'data_zam': '2016-07-26', 'zaplata': 0, 'dni_na_zapl': 14, 'zaplacone': 0, 'w_walucie': 0,
                'wart_bru': 0, 'nr_dok': '574552/323/16', 'kod_wydz': '323', 'dr_fisk': None
            }
        
        pola.update(dict(zip(('rodz_te', 'numer', 'id_kli', 'data', 'data_sp', 'data_pod'), args)))
        pola.update(kwargs)
        
        return MagDok.objects.using(utils.test_dbs(pola)).create(**pola)
                  

    def typ_dokumentu(self):
        """
        Oznaczenia dowodu sprzedaży (pole opcjonalne) dla JPK_VAT >= v4
        """
        if not self.oznacz_jpk or len(self.oznacz_jpk) == 0:
            return None
        
        for typ_dokumentu in TYPY_DOKUMENTOW:
            if typ_dokumentu in self.oznacz_jpk:
                return typ_dokumentu

        return None

    def gtu_proc_elementy(self):
        """
        Ustalenie listy elementów GTU i procedur występujących w fakturze.
        Z pola 'oznacz_jpk' usuwany jest ewentualny typ dokumentu, który też jest w tym polu zapisywany.
        Zakłada się, że GTU wprowadzane są do pola oznacz_jpk tylko jako numery cyfrowe 01-13, 
        które na potrzeby generowania JPK zamieniane są na GTU_##
        """
        elements= []

        if not self.oznacz_jpk or len(self.oznacz_jpk) == 0:
            return elements

        # Ustalenie zawartości pola oznacz_jpk

        wybory= re.split('[ ,]', self.oznacz_jpk)

        # Ustalenia występujących w fakturze GTU

        for i in range(0, 13):
            w= '{:02d}'.format(i+1)
            if w in wybory:
                elements.append('GTU_'+w)

        # Ustalenie występujących w fakturze procedur
                
        for p in PROCEDURY:
            if p in wybory:
                elements.append(PROCEDURY_MAP.get(p, p))

        return elements
            
        
class MagWiersz(models.Model):

    id= models.AutoField(primary_key= True)
    id_dok= models.ForeignKey('MagDok', db_column= 'id_dok', blank=True, related_name= 'wiersze')
    id_kart= models.ForeignKey('MagKart', db_column='id_kart', null=True, blank=True)
    il_dysp= models.DecimalField(null=True, max_digits=12, decimal_places=3, blank=True)
    il_real= models.DecimalField(null=True, max_digits=12, decimal_places=3, blank=True)
    cena_real= models.DecimalField(null=True, max_digits=12, decimal_places=2, blank=True)
    cena_ewid= models.DecimalField(null=True, max_digits=12, decimal_places=2, blank=True)
    upust= models.DecimalField(null=True, max_digits=2, decimal_places=0, blank=True, default= 0)
    vat= models.CharField(max_length=3, blank=True)
    zaliczka= models.DecimalField(null=True, max_digits=12, decimal_places=2, blank=True, default= 0)
    znak= models.CharField(max_length=1, blank=True, null= True, default= '-')
    wsk_wyc= models.CharField(max_length=1, blank=True, null= True)
    zlecenie= models.ForeignKey('Zlc', db_column= 'zlecenie', to_field='temat', max_length=10, blank=True, null= True)
    jm= models.CharField(max_length=3, blank=True, null= True)
    sww= models.CharField(max_length=14, blank=True, null= True)
    waga= models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True)
    wartosc= models.DecimalField(null=True, max_digits=12, decimal_places=2, blank=True)
    konto= models.CharField(max_length=20, blank=True, null= True)
    rodzaj= models.CharField(max_length=3, blank=True, null= True)
    
    class Meta:
        managed= False             
        db_table = 'mag_wiersz'
        ordering= ['id']
        
    def __str__(self):
        return 'Wie[id:{}, id_dok:{}, zlecenie:{}]'.format(self.id, self.id_dok_id, self.zlecenie_id)
            
    def __init__(self, *args, **kwargs):
        super(MagWiersz, self).__init__(*args, **kwargs)
        
    def zmien_znak(self):
        """
        Dla dokumentów rozchodowych trzeba zmienić znak pól il_real i wartosc.
        Rozchodowymi są w naszym przypadku FV, WZ, RW, MM.
        Przychodowy tylko PZ.
        
        W samym wierszu nie ma żadnej informacji, która by wystarczyła do 
        ustalenia czy znak trzeba zmienić czy nie. 
        """
        if self.il_real is not None:
            self.il_real= -self.il_real
        if self.wartosc is not None:
            self.wartosc= -self.wartosc
                
    def wartosc_wiersza(self, fak):
        """
        Wartość wiersza faktury.
        """
        self.zmien_znak()
        
        symbol= fak.symbol
#         zlecenie= self.zlecenie
        ilosc= self.il_real
        cena= self.cena_real
        vat= self.vat
        upust= self.upust
        spr_exp= self.cena_ewid
        wsk_wyc= self.wsk_wyc
        waluta= fak.waluta
        kurs= fak.kurs
        
        def _st_vat(vat):
            return decimal.Decimal(float(vat[:2])/100.0 if re.match('[\s\d]\d%', vat) else 0)
         
        if SysPar._bra() and not self.zlecenie: 
            # Dla GDF zlecenie jest zawsze podane, dla pozostałych nigdy
            self.p_netto= self.cena_real
            self.p_vat= self.cena_ewid
            self.p_brutto= self.cena_real + self.cena_ewid
            return
                       
        # Sprzedaż fiskalną sobie darujemy, bo nigdzie nie jest używana
        
        # Wyznaczenie ceny po upuście
        c_net= cena
        c_bru= cena
        cena= utils.grosze(cena * (1-upust/100))

        # Wyznaczenie wartości
        p_netto= utils.grosze(ilosc * cena)

        # Wartość w walucie
        waluta= waluta.strip() if waluta else ''
        
        if wsk_wyc == 'B':
            # Cena była brutto, więc wartość jest brutto
            c_net= utils.grosze(c_bru/(1+_st_vat(vat)))
            p_brutto= p_netto
            # Wyznaczenie wartości netto
            p_netto = utils.grosze(p_brutto/(1+_st_vat(vat)))
            # Wyznaczenie vatu
            p_vat= p_brutto - p_netto
        else:
            c_bru= c_net * (1 + _st_vat(vat))
            # Wyznaczenie vat na podstawie wartości netto
            p_vat= utils.grosze( p_netto * _st_vat(vat) )
            # Wyznaczenie brutto na podstawie netto i vatu
            p_brutto= p_netto + p_vat
    
        self.p_netto= p_netto
        self.p_vat= p_vat
        self.p_brutto= p_brutto
        self.c_net= c_net
        self.c_bru= c_bru

    def daj_opi(self):
        def _len(s):
            return len(s.strip()) if s else 0
        
        self.opia= self.opisy.filter(opis__isnull= False).values_list('opis', flat= True)
        if len(self.opia)>0: return

        try:        
            self.opia= self.zlecenie.tekst.filter(linia__isnull= False).values_list('linia', flat= True)
        except:
            return
        
        if len(self.opia)>0: return

        self.opia= []
                
        if _len(self.zlecenie.tytul) < _len(self.zlecenie.nazwa):
            self.opia= [self.zlecenie.nazwa]
        else:
            if _len(self.zlecenie.tytul[:80])>0:
                self.opia.append(self.zlecenie.tytul[:80])
            if _len(self.zlecenie.tytul[80:])>0:
                self.opia.append(self.zlecenie.tytul[80:])
        
        self.opia.append('/zlec: {}/'.format(self.zlecenie.temat.strip()))

    def towar_kod(self):
        return self.id_kart.indeks

    def towar_nazwa(self):
        return self.id_kart.id_towar.nazwa
    
    def mag_jm(self):
        return self.id_kart.id_towar.jm

    @staticmethod
    def testowe(*args, **kwargs):
        pola= {
            'id_kart_id': 0, 'zaliczka': 0, 'znak': '-', 'jm': 'szt', 'sww': '71.20.1',
            'il_real': -1, 'upust': 0,
            }
        pola.update(dict(zip(('id_dok', 'zlecenie', 'cena_real', 'vat'), args)))
        pola.update(kwargs)
        
        w= MagWiersz.objects.using(utils.test_dbs(pola)).create(**pola)
        
        dok= args[0]
        w.wartosc_wiersza(dok)
        dok.wart_bru += w.p_brutto
        dok.save()
        
        
    
class MagKart(models.Model):
    dzial= models.CharField(max_length= 3)
    data_kart= models.DateField()
    id_towar= models.ForeignKey('MagTowar', db_column= 'id_towar')
    indeks= models.CharField(max_length= 20)
    partia= models.CharField(max_length= 10)
    data_prod= models.DateField()
    data_wazn= models.DateField()
    saldo_il= models.DecimalField(max_digits=12, decimal_places=3)
    saldo_dysp= models.DecimalField(max_digits= 12, decimal_places= 3)
    cena_ewid= models.DecimalField(max_digits= 12, decimal_places=2)
    lokaliza= models.CharField(max_length= 20)

    class Meta:
        managed= False        
        db_table= 'mag_kart'
        ordering= ['id']
        
    @staticmethod
    def testowe(*args, **kwargs):
        pola= {}
        pola.update(dict(zip(('indeks', 'id_towar'), args)))
        pola.update(kwargs)
        
        return MagKart.objects.using(utils.test_dbs(pola)).create(**pola)
    
            

class MagTowar(models.Model):
    dzial= models.CharField(max_length= 3)
    indeks= models.CharField(max_length= 20)
    nazwa= models.CharField(max_length= 50)
    jm= models.CharField(max_length= 3)

    class Meta:
        managed= False        
        db_table= 'mag_towar'
        ordering= ['id']
            
    @staticmethod
    def testowe(*args, **kwargs):
        pola= {'jm': 'szt'}
        pola.update(dict(zip(('indeks', 'nazwa'), args)))
        pola.update(kwargs)
        
        return MagTowar.objects.using(utils.test_dbs(pola)).create(**pola)
    
    
        
class MagDzial(models.Model):
    
    dzial= models.CharField(max_length= 3, primary_key= True)
    fk_kod= models.CharField(max_length= 3, null= True)
    nazwa= models.CharField(max_length= 40, null= True)
    typ_mag= models.CharField(max_length= 1, null= True)
    sprzedaz= models.CharField(max_length= 1, null= True)
    id_kli= models.ForeignKey('Kon', db_column= 'id_kli', null= True)    
    
    class Meta:
        managed= False        
        db_table= 'mag_dzial'
        ordering= ['dzial']
        
    @staticmethod
    def magazyny():
        mag= MagDzial.objects.using(settings.LAST_DBS).filter(typ_mag__in=('M', 'H'), dzial__in=('M17','M50','M15','M25','M10','M33')).values_list('dzial', 'nazwa')
        return ['{} {}'.format(dzial, nazwa.strip()) for dzial, nazwa in mag]
    
    def kod_nazwa(self):
        return '{} {}'.format(self.dzial, self.nazwa.strip())
            


class MagNumer(models.Model):
    
    id= models.AutoField(primary_key= True)
    dzial= models.CharField(max_length= 3)
    symbol= models.CharField(max_length= 2)
    korekta= models.CharField(max_length= 1)
    rok= models.SmallIntegerField()
    numer= models.IntegerField()
    
    class Meta:
        managed= False        
        db_table= '_mag_numer'
        ordering= ['dzial', 'symbol', 'rok']
        
    @staticmethod
    def nastepny(dbs, dzial, symbol, korekta, rok):
        """
        Ustalenie nastepnego numer danego rodzaju dokumentów.
        """
        try:
            nastepny= MagNumer.objects.using(settings.DBS(dbs)).get(
                        dzial= dzial, symbol= symbol, korekta= korekta, rok= rok
                    )
        except MagNumer.DoesNotExist:
            nastepny= MagNumer.objects.using(settings.DBS(dbs)).create(
                        dzial= dzial, symbol= symbol, korekta= korekta, rok= rok, numer= 1
                    )
            
        return nastepny.numer
        
    @staticmethod
    def ostatni(dbs, dzial, symbol, korekta, rok, numer):
        try:
            nastepny= MagNumer.objects.using(settings.DBS(dbs)).get(
                        dzial= dzial, symbol= symbol, korekta= korekta, rok= rok
                    )
        except MagNumer.DoesNotExist:
            nastepny= MagNumer.objects.using(settings.DBS(dbs)).create(
                        dzial= dzial, symbol= symbol, korekta= korekta, rok= rok, numer= 1
                    )

        nastepny.numer= numer
        nastepny.save()      
            


class DefNum(models.Model):
    
    id= models.AutoField(primary_key= True)
    
    rejestr= models.CharField(max_length= 3)
    symbol= models.CharField(max_length= 2)
    rodzaj= models.CharField(max_length= 3)
    korekta= models.CharField(max_length= 1)
    okres= models.CharField(max_length= 7)
    nastepny= models.IntegerField()
    
    class Meta:
        managed= False        
        db_table= '_def_num'
        ordering= ['rejestr', 'symbol', 'rodzaj', 'okres']
        
    @staticmethod
    def ostatni(dbs, rejestr, symbol, rodzaj, korekta, okres, numer):
        try:
            def_num= DefNum.objects.using(settings.DBS(dbs)).get(
                        rejestr= rejestr, symbol= symbol, rodzaj= rodzaj, korekta= korekta, okres= okres
                    )
        except DefNum.DoesNotExist:
            def_num= DefNum.objects.using(settings.DBS(dbs)).create(
                        rejestr= rejestr, symbol= symbol, rodzaj= rodzaj, korekta= korekta, okres= okres, nastepny= 1
                    )

        def_num.nastepny= numer+1
        def_num.save()    



class FapOpi(models.Model):
    
    id= models.AutoField(primary_key= True)
    id_wiersza= models.ForeignKey('MagWiersz', db_column= 'id_wiersza', related_name='opisy', blank= True)
    opis= models.CharField(max_length=70, blank=True)

    class Meta:
        managed= False        
        db_table= 'fap_opi'
        ordering= ['id']
        
        

class Zak(models.Model):
    
    zak_id = models.AutoField(primary_key= True)
    lp = models.IntegerField(null=True, blank=True)
    rodzaj = models.CharField(max_length=3, null= True, blank=True)
    faktura = models.CharField(max_length=30, null= True, blank=True)
    dostawca = models.ForeignKey('Kon', db_column= 'dostawca', to_field= 'nr_kon')
    nip = models.CharField(max_length=20, null= True, blank=True)
    d_nazwa = models.CharField(max_length=240, null= True, blank=True)
    d_zak = models.DateField(null=True, blank=True)
    d_wyst = models.DateField(null=True, blank=True)
    d_otrzym = models.DateField(null=True, blank=True)
    d_przek = models.DateField(null=True, blank=True)
    d_zwrotu = models.DateField(null=True, blank=True)
    wydzial = models.CharField(max_length=10, null= True, blank=True)
    komu = models.CharField(max_length=30, null= True, blank=True)
    termin = models.DateField(null=True, blank=True)
    l_dni = models.IntegerField(null=True, blank=True)
    d_zapl = models.DateField(null=True, blank=True)
    uwagi = models.CharField(max_length=80, null= True, blank=True)
    dow_fak = models.CharField(max_length=10, null= True, blank=True)
    msc_fak = models.CharField(max_length=7, null= True, blank=True)
    lp_fak = models.IntegerField(null=True, blank=True)
    dow_roz = models.CharField(max_length=10, null= True, blank=True)
    msc_roz = models.CharField(max_length=7, null= True, blank=True)
    lp_roz = models.IntegerField(null=True, blank=True)
    d_ksieg = models.DateField(null=True, blank=True)
    
    brutto = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    netto = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    vat = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    zakup = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    clo = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    pimport = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    akcyza = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    manip = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    
    sop_i_net = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    sop_i_vat = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    sop_p_net = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    sop_p_vat = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    
    kos_w_net = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    kos_w_vat = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    
    soz_i_net = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    soz_i_vat = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    soz_p_net = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    soz_p_vat = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    
    bez_i_net = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    bez_i_vat = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    bez_p_net = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    bez_p_vat = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    
    kto_rej = models.IntegerField(null=True, blank=True)
    d_rej = models.DateField(null=True, blank=True, default= datetime.date.today)
    kto = models.IntegerField(null=True, blank=True)
    kiedy = models.DateField(null=True, blank=True, default= datetime.date.today)
    
    pz = models.CharField(max_length=20, null= True, blank=True)
    nr_zwe = models.CharField(max_length=20, null= True, blank=True)
    mag = models.CharField(max_length=5, null= True, blank=True)
    kas_id = models.IntegerField(null=True, blank=True)
    w_walucie = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True)
    waluta = models.CharField(max_length=3, null= True, blank=True)
    kurs = models.DecimalField(null=True, max_digits=16, decimal_places=6, blank=True)
    symbol = models.CharField(max_length=3, null= True, blank=True)
    korekta = models.CharField(max_length=1, null= True, blank=True)
    d_zbil = models.DateField(null=True, blank=True)

    kos_i_net = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    kos_i_vat = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True, default= 0)
    oznacz_jpk = models.CharField(max_length=40, blank=True, null= True, db_column="jpk")
    
    class Meta:
        managed= False        
        db_table = 'zak'

    def __str__(self):
        return 'Zak[id:{}, fak:{}, dostawca:{}, d_dekl:{}, msc_roz:{}'.format(self.zak_id, self.faktura, self.dostawca_id, self.d_ksieg, self.msc_roz)
    
    def gotowkowy(self):
        return (SysPar._ichp() and self.dostawca_id and self.dostawca_id.strip() == '000000') or \
               (SysPar._bra() and self.dostawca_id and self.dostawca_id.strip() == SysPar.get_wartosc('ZAK-KON-GOTOWKOWY', self.jpk))
                        
    def nazwa_kon(self):
        if self.gotowkowy():
            # Kontrahent gotówkowy - dane z rejestru zak
            return self.d_nazwa[:40] if self.d_nazwa else ''
        else:
            return self.dostawca.nazwa_kon()
        
    def adres_kon(self):
        if self.gotowkowy():
            # Kontrahent gotówkowy - dane z rejestru zak            
            return self.d_nazwa[40:] if self.d_nazwa else ''
        else:
            return self.dostawca.adres_kon(jpk= self.jpk)
    
    def nr_id(self):
        if self.gotowkowy():
            # Kontrahent gotówkowy - dane z rejestru zak            
            return self.nip.replace('-', '') if self.nip else ''
        else:        
            return self.dostawca.id if not self.dostawca.idtyp == 'IDENT' else None


    def nr_id4(self):
        if self.gotowkowy():
            # Kontrahent gotówkowy - dane z rejestru zak            
            nip= self.nip.replace('-', '') if self.nip else ''
        else:        
            nip= self.dostawca.id if not self.dostawca.idtyp == 'IDENT' else ''
            
        if nip and re.match('[A-Z][A-Z].*', nip):
            return nip[2:]
        return nip


    def kraj_tin(self):
        """
        Kraj TIN kontrahenta zagranicznego.
        """
        if self.gotowkowy():
            # Kontrahent gotówkowy - dane z rejestru zak            
            nip= self.nip.replace('-', '') if self.nip else ''
        else:        
            nip= self.dostawca.id if not self.dostawca.idtyp == 'IDENT' else ''
        
        if nip and re.match('[A-Z][A-Z].*', nip):
            return nip[:2]
        return None
    

    def dokument_zakupu(self):
        """
        Ustalenie rodzaju dokumentu zakupu (MK, VAT_RR, WEW)
        Maksymalnie tylko jedna z tych wartości powinna wystąpić w polu.
        Informacja zapisana jest w polu "oznacz_jpk"
        """
        if not self.oznacz_jpk: return None
        
        for dz in ('MK', 'VAT_RR', 'WEW'):
            if dz in self.oznacz_jpk:
                return dz

        return None


    def znaczniki(self):
        """
        Ustalenie czy w danym dokumencie zakupu stosowane są określone procedury.
        Zwracana jest lista zawierająca oznaczenia wszystkich procedur/znaczników
        które występują w danym dokumencie.
        Ważna jest kolejność elementów, wymagana przez XSD. 
        """
        
        if not self.oznacz_jpk: return []
        return [p for p in ('MPP', 'IMP') if p in self.oznacz_jpk]
    
        
    @staticmethod
    def testowe(*args, **kwargs):
        pola= {
                'lp': 1,
                'sop_i_net': 0, 'sop_i_vat': 0, 'sop_p_net': 0, 'sop_p_vat': 0,
                'soz_i_net': 0, 'soz_i_vat': 0, 'soz_p_net': 0, 'soz_p_vat': 0,
                'kos_i_net': 0, 'kos_i_vat': 0, 'kos_w_net': 0, 'kos_w_vat': 0,
                'bez_i_net': 0, 'bez_i_vat': 0, 'bez_p_net': 0, 'bez_p_vat': 0,
                'brutto': 0, 'netto': 0, 'vat': 0,           
               }
        
        pola.update(dict(zip(('rodzaj', 'faktura', 'dostawca', 'd_otrzym', 'd_ksieg', 'msc_roz'), args)))
    
        # Policzenie sum netto, vat, brutto faktury na podstawie rozliczenia VAT
        # Wartości mogą być nadpisane przez argumenty kluczowe do funkcji
            
        pola['brutto']= pola['netto']= pola['vat']= 0
        for pole in kwargs:
            if '_net' in pole:
                pola['netto'] += kwargs[pole]
                pola['brutto'] += kwargs[pole]
            if '_vat' in pole:
                pola['vat'] += kwargs[pole]
                pola['brutto'] += kwargs[pole]
        
        # Ewentualne nadpisanie nett, vat, brutto
               
        pola.update(kwargs)
        return Zak.objects.using(utils.test_dbs(pola)).create(**pola)


     
class ZakPoz(models.Model):
    
    zak= models.ForeignKey('Zak', related_name='pozycje')
    id= models.AutoField(primary_key= True)
    p_netto= models.DecimalField(null= False, max_digits= 16, decimal_places=2)
    p_stawka= models.CharField(max_length= 2)
    p_vat= models.DecimalField(max_digits= 16, decimal_places=2)
    p_brutto= models.DecimalField(max_digits= 16, decimal_places=2)
    p_roz= models.CharField(max_length= 3)
    sww= models.CharField(max_length= 10)
    konto= models.CharField(max_length= 20)
    zlecenie= models.CharField(max_length= 10)
    konto5= models.CharField(max_length= 20)
    w_walucie= models.DecimalField(max_digits= 16, decimal_places=2)

    class Meta:
        managed= False        
        db_table= 'zak_poz'
        


class ZakKos(models.Model):

    zak= models.ForeignKey('Zak', related_name='poz_kos')
    poz= models.ForeignKey('ZakPoz')
    id= models.AutoField(primary_key= True)
    kwota= models.DecimalField(null= False, max_digits= 16, decimal_places=2)
    konto= models.CharField(max_length= 20)
    mpk= models.CharField(max_length= 10)
    zlecenie= models.CharField(max_length= 10)
    konto5= models.CharField(max_length= 20)

    class Meta:
        managed= False
        db_table= 'zak_kos'


        
class ZakZrv(models.Model):
    
    zak_id= models.ForeignKey('Zak', db_column= 'zak_id', related_name='wiersze')
    konto4= models.CharField(max_length= 20, null= False)
    zaklad= models.CharField(max_length= 3)
    temat= models.CharField(max_length= 10)
    netto= models.DecimalField(null= False, max_digits=16, decimal_places=2, default= 0)
    stawka= models.CharField(max_length= 2)
    vat= models.DecimalField(null= False, max_digits=16, decimal_places=2, default= 0)
    ip= models.CharField(max_length= 1, null= False)
    zrv= models.CharField(max_length= 3, null= False)
    odlicz= models.DecimalField(null= False, max_digits=6, decimal_places=2, default= 0)        
    
    class Meta:
        managed= False        
        db_table = 'zak_zrv'
        
    def naliczony(self):
        return utils.procent(self.vat, self.odlicz)
            
    def __str__(self):
        return 'ZakZrv[netto: {}, vat:{}, zrv:{}, ip:{}, odlicz:{}'.format(self.netto, self.vat, self.zrv, self.ip, self.odlicz)
            
    @staticmethod
    def testowe(*args, **kwargs):
        pola= {
                'konto4': '40101', 'zaklad': '320', 'temat': '00000006', 'stawka': '23',
               }
        
        pola.update(dict(zip(('zak_id', 'netto', 'vat', 'zrv', 'ip', 'odlicz'), args)))
        pola.update(kwargs)
        return ZakZrv.objects.using(utils.test_dbs(pola)).create(**pola)
    
                
                
class Kon(models.Model):
    
    kon_id = models.AutoField(primary_key= True, db_column= 'kon_id')
    nr_kon = models.CharField(max_length=8, blank=True, unique= True)
    skrot = models.CharField(max_length=40, blank=True, verbose_name= 'Skrót')
    id = models.CharField(max_length=20, blank=True, verbose_name= 'Nip')
    idtyp = models.CharField(max_length=5, blank=True)
    nazwa = models.CharField(max_length=160, blank=True)
    kod = models.CharField(max_length=10, blank=True)
    miejsc = models.CharField(max_length=30, blank=True, verbose_name= 'Miejscowość')
    ulica = models.CharField(max_length=40, blank=True)
    tel = models.CharField(max_length=15, blank=True)
    fax = models.CharField(max_length=15, blank=True)
    tlx = models.CharField(max_length=20, blank=True)
    konto = models.CharField(max_length=40, blank=True)
    bank = models.CharField(max_length=40, blank=True)
    rodzaj = models.CharField(max_length=1, blank=True)
    kto = models.IntegerField(null=True, blank=True)
    kiedy = models.DateField(null=True, blank=True)
    kat_kli = models.CharField(max_length=1, blank=True, default= 'P', verbose_name= 'Status prawny')
    ma_wypis = models.CharField(max_length=1, blank=True)
    data_us = models.DateField(null=True, blank=True)
    platnik = models.ForeignKey('Kon', db_column= 'platnik', null=True, blank=True)
    podpis = models.CharField(max_length=60, blank=True)
    klas_iso = models.CharField(max_length=2, blank=True, default= '29', verbose_name= 'Grupa')
    kraj = models.CharField(max_length=3, blank=True, default= 'PL')
    region = models.CharField(max_length=3, blank=True)
    swift = models.CharField(max_length=20, blank=True)
    b_adres = models.CharField(max_length=40, blank=True)
    e_mail = models.CharField(max_length=40, blank=True)
    www = models.CharField(max_length=40, blank=True)
    term_zap = models.IntegerField(null=True, blank=True)
    id_obcy = models.IntegerField(null=True, blank=True)
    przedplata = models.CharField(max_length=40, blank=True)
    
    class Meta:
        managed= False        
        db_table= 'kon'
        
#     __getattribute__ = model_utils.strip_tail_spaces

    def __str__(self):
        return 'Kon[kon_id:{}, nr_kon:{}, idtyp:{}, id:{}, nazwa:{}, kod:{}, miejsc:{}, ulica:{}]'.format(
                    self.kon_id, self.nr_kon, self.idtyp, self.id, self.nazwa.strip(), 
                    self.kod, self.miejsc.strip(), self.ulica.strip()
                )
    
    def nipue(self):
        return self.idtyp.strip() == 'NIPUE' if self.idtyp else self.idtyp
    
    def not_nipue(self):
        """
        Sprawdzenie czy NIP wygląda na NIPUE ale nie jest tak oznaczony.
        """
        return re.match(r'[A-Z][A-Z]', self.id or '') and not self.idtyp.strip() in ('NIPUE', 'IDENT')
        
    def nazwa_kon(self):
        if not self.nazwa: return self.nazwa
        
        nazwa= ' '.join((utils.ss(self.nazwa[:40]),
                         utils.ss(self.nazwa[40:80]),
                         utils.ss(self.nazwa[80:120]),
                         utils.ss(self.nazwa[120:])))
        return nazwa.strip()

    def adres_kon(self, jpk= None):
        if not self.kod and not self.miejsc and not self.ulica:
            if self.kraj and self.kraj.strip() != 'PL' and jpk:
                return Spo.nazwa_pozycji('KRAJ', self.kraj, jpk)
            return ''
        
        if self.kod:
            kod_miejsc= '{} {}'.format(utils.ss(self.miejsc), utils.ss(self.kod))
        else:
            kod_miejsc= utils.ss(self.miejsc)
            
        return '{}, {}'.format(kod_miejsc, utils.ss(self.ulica))   
    
    def nip(self):
        if self.idtyp == 'NIPUE':
            return self.id if self.id else ''
        if self.idtyp is None or len(self.idtyp.strip())==0 or self.idtyp[:3] == 'NIP':
            return self.id.strip() if self.id else ''
        return ''  
    
    def prefiks_nip(self):
        return self.id[:2] if self.idtyp == 'NIPUE' else ''
    
    def nazwa_miejsc(self):
        return '{}, {}'.format(self.nazwa_kon().strip(), self.miejsc.strip())

    @staticmethod
    def testowe(*args, **kwargs):
        pola= {
               'idtyp': 'NIP', 'kraj': 'PL', 'nazwa': 'FIRMA1', 'kod': '01-920', 'miejsc': 'WARSZAWA', 'ulica': 'KOPERNIKA 1'
            }
        pola.update(dict(zip(('nr_kon', 'id'), args)))
        pola.update(kwargs)
        
        return Kon.objects.using(utils.test_dbs(pola)).create(**pola)



class Zlc(models.Model):
    
    id= models.AutoField(primary_key= True)
    temat= models.CharField(max_length=10, unique= True)
    nazwa = models.CharField(max_length=40, blank=True)
    nr_ref = models.CharField(max_length=6, blank=True)
    nr_wp = models.CharField(max_length=6, blank=True)
    nr_ot = models.CharField(max_length=8, blank=True)
    d_rozp = models.DateField(null=True, blank=True)
    d_zakon = models.DateField(null=True, blank=True)
    dalej = models.CharField(max_length=1, blank=True)
    tu = models.CharField(max_length=1, blank=True)
    sww = models.CharField(max_length=14, blank=True)
    cenaj = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True)
    jm = models.CharField(max_length=3, blank=True)
    ksprz = models.CharField(max_length=20, blank=True)
    kvat = models.CharField(max_length=20, blank=True)
    stawka = models.DecimalField(null=True, max_digits=4, decimal_places=2, blank=True)
    skrot = models.CharField(max_length=30, blank=True)
    upowaz = models.CharField(max_length=1, blank=True)
    d_sprzed = models.DateField(null=True, blank=True)
    waga = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True)
    r1 = models.CharField(max_length=10, blank=True)
    r2 = models.CharField(max_length=10, blank=True)
    r3 = models.CharField(max_length=10, blank=True)
    nr_umowy = models.CharField(max_length=30, blank=True)
    tytul = models.CharField(max_length=240, blank=True)
    uwagi = models.CharField(max_length=80, blank=True)
    lider = models.CharField(max_length=4, blank=True)
    
    class Meta:
        managed= False             
        db_table = 'zlc'
               
#     __getattribute__ = model_utils.strip_tail_spaces
    
    def __str__(self):
        return 'Zlc[id:{}, temat:{}, nazwa:{}]'.format(self.id, self.temat, self.nazwa)

    @staticmethod
    def testowe(*args, **kwargs):
        pola= {
            }
        pola.update(dict(zip(('temat', 'nazwa'), args)))
        pola.update(kwargs)
        
        return Zlc.objects.using(utils.test_dbs(pola)).create(**pola)


class ZlcTxt(models.Model):
    
    zlecenie= models.ForeignKey('Zlc', db_column= 'zlc_id', related_name='tekst')
    linia= models.CharField(max_length= 80)
    
    class Meta:
        managed= False             
        db_table = 'zlc_txt'
            
     
class SrtVat(models.Model):
     
    mkv= models.ForeignKey('SrtMkv', db_column= 'mkv_id', related_name='pozycje')
    rok= models.SmallIntegerField()
    proporcja= models.DecimalField(max_digits=5, decimal_places=2)
    zmiana_p= models.DecimalField(max_digits=5, decimal_places=2)
    vat_do_odlicz= models.DecimalField(max_digits=16, decimal_places=2)
    roznica_vat= models.DecimalField(max_digits=16, decimal_places=2)
    korekta_vat= models.DecimalField(max_digits=16, decimal_places=2)

    class Meta:
        managed= False             
        db_table = 'srt_vat'
        
    @staticmethod
    def testowe(*args, **kwargs):
        pola= {
               'rok': 2016,
            }
        
        pola.update(dict(zip(('mkv', 'korekta_vat'), args)))
        pola.update(kwargs)
        
        return SrtVat.objects.using(utils.test_dbs(pola)).create(**pola)
    
    
            
class SrtMkv(models.Model):
    
    nr_inw= models.CharField(max_length= 20)
    nazwa= models.CharField(max_length= 160)
    nr_faktury= models.CharField(max_length= 40)
    data_ot= models.DateField()
    uwagi= models.CharField(max_length= 100)

    class Meta:
        managed= False             
        db_table = 'srt_mkv'
        
    @staticmethod
    def testowe(*args, **kwargs):
        pola= {
                'nr_faktury': 'FAK1',
                'data_ot': '2016-02-01',
                'uwagi': 'ZMIANA PRZEZNACZENIA',
            }
        
        pola.update(dict(zip(('nr_inw', 'nazwa'), args)))
        pola.update(kwargs)
        
        return SrtMkv.objects.using(utils.test_dbs(pola)).create(**pola)



class SysPar(models.Model):
    
    id= models.AutoField(primary_key= True)
    kod= models.CharField(max_length=30)
    nazwa= models.CharField(max_length=40, blank=True)
    wartosc= models.CharField(max_length=120, blank=True)
    uwagi= models.CharField(max_length=300, blank=True)
    poprawne= models.CharField(max_length=60, blank=True)
    sysid= models.CharField(max_length=1, blank=True)
    
    _params= {}
    
    class Meta:
        managed= False             
        db_table= 'sys_par'
        
    @staticmethod
    def get_wartosc(kod, skad, current= False):
        dbs= skad if isinstance(skad, string_types) else skad.fkdbs('SysPar.get_wartosc {}'.format(kod))
                    
        dbs_params= SysPar._params.get(dbs)
        if not dbs_params:
            dbs_params= {}
            SysPar._params[dbs]= dbs_params
            
        wartosc= dbs_params.get(kod)
        if current or not wartosc:
            if not settings.DATABASES.get(dbs):
                settings.DODAJ_BAZE(dbs)
                            
            wartosc= SysPar.objects.using(dbs).get(kod= kod).wartosc.strip()
            dbs_params[kod]= wartosc
            
        return wartosc 
          
    @staticmethod
    def _firma():
        return settings.FIRMA
     
    @staticmethod
    def _gig():
        return settings.FIRMA == 'gig'
    
    @staticmethod
    def _ichp():
        return settings.FIRMA == 'ichp'  
      
    @staticmethod
    def _bra():
        return settings.FIRMA == 'bra' 
            
    @staticmethod
    def na_liscie(kod, w, jpk):
        for pat in SysPar.get_wartosc(kod, jpk).split():
            pat= pat.replace('*', '.*')
            if pat.startswith('!'):
                if not re.match(pat[1:], w):
                    return True
            else:
                if re.match(pat, w):
                    return True
        return False
    
    @staticmethod
    def testowe(*args, **kwargs):
        pola= {}
        pola.update(dict(zip(('kod', 'wartosc'), args)))
        pola.update(kwargs)
        
        return SysPar.objects.using(utils.test_dbs(pola)).create(**pola)
    
    
class Spo(models.Model):
    
    nr_slo= models.CharField(max_length=5)
    spokod= models.CharField(primary_key= True, max_length=20)
    pnazwa= models.CharField(max_length=40)
    
    class Meta:
        managed= False             
        db_table= 'spo'
    
    @staticmethod
    def nazwa_pozycji(nr_slo, spokod, jpk):
        pnazwa= jpk.slownik(nr_slo).get(spokod)
        return pnazwa.strip() if pnazwa else spokod.strip()        
    
    @staticmethod
    def pozycje(nr_slo, jpk):
        return jpk.slownik(nr_slo)

    @staticmethod
    def testowe(*args, **kwargs):
        pola= {}
        pola.update(dict(zip(('nr_slo', 'spokod', 'pnazwa'), args)))
        pola.update(kwargs)
        
        return Spo.objects.using(utils.test_dbs(pola)).create(**pola)
    
    @staticmethod
    def slo_pozycje(firma, slownik, *args, **kwargs):
        pozycje= Spo.objects.using(settings.DBS(firma)).filter(nr_slo= slownik, **kwargs).order_by('spokod')
        return pozycje



class FakRes(models.Model):
    id_dok= models.OneToOneField('MagDok', primary_key= True, db_column='id_dok', blank= True)
    k_rach= models.CharField(max_length= 20)
    przyczyna= models.CharField(max_length= 120)
    
    class Meta:
        managed= False             
        db_table= 'fak_res'
        
    @staticmethod
    def testowe(*args, **kwargs):
        pola= {}
        pola.update(dict(zip(('id_dok',), args)))        
        pola.update(kwargs)
        
        return FakRes.objects.using(utils.test_dbs(pola)).create(**pola)



class FakZaf(models.Model):
    """
    Numery faktur zaliczkowych do JPK_FA3
    """
    fak_id= models.ForeignKey('MagDok', blank= True, db_column='fak_id', related_name='zaliczkowe')
    data= models.DateField(null= True)
    numer= models.CharField(max_length= 15)
    kwota= models.DecimalField(max_digits= 16, decimal_places= 2)
    
    class Meta:
        managed= False             
        db_table= 'fak_zaf'

        

class KasDow(models.Model):
    
    kpw_id= models.AutoField(primary_key= True)
    kasa= models.CharField(max_length= 2)
    data= models.DateField(null= False)
    rodzaj= models.CharField(max_length= 2, null= True)
    numer= models.IntegerField(null= True)
    stan= models.CharField(max_length=1, null= True)
    nr_pra= models.CharField(max_length=6, null= True)
    nazwa= models.CharField(max_length= 240, null= True)
    lacznie= models.DecimalField(max_digits= 16, decimal_places= 2)
    ksi= models.CharField(max_length= 1, null= True)

    class Meta:
        managed= False             
        db_table= 'kas_dow'



class KasPoz(models.Model):
    
    kpo_id= models.AutoField(primary_key= True)
    kpw= models.ForeignKey('KasDow')
    lp= models.SmallIntegerField(null= True)
    kwota= models.DecimalField(max_digits= 16, decimal_places= 2)
    rach= models.CharField(max_length= 30, null= True)
    opis= models.CharField(max_length= 80, null= True)
    operacja= models.CharField(max_length= 2, null= True)
    konto= models.CharField(max_length= 20, null= True)
    ksi= models.CharField(max_length= 1, null= True)

    class Meta:
        managed= False             
        db_table= 'kas_poz'


class SysDan(models.Model):
    
    dan_id= models.AutoField(primary_key= True)
    
    nr_uzy= models.CharField(max_length= 10)
    modul= models.CharField(max_length= 3)
    funkcja= models.CharField(max_length= 3)
    
    dane1= models.CharField(max_length= 100)
    dane2= models.CharField(max_length= 100)
    dane3= models.CharField(max_length= 100)
    dane4= models.CharField(max_length= 100)
    dane5= models.CharField(max_length= 100)            
    dane6= models.CharField(max_length= 100)
    dane7= models.CharField(max_length= 100)
    dane8= models.CharField(max_length= 100)
    dane9= models.CharField(max_length= 100)
    dane0= models.CharField(max_length= 100)  
        
    class Meta:
        managed= False             
        db_table= 'sys_dan'
        
        
class SysKli(models.Model):
    
    id= models.AutoField(primary_key= True)
    kod= models.CharField(max_length= 10)
    nazwa= models.CharField(max_length=40, blank=True)
    rok= models.SmallIntegerField()
    na_podst= models.CharField(max_length=10)
    
    class Meta:
        managed= False             
        db_table= 'sys_kli'
                