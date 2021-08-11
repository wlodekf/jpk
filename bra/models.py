# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import decimal
import re

from django.db import models
from datetime import datetime

from app import model_fields
from app.models import Firma

import logging
logger= logging.getLogger(__name__)

def data(d):
    """
    Parsowanie daty.
    """
    if len(d) == 10:
        if re.match('20\d\d.\d\d.\d\d', d):
            delim= d[4]
            return datetime.strptime(d, '%Y{0}%m{0}%d'.format(delim))
        if re.match('\d\d.\d\d.20\d\d', d):
            delim= d[2]
            return datetime.strptime(d, '%d{0}%m{0}%Y'.format(delim))            
    elif len(d) == 8:
        return datetime.strptime(d, '%Y%m%d')
    else:
        return None        

def kwota(k):
    """
    Parsowanie kwoty.
    """
    k= re.sub('[^0-9,-]', '', k).strip()
    if k == '-': 
        k= '0'
    return decimal.Decimal(k.replace(',', '.') if k else 0)

def znacznik(z):
    """
    Parsowanie znacznika logicznego.
    """
    return z.strip() == 'T'

def znakowe(z):
    return z.strip().replace('“', '"').replace('”', '"') if z else z

def sprzedaz_path(instance, filename):
    return '{}/{}/{}'.format(instance.firma.oznaczenie, datetime.today().year, filename)

d0= lambda: decimal.Decimal(0.0)



class ImportSprzedazy(models.Model):
    """
    Informacja o imporcie sprzedaży.
    """
    
    firma= models.ForeignKey(Firma)
        
    faktury= models.FileField(upload_to= sprzedaz_path)
    wiersze= models.FileField(upload_to= sprzedaz_path, null= True, blank= True)

    do_rejestru= models.BooleanField(default= False)
    rejestr= models.CharField(max_length= 3, null= True, blank= False)
    konto_kon= models.CharField(max_length= 20, null= True, blank= True)
    konto_spr= models.CharField(max_length= 20, null= True, blank= True)
    
    ile_faktur= models.SmallIntegerField(default= 0)
    ile_wierszy= models.SmallIntegerField(default= 0)
    nadpisane= models.SmallIntegerField(default= 0)
    
    ile_23= models.SmallIntegerField(default= 0)
    ile_8= models.SmallIntegerField(default= 0)
    ile_5= models.SmallIntegerField(default= 0)
    ile_0= models.SmallIntegerField(default= 0)
    ile_zw= models.SmallIntegerField(default= 0)
            
    netto_23= models.DecimalField(max_digits= 16, decimal_places= 2, default= d0())
    vat_23= models.DecimalField(max_digits= 16, decimal_places= 2, default= d0())
    netto_8= models.DecimalField(max_digits= 16, decimal_places= 2, default= d0())
    vat_8= models.DecimalField(max_digits= 16, decimal_places= 2, default= d0())
    netto_5= models.DecimalField(max_digits= 16, decimal_places= 2, default= d0())
    vat_5= models.DecimalField(max_digits= 16, decimal_places= 2, default= d0())
    netto_0= models.DecimalField(max_digits= 16, decimal_places= 2, default= d0())
    netto_zw= models.DecimalField(max_digits= 16, decimal_places= 2, default= d0())
    naleznosc= models.DecimalField(max_digits= 16, decimal_places= 2, default= d0())
                            
    od_numeru= models.SmallIntegerField(null= True, blank= True)
    do_numeru= models.SmallIntegerField(null= True, blank= True)
    od_daty= models.DateField(null= True, blank= True)
    do_daty= models.DateField(null= True, blank= True)
    
    kiedy= models.DateTimeField(default= datetime.now)
    kto= models.CharField(max_length= 10)
            
    def netto(self):
        return self.netto_23 + self.netto_8 + self.netto_5 + self.netto_0 + self.netto_zw
    
    def vat(self):
        return self.vat_23 + self.vat_8 + self.vat_5

    def stawek(self):
        ile= 0
        if self.ile_23: ile += 1
        if self.ile_8: ile += 1
        if self.ile_5: ile += 1
        if self.ile_0: ile += 1
        if self.ile_zw: ile += 1
        return ile
    
    def to_json(self):
        """
        Konwersja nagłówka importu do postaci nadającej się do wyświetlenia
        na liście faktur (z grupowaniem pól). 
        """
        return {
            'id': self.id,
            'kiedy': self.kiedy.strftime('%Y-%m-%d %H:%M:%S'),
            'ile_faktur': self.ile_faktur,
            'nadpisane': self.nadpisane,          
            'ile_wierszy': self.ile_wierszy,
            'netto': '{:,.2f}'.format(self.netto_23+ self.netto_8+ self.netto_5+ self.netto_0+ self.netto_zw),
            'vat': '{:,.2f}'.format(self.vat_23+ self.vat_8+ self.vat_5),
            'od_daty': self.od_daty.strftime('%Y-%m-%d'),
            'do_daty': self.do_daty.strftime('%Y-%m-%d'),
            'rejestr': self.rejestr   
        }
        
    def z_fakturami(self):
        return self.faktura_set.all().exists()
        
            

class Faktura(models.Model):
    """
    Nagłówek faktury.
    """
    
    import_sprzedazy= models.ForeignKey(ImportSprzedazy, on_delete= models.CASCADE)
        
    ident= models.CharField(max_length= 30)
    nr_faktury= models.CharField(max_length= 30)
    
    data_wystawienia= models.DateField()
    data_sprzedazy= models.DateField()
    termin_platnosci= models.DateField(null= True)
    
    nazwa_nabywcy= models.CharField(max_length= 160)
    adres_nabywcy= models.CharField(max_length= 160)
    nip_nabywcy= models.CharField(max_length= 20, null= True)
    
    netto_23= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)
    vat_23= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)
    
    netto_8= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)
    vat_8= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)
    
    netto_5= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)
    vat_5= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)
    
    netto_0= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)
    netto_zw= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)
    
    naleznosc= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)

    korygujaca= models.BooleanField(default= False)
    przyczyna_korekty= models.CharField(max_length= 100, null= True)
    nr_korygowanej= models.CharField(max_length= 30, null= True)
    data_korygowanej= models.DateField(null= True)
    
    zaliczkowa= models.BooleanField(default= False)
    odwrotne= models.BooleanField(default= False)
    turystyka= models.BooleanField(default= False)
    
    uwagi= models.CharField(max_length= 160, null= True)

    konto_kon= models.CharField(max_length= 20, null= True) # Konto kontrahenta
    konto_spr= models.CharField(max_length= 20, null= True) # Konto sprzedaży
    
    fak_id= models.IntegerField(null= True) # Referencja do mag_dok jeżeli z zapisem do rejestru sprezdaży

    
    class Meta:
        unique_together= ['import_sprzedazy', 'ident']
        
    def nazwa_nabywcy1(self):
        return self.nazwa_nabywcy.split('/')[0]
    
    def rodzaj(self):
        if self.korygujaca:
            return 'KOREKTA'
        if self.odwrotne:
            return 'ODWROTNE'
        if self.turystyka:
            return 'TURYSTYKA'
        return 'VAT'
    
    @staticmethod
    def from_csv(r, header):
        """
        Utworzenie faktury z danych wczytanych z pliku CSV.
        """
        it= iter(range(30))
        def ri():
            i= next(it)
            return r[i] if i<len(r) else ''
        
        fak= Faktura()
        
        fak.ident= ri()
        fak.nr_faktury= ri()

        fak.data_wystawienia= data(ri())
        fak.data_sprzedazy= data(ri())
        fak.termin_platnosci= data(ri())

        fak.nazwa_nabywcy= znakowe(ri())
        fak.adres_nabywcy= re.sub(' ,', ',', znakowe(ri()))
        fak.nip_nabywcy= re.sub('[- ]', '', ri())
        
        fak.netto_23= kwota(ri())
        fak.vat_23= kwota(ri())
        
        fak.netto_8= kwota(ri())
        fak.vat_8= kwota(ri())
        
        fak.netto_5= kwota(ri())
        fak.vat_5= kwota(ri())
        
        fak.netto_0= kwota(ri())
        # Jeżeli jest błędna kolumna z VAT 0% to ją pomiajamy
        if 'Vat 0%' in header:   
            next(it)
        
        fak.netto_zw= kwota(ri())
        fak.naleznosc= kwota(ri()) 
        
        fak.korygujaca= znacznik(ri())
        fak.przyczyna_korekty= ri()
        fak.nr_korygowanej= ri()
        fak.data_korygowanej= data(ri())
        
        fak.zaliczkowa= znacznik(ri()) 
        fak.odwrotne= znacznik(ri())
        fak.turystyka= znacznik(ri())
        
        fak.uwagi= znakowe(ri())
        
        # Z numerów kont usuwane są - i spacje
        fak.konto_kon= re.sub('[- ]', '', znakowe(ri()))
        fak.konto_spr= re.sub('[- ]', '', znakowe(ri()))
                  
        return fak

    def to_json(self):
        """
        Konwersja nagłówka faktury do postaci nadającej się do wyświetlenia
        na liście faktur (z grupowaniem pól). 
        """
        return {
          'faktura': self.nr_faktury,
          'daty': '<span>{:%Y-%m-%d}</span> <span>{:%Y-%m-%d}</span> <span>{:%Y-%m-%d}</span>'.format(self.data_wystawienia, self.data_sprzedazy, self.termin_platnosci),
          'nip': self.nip_nabywcy,
          'nazwa': self.nazwa_nabywcy1(),
          'adres': self.adres_nabywcy,

          'sprzedaz23': '{}<br/>{}'.format(self.netto_23, self.vat_23),
          'sprzedaz8': '{}<br/>{}'.format(self.netto_8, self.vat_8),
          'sprzedaz5': '{}<br/>{}'.format(self.netto_5, self.vat_5),

          'sprzedaz0zw': '{}<br/>{}'.format(self.netto_0, self.netto_zw),

          'naleznosc': '{}'.format(self.naleznosc),
          'rodzaj': self.rodzaj()   
        }
        
    def nip_poprawny(self):
        if not self.nip_nabywcy: return False
        if len(self.nip_nabywcy)!= 10: return False
        
        waga= [6, 5, 7, 2, 3, 4, 5, 6, 7]
        suma= 0
        for i in range(9):
            suma += int(self.nip_nabywcy[i]) * waga[i]
        reszta= suma % 11
        if reszta == 10 or reszta != int(self.nip_nabywcy[9]):
            return False
        return True
    

class Wiersz(models.Model):
    """
    Nagłówek faktury.
    """
    
    faktura= models.ForeignKey(Faktura, on_delete= models.CASCADE)
    
    ident= models.CharField(max_length= 30)
    nazwa= models.CharField(max_length= 100)
    jm= models.CharField(max_length= 3)
    ilosc= models.DecimalField(null=True, max_digits=12, decimal_places=3)
    
    cena_netto= models.DecimalField(null= True, max_digits=12, decimal_places=2, default= 0)
    cena_brutto= models.DecimalField(null= True, max_digits=12, decimal_places=2, default= 0)    
    upust= models.DecimalField(null= True, max_digits=2, decimal_places=0, blank=True, default= 0)
    netto= models.DecimalField(null= True, max_digits=12, decimal_places=2, default= 0)
    brutto= models.DecimalField(null= True, max_digits=12, decimal_places=2, default= 0)
    stawka= models.CharField(null= True, max_length= 2)

    @staticmethod
    def from_csv(r, header):
        """
        Utworzenie faktury z danych wczytanych z pliku CSV.
        """
        wiersz= Wiersz()
        
        wiersz.ident= r[0]
        wiersz.nazwa= r[1]
        wiersz.jm= r[2]
        wiersz.ilosc= kwota(r[3])
        
        wiersz.cena_netto= kwota(r[4])
        wiersz.cena_brutto= kwota(r[5])
        wiersz.upust= kwota(r[6])
        wiersz.netto= kwota(r[7])
        wiersz.brutto= kwota(r[8])
        
        wiersz.stawka= re.sub('%', '', r[9])

        return wiersz


class Kontrahent(models.Model):
    """
    Nagłówek faktury.
    """
    
    nip = models.CharField(max_length= 30)
    nazwa1 = models.CharField(max_length= 255)


class ImportZakupow(models.Model):
    """
    Informacja o imporcie sprzedaży.
    """
    
    firma= models.ForeignKey(Firma)

    od_daty= models.DateField("Od daty")
    do_daty= models.DateField("Do daty")
            
    ile_faktur= models.SmallIntegerField(default= 0)
    ile_wierszy= models.SmallIntegerField(default= 0)
    ile_kon= models.SmallIntegerField(default= 0)

    ile_nie_fa= models.SmallIntegerField(default= 0)
    ile_lp_roz= models.SmallIntegerField(default= 0)
    ile_podobne= models.SmallIntegerField(default= 0)

    od_zak_id= models.IntegerField(null= True, default= 0)
    do_zak_id= models.IntegerField(null= True, default= 0)
        
    kiedy= models.DateTimeField(default= datetime.now)
    kto= models.CharField(max_length= 10)

    xls= model_fields.CompressedTextField('Plik kontrolny XLS', null= True)
    
    def to_json(self):
        """
        Konwersja nagłówka importu do postaci nadającej się do wyświetlenia
        na liście faktur (z grupowaniem pól). 
        """
        return {
            'id': self.id,
            'kiedy': self.kiedy.strftime('%Y-%m-%d %H:%M:%S'),
            
            'od_daty': self.od_daty.strftime('%Y-%m-%d'),
            'do_daty': self.do_daty.strftime('%Y-%m-%d'),
            
            'ile_faktur': self.ile_faktur,
            'ile_wierszy': self.ile_wierszy,
            'ile_kon': self.ile_kon,
            
            'ile_nie_fa': self.ile_nie_fa,
            'ile_lp_roz': self.ile_lp_roz,
            'ile_podobne': self.ile_podobne,
            
            'od_zak_id': self.od_zak_id,
            'do_zak_id': self.do_zak_id   
        }


class ApiSprzedaz(models.Model):
    """
    Informacja o imporcie sprzedaży.
    """
    
    firma= models.ForeignKey(Firma)

    od_daty= models.DateField("Od daty")
    do_daty= models.DateField("Do daty")
            
    ile_faktur= models.SmallIntegerField(default= 0)
    ile_wierszy= models.SmallIntegerField(default= 0)
    ile_kon= models.SmallIntegerField(default= 0)

    ile_nie_fa= models.SmallIntegerField(default= 0)
    ile_lp_roz= models.SmallIntegerField(default= 0)
    ile_podobne= models.SmallIntegerField(default= 0)

    od_fak_id= models.IntegerField(null= True, default= 0)
    do_fak_id= models.IntegerField(null= True, default= 0)
        
    kiedy= models.DateTimeField(default= datetime.now)
    kto= models.CharField(max_length= 10)

    xls= model_fields.CompressedTextField('Plik kontrolny', null= True)
    
    def to_json(self):
        """
        Konwersja nagłówka importu do postaci nadającej się do wyświetlenia
        na liście faktur (z grupowaniem pól). 
        """
        return {
            'id': self.id,
            'kiedy': self.kiedy.strftime('%Y-%m-%d %H:%M:%S'),
            
            'od_daty': self.od_daty.strftime('%Y-%m-%d'),
            'do_daty': self.do_daty.strftime('%Y-%m-%d'),
            
            'ile_faktur': self.ile_faktur,
            'ile_wierszy': self.ile_wierszy,
            'ile_kon': self.ile_kon,
            
            'ile_nie_fa': self.ile_nie_fa,
            'ile_lp_roz': self.ile_lp_roz,
            'ile_podobne': self.ile_podobne,
            
            'od_fak_id': self.od_fak_id,
            'do_fak_id': self.do_fak_id   
        }