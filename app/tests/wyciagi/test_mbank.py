# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import decimal, os

from .. import JpkTestCase
from app import wyciagi
from app.models import Wyciag

import logging
logging.disable(logging.ERROR)

                
class MbankImportTestCase(JpkTestCase):

    @staticmethod
    def mbank_sta(nazwa):
        return os.path.join(os.path.dirname(__file__), '{}.sta'.format(nazwa))
    
    def setUp(self):
        pass
    
    def test_import_mbank(self):
        
        wyciagi.importuj_mbank(open(self.mbank_sta('mbank'), 'rb'))

        w= Wyciag.objects.all()[0]
        
        self.assertEqual('PL05114010780000301812001001', w.nr_rachunku)
        self.assertEqual(98, w.nr_wyciagu)
        self.assertEqual('PLN', w.waluta)
        self.assertEqual('760', w.kod)
        self.assertEqual('2016-05-23', str(w.data))
        self.assertEqual(decimal.Decimal('736.77'), w.kwota)
        self.assertEqual('FRA 5722664/331/16', w.opis)
        self.assertEqual('INSTYTUT BADAWCZY DRÓG I MOSTÓW ŻMI GRÓD-WĘGLEWO 55-140 ŻMIGRÓDWĘGLEWO', w.podmiot)
        self.assertEqual(decimal.Decimal('736.77'), w.saldo)
        
        self.assertEqual(1, Wyciag.objects.all().count())

    def test_ostatnia_operacja_w_pliku(self):
        """
        Uwzględnienie ostatniej operacji w pliku mt940.
        """
        wyciagi.importuj_mbank(open(self.mbank_sta('mbank_end'), 'rb'))

        self.assertEqual(1, Wyciag.objects.all().count())
