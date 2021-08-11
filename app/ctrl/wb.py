# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from app.models import Wyciag
from app import ctrl


class Salda(ctrl.CtrlTabeli):
    """
    Salda wyciągu bankowego.
    """
    
    def __init__(self, jpk):
        super(Salda, self).__init__(jpk)
        self.elementy= [
                        Wyciag.objects.filter(data__gte= jpk.dataod, 
                                              data__lte= jpk.datado,
                                              nr_rachunku= jpk.rachunek 
                                              ).order_by('nr_wyciagu', 'data', 'id'),
                       ]
        self.tabela= 'salda'
    
    def sumuj(self, i, element):
        if element.lp == 1:
            self.suma1= element.saldo - element.kwota  # Saldo początkowe
            self.suma2= self.suma1 # Saldo końcowe
            
        self.suma2 += element.kwota # Saldo końcowe

    def uwzglednij(self, i, wyc):
        """
        Faktury sprzedaży
        """
        return True
    
    
class WyciagWiersz(ctrl.CtrlTabeli):
    """
    Kontrola sprzedaży VAT.
    """
    
    def __init__(self, jpk):
        super(WyciagWiersz, self).__init__(jpk)
        self.elementy= [
                        Wyciag.objects.filter(data__gte= jpk.dataod, 
                                              data__lte= jpk.datado,
                                              nr_rachunku= jpk.rachunek 
                                              ).order_by('nr_wyciagu', 'data', 'id'),
                       ]
        self.tabela= 'wyciag'
            
    def sumuj(self, i, element):
        if element.kwota < 0:
            self.suma1 -= element.kwota # Suma obciążeń
        else:
            self.suma2 += element.kwota # Suma uznań

    def uwzglednij(self, i, wyc):
        """
        Faktury sprzedaży
        """
        if not wyc.data:
            wyc.jpk.blad('Wyciag', wyc.lp, 'Brak daty pozycji wyciągu')
        if not wyc.podmiot or len(wyc.podmiot.strip())==0:
            wyc.jpk.blad('Wyciag', wyc.lp, 'Brak nazwy podmiotu')
        if not wyc.opis or len(wyc.opis.strip())==0:
            wyc.jpk.blad('Wyciag', wyc.lp, 'Brak opisu pozycji wyciągu')
        if not wyc.kwota:
            wyc.jpk.blad('Wyciag', wyc.lp, 'Brak kwoty operacji wyciągu')
                                                        
        return True
