# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import decimal
import re

from django.db import connections

from app import ctrl
from collections import OrderedDict

from app.models import Plik
from sf.models import Sprawozdanie, Raport, Pozycja, Podatek
        
"""
Sprawozdanie tworzone jest na podstawie innego sprawozdania (poprzedniego okresu).
Tworzenie polega na skopiowaniu pozycji raportów z przeniesieniem kwot bieżących
do poprzednich i wyzerowaniu kwot bieżących.
"""

class Wprowadzenie(ctrl.CtrlTabeli):
    """
    Kontrola zestawienie obrotów i sald.
    """
    
    def __init__(self, jpk, config):
        super(Wprowadzenie, self).__init__(jpk)
        
        self.elementy= []
        self.tabela= 'wprowadz'
        self.config= config
        
        # Tak aby przy tworzeniu pozostałych Ctrl Sprawozdanie już istniało 
        # bo kolejność nie jest znana

        spr= None
        try:   
            pop_spr_id= config.get('poprzednie')     
            if pop_spr_id:
                spr= Sprawozdanie.objects.get(id=pop_spr_id)
        except Sprawozdanie.DoesNotExist:
            pass
        
        if not spr:
            spr= Sprawozdanie.pierwsze(jpk)
        
        uszczegolowienia= list(spr.uszczegolowienia.all().order_by('id'))
        
        spr.pk= None
        spr.jpk= jpk
        spr.p0_data_sporzadzenia= datetime.date.today()
        spr.p3_data_od= jpk.dataod
        spr.p3_data_do= jpk.datado
        
        spr.save()
        
        # Skopiowanie uszczegółowień
        for wpr in uszczegolowienia: 
            wpr.pk= None
            wpr.sprawozdanie= spr
            wpr.save()

    def utworz(self):
        pass
    
    def sumuj(self, i, element):
        pass
    
    def uwzglednij(self, i, ana):
        return True       


class RaportSprawozdania(ctrl.CtrlTabeli):
    """
    Jeżeli danego raportu nie ma być w sprawozdaniu to konstruktor nie będzie wywołany.
    """
    
    def __init__(self, jpk, tabela, config):
        super(RaportSprawozdania, self).__init__(jpk)
        
        self.elementy= []
        self.tabela= tabela
        self.config= config
        
        self.ten_cursor= connections[self.jpk.fkdbs('Obroty')].cursor()        
        self.pop_cursor= connections[self.jpk.fkdbs_1('Obroty')].cursor()         
        
    def raport_element(self):
        ELEMENTY= {'aktywa': 'Aktywa',
                   'pasywa': 'Pasywa',
                   'rzis': 'RZiS',
                   'kapital': 'ZestZmianWKapitale',
                   'przeplywy': 'Przeplywy'
                   }
        element= ELEMENTY.get(self.tabela)
        if self.tabela == 'rzis':
            element= self.config['wynik']
        if self.tabela == 'przeplywy':
            element= self.config['przeplywy_metoda']
        return element
        
    def utworz(self):
        # To sprawozdanie
        sprawozdanie= Sprawozdanie.objects.get(jpk= self.jpk)
        
        # Raport tworzony jest na podstawie wybranego sprawozdanie odniesienia
        self.pop_spraw_id= int(self.config.get('poprzednie', 1))
        element= self.raport_element()
                
        try:
            self.raport= Raport.objects.get(sprawozdanie_id= self.pop_spraw_id, tabela= self.tabela, element=element)
        except Raport.DoesNotExist:
            # Jeżeli nie znaleziono odpowiedniego raportu z poprzedniego okresu/sprawozdania
            # to bierzemy domyślny szablon
            self.pop_spraw_id= 1
            self.raport= Raport.objects.get(sprawozdanie_id= self.pop_spraw_id, tabela= self.tabela, element=element)


        if self.pop_spraw_id > 1:        
            try:
                pop_jpk= Plik.objects.get(sprawozdanie__id= self.pop_spraw_id)
                pop_ctrl= pop_jpk.get_ctrl(self.tabela)
                if self.config['kopia']:
                    self.suma1= pop_ctrl.suma1
                    self.suma2= pop_ctrl.suma2
                else:
                    self.suma2= pop_ctrl.suma1
            except:
                pass
            
            
        # Pozycje raportu poprzedniego okresu
        self.elementy= [Pozycja.objects.filter(raport=self.raport)]
        
        self.raport.id= None
        self.raport.sprawozdanie= sprawozdanie
        self.raport.save()
        
        self.sprawozdanie= sprawozdanie
        
        list(self.generator())

        self.obliczenia()
            
    def sumuj(self, i, element):
        pass
    
    def uwzglednij(self, i, poz):
        """
        Skopiowanie pozycji z raportu odniesienia do bieżącego raportu,
        ewentualne ustalenie wartości pozycji na podstawie obrotów.
        """
        poz.id= None
        poz.raport= self.raport
        
        if not self.config['kopia']:
            if self.pop_spraw_id == 1:
                # Jeżeli nie ma poprzedniego raportu ustalamy obroty
                poz.kwota_b= self.obroty(poz, False)
            else: 
                poz.kwota_b= poz.kwota_a
                
            poz.kwota_a= self.obroty(poz, True)
            poz.kwota_b1= 0
            
        poz.save()
        
        return True
    
    def obroty(self, poz, biezacy):
        """
        Ustalenie wartości pozycji raportu na podstawie obrotów podanych kont.
        """
        if not poz.oblicz or not '(' in poz.oblicz:
            return 0
        
#         print('obroty {} {}: {}'.format(self.raport.tabela, poz.klu1, poz.oblicz))
        
        m= re.split("([\+\-])", poz.oblicz)
        op = '+'
        wynik= decimal.Decimal(0)
        
        for x in m:
            x= x.strip()
            if not x or len(x)==0:
                continue
            
            if x in ('+', '-'):
                op= x
            else:
                if not '(' in x:
                    try:
                        if op == '+':
                            wynik += decimal.Decimal(x)
                        if op == '-':
                            wynik -= decimal.Decimal(x)
                    except:
                        pass
                    
                    continue
                    
                w= re.split('[\(\)]', x)
                
                proc= w[0]
                konta= w[1]
                
                rc, wynik= self.referencja(proc, konta, wynik, biezacy)
                if rc:
                    continue
                
                if proc == 'sw':
                    strona= 'W'
                elif proc == 'sm':
                    strona= 'M'
                else:
                    strona= 'S'

                cursor= self.ten_cursor if biezacy else self.pop_cursor                
                cursor.callproc('saldo', [konta, strona, 0, 12])
                results= cursor.fetchall()
                
#                 print(konta, strona, op, results[0][0])
                
                if op == '+':
                    wynik += results[0][0] or 0
                if op == '-':
                    wynik -= results[0][0] or 0
                    
        return wynik  
    
    def referencja(self, proc, konta, wynik, biezacy):
        """
        Pobranie określonej wartości z innego raportu.
        Np. wyniku netto rzis(O;L) do bilansu/pasywów.
        Referencję określa się w postaci raport(klucz), 
        gdzie raport jest oznaczeniem (aktualnie pole tabela) daportu
        a klucz to pole klu1.
        """
        if proc in ('aktywa', 'pasywa', 'rzis', 'kapital', 'przeplywy'): 
            print('referencja', proc, konta, wynik, biezacy)
            try:
                # Ustalenie raportu, z którego należy pobrać wartość
                rzis= Raport.objects.get(sprawozdanie=self.sprawozdanie, tabela=proc)

                # Pobranie wartości pozycji

                # W przypadku gdy dane mają być pobrane z raportu, który ma różne wersje
                # należy wpisać klucze oddzielone średnikiem, tak aby pierwsza
                # wartość istniejąca była brana pod uwagę
                # np. rzis(O;L)

                for konta in konta.split(';'):
                    print('konta', konta)
                    p= Pozycja.objects.filter(raport=rzis, klu1=konta)
                    if p:
                        p= p[0]
                        print('p', p.kwota_a, p.kwota_b)
                        wynik += (p.kwota_a or 0) if biezacy else (p.kwota_b or 0)
                        break
            except:
                pass
            
            return True, wynik
        return False, wynik
                        
    def obliczenia(self):
        """
        Wykonanie obliczeń dla wszystkich pozycji w celu posumowania
        pozycji obliczanych.
        """
        
#         print('raport.obliczenia {}'.format(self.raport.tabela))
        pozycje= Pozycja.objects.filter(raport=self.raport)
        Pozycja.obliczenia_zalezne(pozycje)
        
        self.pozycje= list(pozycje)
        
        for poz in pozycje:
            
            if poz.zalezne or poz.zalezne == 0:
                self.wyrazenie(poz.zalezne, True)
                
            if poz.zalezne or poz.zalezne == 0:
                self.wyrazenie(poz.zalezne, False)
        
        PODSUM= {'Aktywa': 'Aktywa',
             'Pasywa': 'Pasywa',
             'RZiSKalk': 'O',
             'RZiSPor': 'L',
             'ZestZmianWKapitale': 'III',
             'PrzeplywyPosr': 'G',
             'PrzeplywyBezp': 'G'
        }
                    
        sum_el= PODSUM.get(self.raport.element)
        for pozycja in pozycje:
            pozycja.save(update_fields=['kwota_a', 'kwota_b'])
                
            if sum_el == pozycja.el:
                self.suma1= pozycja.kwota_a
                self.suma2= pozycja.kwota_b
            
    def wyrazenie(self, zalezne, ten_okres):
        """
        Obliczenie wartości wiersza "zalezne" w kolumnie "ten_okres".
        """
        if not zalezne and zalezne != 0:
            return

        zalezne= str(zalezne)
        for zal in zalezne.split(','):
            zal= int(zal)
            p= self.pozycje[zal]
    
            if ten_okres:
                p.kwota_a= self.obliczenie(p.oblicz, ten_okres)
            else:
                p.kwota_b= self.obliczenie(p.oblicz, ten_okres)
    
            self.wyrazenie(p.zalezne, ten_okres);
        
    def obliczenie(self, oblicz, ten_okres):
        """
        Obliczenie wyrażenia podanego w "oblicz" w kolumnie "ten_okres". 
        """
        if not oblicz or '(' in oblicz:
            return 0

        wynik= decimal.Decimal(0)

        op= '+'
        m= re.split("(\s*[\+\-\>\<]\s*)", oblicz)
        
        for x in m:
            try:
                x= x.strip()
                if x in ['+', '-', '>', '<']:
                    op= x
                else:
                    if not '.' in x:
                        poz= self.pozycje[int(x)]
                        x= decimal.Decimal(poz.kwota_a if ten_okres else poz.kwota_b)

                    x= decimal.Decimal(x)

                    if op == '+': wynik += x
                    elif op == '-': wynik -= x
                    elif op == '>': wynik= wynik if wynik > x else 0
                    elif op == '<': wynik= wynik if wynik < x else 0 
            except:
                pass
                
        return wynik
             
    def ustal_obroty(self, raport):
        lspr= Sprawozdanie.objects.filter(jpk__firma= self.jpk.firma).count()
        self.raport= raport
        
        for poz in Pozycja.objects.filter(raport=self.raport):
            if poz.oblicz and '(' in poz.oblicz:
                poz.kwota_a= self.obroty(poz, True)
                if lspr == 1:
                    poz.kwota_b= self.obroty(poz, False)
                poz.save(update_fields=['kwota_a', 'kwota_b'])
            
        self.obliczenia()
           
    def przelicz(self, tabela):
        self.sprawozdanie= Sprawozdanie.objects.get(jpk= self.jpk)
        try:
            self.raport= Raport.objects.get(sprawozdanie=self.sprawozdanie, tabela=tabela)
        except:
            return False
        
        self.ustal_obroty(self.raport)
        
        self.obliczenia()
        return True
        
        
class Aktywa(RaportSprawozdania):
    def __init__(self, jpk, config):
        super(Aktywa, self).__init__(jpk, 'aktywa', config)
        
class Pasywa(RaportSprawozdania):
    def __init__(self, jpk, config):
        super(Pasywa, self).__init__(jpk, 'pasywa', config)

class RZiS(RaportSprawozdania):
    def __init__(self, jpk, config):
        super(RZiS, self).__init__(jpk, 'rzis', config)

class Kapital(RaportSprawozdania):
    def __init__(self, jpk, config):
        super(Kapital, self).__init__(jpk, 'kapital', config)
        
class Przeplywy(RaportSprawozdania):
    def __init__(self, jpk, config):
        super(Przeplywy, self).__init__(jpk, 'przeplywy', config)
        
  
class PodatekCtrl(ctrl.CtrlTabeli):
    """
    Kontrola zestawienie obrotów i sald.
    """
    
    def __init__(self, jpk, config):
        super(PodatekCtrl, self).__init__(jpk)
        
        self.elementy= []
        self.tabela= 'podatek'
        self.config= config

    def utworz(self):
        self.sprawozdanie= Sprawozdanie.objects.get(jpk= self.jpk)
        
        # Ustalenie sprawozdania  
        pop_spraw_id= int(self.config.get('poprzednie', 1))
        
        if pop_spraw_id > 1:        
            try:
                pop_jpk= Plik.objects.get(sprawozdanie__id= pop_spraw_id)
                pop_ctrl= pop_jpk.get_ctrl(self.tabela)
                if self.config['kopia']:
                    self.suma1= pop_ctrl.suma1
                    self.suma2= pop_ctrl.suma2
                else:
                    self.suma2= pop_ctrl.suma1
            except:
                pass
            
            
        # Pozycje raportu poprzedniego okresu
        self.elementy= [Podatek.objects.filter(sprawozdanie=pop_spraw_id).order_by('klucz')]
        list(self.generator())

    def sumuj(self, i, element):
        pass
    
    def uwzglednij(self, i, poz):
        poz.id= None
        poz.sprawozdanie= self.sprawozdanie
        
        if not self.config['kopia']:
            poz.rp_lacznie= poz.rb_lacznie
            poz.rp_kapitalowe= poz.rb_kapitalowe
            poz.rp_inne= poz.rb_inne
            
            poz.rb_lacznie= 0
            poz.rb_kapitalowe= 0
            poz.rb_inne= 0
            
        poz.save()
        
        return True 
    

class Dodatkowe(ctrl.CtrlTabeli):
    """
    Kontrola zestawienie obrotów i sald.
    """
    
    def __init__(self, jpk, config):
        super(Dodatkowe, self).__init__(jpk)
        
        self.elementy= []
        self.tabela= 'dodatkowe'
        self.config= config

    def utworz(self):
        pass

    def sumuj(self, i, element):
        pass
    
    def uwzglednij(self, i, ana):
        return True   


def obliczenia(jpk, raport, ctrl):
    """
    Ustalenie obrotów podanego raportu i 
    przeliczenie wartości wszystkich raportów (ze względu na możliwe powiązania)
    """
    
    RAPORTY= OrderedDict([
        ('rzis', RZiS),
        ('aktywa', Aktywa),
        ('pasywa', Pasywa),
        ('kapital', Kapital),
        ('przeplywy', Przeplywy)
        ]
    )

    for tabela, ctrl in RAPORTY.items():
        rap= ctrl(jpk, {})
        if rap.przelicz(tabela):
            rap.save_ctrl()

