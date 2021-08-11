# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import override_settings

from app.tests import JpkTestCase
from fk import models as fk

import logging
logging.disable(logging.ERROR)


class ZakTests(JpkTestCase):
    
    def test_nazwa_kon(self):
        """
        Nazwa kontrahenta z rejestru kontrahentów.
        """
        
        self.kon= fk.Kon.testowe('999999', '6665554433', nazwa= 'KON NAZWA')
        zak= fk.Zak.testowe('ZKU', 'FAK1', self.kon, '2016-07-02', '2016-07-02', '2016/07', d_nazwa= 'ZAK NAZWA')

        self.assertEqual('KON NAZWA', zak.nazwa_kon())
        
            
    @override_settings(FIRMA='ichp')
    def test_nazwa_kon_gotowkowy(self):
        """
        Brak nazwy kontrahenta gotówkowego (nr_kon 000000) z rejestru zakupów.
        """
        
        self.kon= fk.Kon.testowe('000000', '6665554433', nazwa= 'KON NAZWA')
        zak= fk.Zak.testowe('ZKU', 'FAK1', self.kon, '2016-07-02', '2016-07-02', '2016/07', d_nazwa= 'ZAK NAZWA')

        self.assertEqual('ZAK NAZWA', zak.nazwa_kon())
        
                    
    @override_settings(FIRMA='ichp')
    def test_nazwa_kon_gotowkowy_brak_nazwy(self):
        """
        Brak nazwy kontrahenta gotówkowego (nr_kon 000000) w rejestrze zakupów.
        Powinien być zwracany pusty string.
        """
        
        self.kon= fk.Kon.testowe('000000', '6665554433')
        zak= fk.Zak.testowe('ZKU', 'FAK1', self.kon, '2016-07-02', '2016-07-02', '2016/07', d_nazwa= None)

        self.assertEqual('', zak.nazwa_kon())
        
        
    @override_settings(FIRMA='ichp')
    def test_adres_kon_gotowkowy_brak_nazwy(self):
        """
        Brak nazwy kontrahenta gotówkowego (nr_kon 000000) w rejestrze zakupów.
        Powinien być zwracany pusty string.
        """
        
        self.kon= fk.Kon.testowe('000000', '6665554433')
        zak= fk.Zak.testowe('ZKU', 'FAK1', self.kon, '2016-07-02', '2016-07-02', '2016/07', d_nazwa= None)

        self.assertEqual('', zak.adres_kon())
        
        
    @override_settings(FIRMA='ichp')
    def test_nr_id_gotowkowy_brak_nip(self):
        """
        Brak nip kontrahenta gotówkowego (nr_kon 000000) w rejestrze zakupów.
        Powinien być zwracany pusty string.
        """
        
        self.kon= fk.Kon.testowe('000000', '6665554433')
        zak= fk.Zak.testowe('ZKU', 'FAK1', self.kon, '2016-07-02', '2016-07-02', '2016/07', d_nazwa= None, nip= None)

        self.assertEqual('', zak.nr_id())


