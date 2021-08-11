# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import base64
import datetime
import re

from django.utils.encoding import force_bytes
from django.db import models

from app import model_fields
from app.models import Plik

import logging
logger= logging.getLogger(__name__)

def data(d):
    return d.strftime('%Y-%m-%d') if d else ''

def tekst(t):
    return t or ''

def tt3500(text):
    """
    Podział podanego tekstu na fragmenty o maksymalnej długości 3500.
    Podział robiony jest przy przejściach do nowych linii (\n).
    """
    tt= []
    par= ''
    for p in text.split('\n'):
        if len(par)+len(p)+1 >3500:
            tt.append(par)
            par= p
        else:
            par += '\n'+p
            
    if len(par)>0:
        tt.append(par)
    return tt


class Sprawozdanie(models.Model):
    """
    Ogólne informacje o sprawozdaniu.
    """
    jpk = models.ForeignKey(Plik, on_delete= models.CASCADE)
    
    p0_data_sporzadzenia = models.DateField('Data sporządzenia', default= datetime.date.today)
    
    p1_nazwa_firmy= models.CharField('Pełna nazwa firmy', max_length= 255, null= True)
    p1_kod_kraju= models.CharField("Kod kraju", max_length= 2, default= "PL")
    p1_wojewodztwo= models.CharField('Województwo', max_length= 36, null= True)
    p1_powiat= models.CharField("Powiat", max_length= 36, null= True)
    p1_gmina= models.CharField("Gmina", max_length= 36, null= True)
    p1_miejscowosc= models.CharField("Miejscowość", max_length= 56, null= True)
    p1_kod_pocztowy= models.CharField("Kod pocztowy", max_length= 8, null= True)
    p1_poczta= models.CharField("Poczta", max_length= 56, null= True)
    p1_ulica= models.CharField("Ulica", max_length= 65, null= True, blank= True)
    p1_nr_domu= models.CharField("Nr domu", max_length= 9, null= True)
    p1_nr_lokalu= models.CharField("Nr lokalu", max_length= 10, null= True, blank= True)
    p1_pkd= models.CharField("Przedmiot działalności jednostki", max_length= 100, null= True)
    p1_nip= models.CharField("Identyfikator podatkowy (NIP)", max_length= 10, null= True, blank= True) 
    p1_krs= models.CharField("Numer KRS", max_length= 11, null= True, blank= True)
                    
    p2_data_od= models.DateField('Działa od', null= True)
    p2_data_do= models.DateField('Działa do', null= True)
    p2_data_do_opis= models.CharField('Opis', max_length= 250, null= True)

    p3_data_od= models.DateField("Początek okresu", null= True)
    p3_data_do= models.DateField("Koniec okresu", null= True)
                
    p4_laczne = models.BooleanField('Dane łączne', default= False)
    
    p5_kontynuacja = models.BooleanField('Założenie kontynuacji', default= True)
    p5_brak_zagrozen= models.BooleanField('Bez zagrożenia kontynuacji', default= True)
    p5_opis_zagrozen= model_fields.CompressedTextField('Zawartość pliku JPK', null= True) 
    
    p6_po_polaczeniu= models.BooleanField('Po połączeniu', default= False)
    p6_metoda= model_fields.CompressedTextField('Opis połączenia', null= True)
    
    p7_zasady= model_fields.CompressedTextField('Opis zasad', null= True)
    p7_wycena= model_fields.CompressedTextField('Opis wyceny', null= True)
    p7_wynik= model_fields.CompressedTextField('Opis wyniku', null= True)
    p7_spraw= model_fields.CompressedTextField('Opis sprawozdania', null= True)

    def to_json(self):
        p8= [w.to_json() for w in self.uszczegolowienia.all().order_by('id')]
             
        return {
            'p0_data_sporzadzenia': data(self.p0_data_sporzadzenia),

            'p1_nazwa_firmy': tekst(self.p1_nazwa_firmy),
            'p1_kod_kraju': self.p1_kod_kraju,
            'p1_wojewodztwo': self.p1_wojewodztwo,
            'p1_powiat': self.p1_powiat,
            'p1_gmina': self.p1_gmina,
            'p1_miejscowosc': self.p1_miejscowosc,
            'p1_kod_pocztowy': self.p1_kod_pocztowy,
            'p1_poczta': self.p1_poczta,
            'p1_ulica': self.p1_ulica,
            'p1_nr_domu': self.p1_nr_domu,
            'p1_nr_lokalu': self.p1_nr_lokalu,
            'p1_pkd': self.p1_pkd,
            'p1_nip': self.p1_nip,
            'p1_krs': self.p1_krs,

            'p2_data_od': data(self.p2_data_od),
            'p2_data_do': data(self.p2_data_do),
            'p2_data_do_opis': tekst(self.p2_data_do_opis),

            'p3_data_od': data(self.p3_data_od),
            'p3_data_do': data(self.p3_data_do),

            'p4_laczne': self.p4_laczne,
            
            'p5_kontynuacja': self.p5_kontynuacja,
            'p5_brak_zagrozen': self.p5_brak_zagrozen,
            'p5_opis_zagrozen': tekst(self.p5_opis_zagrozen),
            
            'p6_po_polaczeniu': self.p6_po_polaczeniu,
            'p6_metoda': tekst(self.p6_metoda),
            
            'p7_zasady': tekst(self.p7_zasady),
            'p7_wycena': tekst(self.p7_wycena),
            'p7_wynik': tekst(self.p7_wynik),
            'p7_spraw': tekst(self.p7_spraw),
            
            'p8': p8
        }
        
    def kody_pkd(self):
        return [kod for kod in re.split('\W+', self.p1_pkd or '') if len(kod)==4 or len(kod)==5]
        
    def p7_zasady_tt(self):
        return tt3500(self.p7_zasady)
    def p7_wycena_tt(self):
        return tt3500(self.p7_wycena)
    def p7_wynik_tt(self):
        return tt3500(self.p7_wynik)
    def p7_spraw_tt(self):
        return tt3500(self.p7_spraw)
            
    def p8(self):
        return self.uszczegolowienia.all().order_by('id')
        
    def aktywa(self):
        return Raport.objects.get(sprawozdanie=self, tabela='aktywa')
    
    def pasywa(self):
        return Raport.objects.get(sprawozdanie=self, tabela='pasywa')

    def rzis(self):
        raport= Raport.objects.get(sprawozdanie=self, tabela='rzis')
        pozycje= Pozycja.objects.filter(raport= raport, poziom=1)
        
        return {
                'raport': raport,
                'element': raport.element,
                'pozycje': pozycje,
                'kwoty': False
        }    
    
    def kapital(self):
        try:
            raport= Raport.objects.get(sprawozdanie=self, tabela='kapital')
            pozycje= Pozycja.objects.filter(raport= raport, poziom=1)
        
            return {
                'raport': raport,
                'pozycje': pozycje,
                'kwoty': False
            }
        except Raport.DoesNotExist:
            return {} 
          
    def przeplywy(self):
        try:
            raport= Raport.objects.get(sprawozdanie=self, tabela='przeplywy')
            pozycje= Pozycja.objects.filter(raport= raport, poziom=1)
        
            return {
                    'raport': raport,
                    'element': raport.element,
                    'pozycje': pozycje,
                    'kwoty': False
            }
        except Raport.DoesNotExist:
            return {}
        
    def zalaczniki(self):
        return Dodatkowe.objects.filter(sprawozdanie=self).order_by('id')
    
    def podatek(self):
        return Podatek.objects.filter(sprawozdanie=self).exclude(element__in=('PozycjaUzytkownika', 'Pozostale')).order_by('id')
    
    @staticmethod
    def poprzednie(firma):
        return Sprawozdanie.objects.filter(id__gt=1, jpk__firma__oznaczenie=firma).order_by('-p3_data_do', '-id')

    def nazwa(self):
        jpk= self.jpk
        return jpk.nazwa if jpk.nazwa else "Sprawozdanie za okres {} - {} ({})".format(self.p3_data_od, self.p3_data_do, jpk.id)

    @staticmethod
    def nowe_config(firma):
        """
        Ustalenie konfiguracji dla nowych plików JPK_SF.
        Bierzemy taką samą konfigurację jak w ostatnim istniejącym już sprawozdaniu.
        """
        sprawozdania= Sprawozdanie.objects.filter(id__gt=1, jpk__firma__oznaczenie=firma).order_by('-p3_data_do', '-id')
        if not sprawozdania:
            return {}
        
        spr= sprawozdania[0]
        
        config= {}
        
        try:
            config['wynik']= spr.raporty.get(tabela='rzis').element
        except:
            pass
        
        config['kapital']= Raport.objects.filter(sprawozdanie=spr, tabela='kapital').exists()
        p= Raport.objects.filter(sprawozdanie=spr, tabela='przeplywy')
        if p:
            config['przeplywy']= True
            config['przeplywy_metoda']= p[0].element
        else:
            config['przeplywy']= False
        
        return config 
            
    @staticmethod
    def pierwsze(jpk):
        
        firma= jpk.firma
        
        spr= Sprawozdanie(
            p0_data_sporzadzenia= datetime.date.today(),
            
            p1_nazwa_firmy= firma.nazwa,
            p1_kod_kraju= 'PL',
            p1_wojewodztwo= firma.wojewodztwo,
            p1_powiat= firma.powiat,
            p1_gmina= firma.gmina,
            p1_miejscowosc= firma.miejscowosc,
            p1_kod_pocztowy= firma.kod_pocztowy,
            p1_poczta= firma.poczta,
            p1_ulica= firma.ulica,
            p1_nr_domu= firma.nr_domu,
            p1_nr_lokalu= firma.nr_lokalu,
            p1_pkd= None,
            p1_krs= firma.krs,

            p4_laczne= False,

            p5_kontynuacja= True,
            p5_brak_zagrozen= True,
            p5_opis_zagrozen= None,

            p6_po_polaczeniu= False,
            p6_metoda= None,

            p7_zasady= None,
            p7_wycena= None,
            p7_wynik= None,
            p7_spraw= None
        )
        
        return spr
    
        
class Wprowadzenie(models.Model):
    sprawozdanie= models.ForeignKey(Sprawozdanie, on_delete= models.CASCADE, related_name='uszczegolowienia')
    nazwa = models.CharField(max_length= 250)
    opis = model_fields.CompressedTextField('Opis', null= True)

    def to_json(self):
        return {
            'p8_id': self.id,
            'p8_nazwa': self.nazwa,
            'p8_opis': tekst(self.opis)
        }
        
    def opis_tt(self):
        return tt3500(self.opis)


class Raport(models.Model):
    """
    Informacja o raporcie sprawozdania finansowego.
    """
    
    sprawozdanie= models.ForeignKey(Sprawozdanie, on_delete= models.CASCADE, related_name='raporty')
    tabela= models.CharField('Tabela', max_length= 20, null=True)
    nazwa= models.CharField(max_length= 100)
    element= models.CharField(max_length= 30)
    
    def to_json(self):
        return {
            'nazwa': self.nazwa,
            'element': self.element
        }

    def el(self, element):
        poz= Pozycja.objects.get(raport= self, el=element)
        poziom1= poz.poziom+1
        pozycje= Pozycja.objects.filter(raport= self, klu1__startswith=poz.klu1, poziom=poziom1)
        
        return {
                'raport': self,
                'element': poz.element,
                'el': poz.el,
                'nazwa': poz.nazwa,
                'uszczegolawiajaca': poz.uszczegolawiajaca(),
                'kwota_a': poz.kwota_a, 
                'kwota_b': poz.kwota_b, 
                'pozycje': pozycje,
                'kontener': poz.kontener,
                'kwoty': True
        }


class Pozycja(models.Model):
    """
    Pozycja raportu
    """

    raport= models.ForeignKey(Raport, on_delete= models.CASCADE)
    element= models.CharField(max_length= 30)
    el= models.CharField(max_length= 30)
    nazwa= models.CharField(max_length= 255)
    poziom= models.SmallIntegerField()
    lp= models.SmallIntegerField()
    klu1= models.CharField(max_length= 10)
    klu2= models.CharField(max_length= 1)
    klu3= models.CharField(max_length= 10, null= True)
    wyliczenie= models.CharField(max_length= 10)
    
    kwota_a= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)
    kwota_b= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)
    kwota_b1= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)
    oblicz= models.CharField(max_length= 100, null= True)
    zalezne= models.CharField(max_length=20, null= True)
    kontener= models.BooleanField(default= False)
    wymagana= models.BooleanField(default= False)

    class Meta:
        ordering= ['klu1']
        
    @staticmethod
    def obliczenia_zalezne(pozycje):
        """
        Przekształcenie definicji obliczeń z symboli/kluczy na numery wierszy oraz
        ustalenie zależności symboli/wierszy.
        """

        idx_poz= {poz.klu1:(i, poz) for i, poz in enumerate(pozycje)}
        for i, poz in enumerate(pozycje):
            poz.formula= poz.oblicz
            if poz.oblicz and not '(' in poz.oblicz:
                opel_tab= [];
                for opel in poz.oblicz.split(' '):
                    try:
                        if not opel in ('+', '-', '>', '<') and not '.' in opel:
                            i_poz= idx_poz[opel]
                            i_poz[1].zalezne= '{},{}'.format(i_poz[1].zalezne, i) if i_poz[1].zalezne else i 
                            opel= str(i_poz[0])
                        opel_tab.append(opel)
                    except Exception as e:
                        print('Błąd przy kowersji formuły {}: {}'.format(poz.formula, e))
                poz.oblicz= ' '.join(opel_tab)
        
    def to_json(self):
        return {
            'id': self.id,
            'element': self.element,
            'el': self.el,
            'nazwa': self.nazwa,
            'poziom': self.poziom,
            'lp': self.lp,
            'klu1': self.klu1,
            'wyliczenie': self.wyliczenie,
            'kwota_a': float(self.kwota_a) if self.kwota_a else '',
            'kwota_b': float(self.kwota_b) if self.kwota_b else '',
            'oblicz': self.oblicz, 
            'formula': self.formula,
            'zalezne': self.zalezne,
            'kontener': self.kontener
        }
        
    def uszczegolawiajaca(self):
        rc= self.element.startswith('PozycjaUszczegolawiajaca')
        return rc


class Dodatkowe(models.Model):
    sprawozdanie = models.ForeignKey(Sprawozdanie, on_delete= models.CASCADE)
    opis= model_fields.CompressedTextField('Opis', null= True)
    nazwa= models.CharField(max_length= 55)
    zawartosc= model_fields.CompressedTextField('Zawartość', null= True)

    def to_json(self):
        return {
            'id': self.id,
            'nazwa': self.nazwa,
            'opis': self.opis
        }
        
    def zawartosc_encode(self):
        return base64.b64encode(force_bytes(self.zawartosc))
        

class Podatek(models.Model):
    """
    Rozliczenie różnicy pomiędzy podstawą opodatkowania podatkiem dochodowym a 
    wynikiem finansowym (zyskiem, stratą) brutto
    """
    sprawozdanie= models.ForeignKey(Sprawozdanie, on_delete= models.CASCADE)
    klucz= models.CharField(max_length= 20)
    
    element = models.CharField(max_length= 50)
    nazwa= models.CharField(max_length= 250)
    
    rb_lacznie = models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)
    rb_kapitalowe = models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)
    rb_inne = models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)

    pp_art = models.CharField(max_length= 5, null= True)
    pp_ust = models.CharField(max_length= 5, null= True)
    pp_pkt = models.CharField(max_length= 5, null= True)
    pp_lit = models.CharField(max_length= 5, null= True)
                
    rp_lacznie = models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)
    rp_kapitalowe = models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)
    rp_inne = models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)

    def to_json(self):
        return {
            'id': self.id,
            
            'klucz': self.klucz,
            'klu1': self.klucz,
            'element': self.element,
            'nazwa': self.nazwa,
            
            'kwota_a': float(self.rb_lacznie) if self.rb_lacznie else '',
            'kwota_b': float(self.rb_kapitalowe) if self.rb_kapitalowe else '',
            'kwota_c': float(self.rb_inne) if self.rb_inne else '',
            
            'ppa': self.pp_art,
            'ppb': self.pp_ust,
            'ppc': self.pp_pkt,
            'ppd': self.pp_lit,
            
            '_kwota_a': float(self.rp_lacznie) if self.rp_lacznie else '',
            '_kwota_b': float(self.rp_kapitalowe) if self.rp_kapitalowe else '',
            '_kwota_c': float(self.rp_inne) if self.rp_inne else '',
                        
            'kontener': False
        }
        
    def tpozycja(self):
        return not self.element in ('P_ID_1', 'P_ID_10', 'P_ID_11')
    
    def pozycje_uzytkownika(self):
        return Podatek.objects.filter(sprawozdanie=self.sprawozdanie, 
                                      element= 'PozycjaUzytkownika', 
                                      klucz__startswith=self.klucz).order_by('klucz')
    
    def pozostale(self):
        return Podatek.objects.filter(sprawozdanie=self.sprawozdanie, 
                                      element= 'Pozostale', 
                                      klucz__startswith=self.klucz).order_by('klucz')      
