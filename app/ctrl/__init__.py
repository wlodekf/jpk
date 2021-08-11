# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from app.models import Ctrl, Deklaracja, DeklaracjaPoz
from fk.models import SysPar, MagDok
import decimal


class CtrlTabeli(object):
    """
    Kontrola tego co ma być uwzględnione oraz ustalanie podsumowania tabeli.
    """
    
    def __init__(self, jpk):
        self.MAX_LP= None
        self.jpk= jpk
        self.lp= 0
        self.suma1= decimal.Decimal('0.00')
        self.suma2= decimal.Decimal('0.00')
        
        # Sprawdzenie czy istnieje baza danych pliku JPK
        jpk.fkdbs('DBS')        
        
    def generator(self):
        for pozycje in self.elementy:
            for element in pozycje:
                element.jpk= self.jpk
                if self.MAX_LP and self.lp >= self.MAX_LP: return
                
                if self.uwzglednij(pozycje, element):
                    self.lp += 1
                    element.lp= self.lp 
                    self.sumuj(pozycje, element)
                    yield element
            
#             self.uwzglednij(pozycje, None) # ewentualne wywołanie do podsumowania

    def uwzglednij(self, pozycje, element):
        return True
    
    def sumuj(self, pozycje, element):
        pass
                
    def save_ctrl(self):
        ctrl, _ = Ctrl.objects.get_or_create(plik= self.jpk, tabela= self.tabela)
        
        ctrl.wiersze= self.lp
        ctrl.suma1= self.suma1
        ctrl.suma2= self.suma2
        ctrl.save()
        
        self.ctrl= ctrl
        
    def do_deklaracji(self, dok, od_num, do_num, shift= 0):
        """
        Uwzględnienie danego dokumentu w deklaracji.
        Wszystkie niezerowe kwoty K_* są dodawane do odpowiednich pozycji deklaracji (P_*)
        Kwoty z danego dokumentu są dosumowywane do pozycji deklaracji danego JPK pamiętanych 
        w modelu Deklaracja.
        Dopiero po utworzeniu tych pozycji, mogą one być podsumowane i wwpisane do XML.
        Niestety w XML deklaracja jest przed ewidencją.
        """
        if dok.nr_faktury == 'KOREKTA ROCZNA':
            return

        for k in range(od_num, do_num+1):
            kwota= getattr(dok, 'k_{}'.format(k))
            
            if kwota != decimal.Decimal(0.00):
                # Debile zmienili numerację pozycji, np. numery pozycji 43-48 ze starszych wersji
                # teraz mają numery 40-45
                numer= k + shift
                # szukamy w Deklaracja pozycji, w której możemy zapisać daną kwotę 
                dek= Deklaracja.objects.filter(jpk= self.jpk, numer= numer)
                if not dek:
                    dek= DeklaracjaPoz.pozycja_deklaracji(self.jpk, numer)
                else:
                    dek= dek[0]
                dek.kwota += kwota
                dek.save()
                
                
        
class CtrlTabeliMag(CtrlTabeli):
    """
    Kontrola sprzedaży VAT.
    """
    
    def __init__(self, jpk, symbole, zmien_znak):
        super(CtrlTabeliMag, self).__init__(jpk)
        
        self.elementy= [
                        MagDok.objects.using(jpk.fkdbs('Mag')).filter(
                                              data__gte= jpk.dataod, 
                                              data__lte= jpk.datado,
                                              dzial= jpk.magazyn[:3],
                                              stat= 'D'
                                              )
                                    .filter(**symbole)
                                    .order_by('data', 'id'),   
                        ]     

        self.zmien_znak= zmien_znak
        self.tabela= self.__class__.__name__.lower()
        
        self.dokumenty= []
        
        # cachowanie dokumentów bo i tak będą dwa przebiegi
        for d in self.generator():
            pass
                    
    def sumuj(self, pozycje, element):
        self.suma1 += element.mag_wartosc

    def uwzglednij(self, pozycje, dok):
        """
        Dokument magazynowy
        """
        super(CtrlTabeliMag, self).uwzglednij(pozycje, dok)
        
        self.dokumenty.append(dok)
        
        dok.wiersze_all= []
        dok.mag_wartosc= decimal.Decimal(0)
        for w in dok.wiersze.all():
            if self.zmien_znak:
                w.zmien_znak()
            dok.mag_wartosc += w.wartosc
            dok.wiersze_all.append(w)            
            
        return True



class Pozycje(object):
    
    def __init__(self, pozycje):
        self.pozycje= pozycje
        
    def __iter__(self):
        return self.pozycje.__iter__()


