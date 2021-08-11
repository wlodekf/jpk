# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import decimal, os

from .. import JpkTestCase
from app import wyciagi
from app.models import Wyciag

import logging
logging.disable(logging.ERROR)

                
class IngImportTestCase(JpkTestCase):

    ING_STA_FILENAME= os.path.join(os.path.dirname(__file__), 'ing.sta')
    
    def setUp(self):
        self.ing_sta= open(self.ING_STA_FILENAME, 'rb')
        
    def test_import_ing(self):
        
        wyciagi.importuj_ing(self.ing_sta)

        w= Wyciag.objects.all()[0]

        self.assertEqual('PL62105012141000002227500978', w.nr_rachunku)
        self.assertEqual(103, w.nr_wyciagu)
        self.assertEqual('PLN', w.waluta)
        self.assertEqual('S034', w.kod)
        self.assertEqual('2016-05-19', str(w.data))
        self.assertEqual(decimal.Decimal('1000.00'), w.kwota)
        self.assertEqual('III semestr studiówdoktoranckichI rata i IV rataRoman Mańka', w.opis)
        self.assertEqual('RZEPKA KATARZYNA ALEJA MŁODYCH 10/16 41-106 SIEMIANOWICE ŚLĄSKIE', w.podmiot)
        self.assertEqual(decimal.Decimal('31813.60'), w.saldo)
        
        self.assertEqual(1, Wyciag.objects.all().count())
