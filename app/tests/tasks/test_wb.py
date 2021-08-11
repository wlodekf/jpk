# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from app import tasks
from app.models import Plik, Wyciag
import datetime, decimal
import re
from .. import JpkTestCase
import logging

logging.disable(logging.CRITICAL)

        
class WbTestCase(JpkTestCase):

    def setUp(self):
        self.jpk= Plik.objects.create(kod= 'JPK_WB',
                                      dataod= datetime.date(2016,7,1),
                                      datado= datetime.date(2016,7,31),
                                      rachunek= 'PL34105012141000000700407299',
                                      utworzony_user= 'test')

    def get_jpk_xml(self):
        self.jpk= tasks.JpkTask(self.jpk.id).run()
        
        self.assertXmlDocument(self.jpk.xml.encode('utf-8'))
        
        # Dla ułatwienia dalszego sprawdzania wywalany jest domyślny namespace
        return self.assertXmlDocument(re.sub('xmlns="http://jpk.mf.gov.pl/wzor/2016/03/09/03092/"', '', self.jpk.xml).encode('utf-8'))

    def test_wb(self):
        
        # Przygotowanie kontekstu 
        
        wb= Wyciag.testowe('PL34105012141000000700407299', 1, '2016-07-02', 
                           100.00, 100.00, 
                           'DOSTAWCA', 'ZAPŁATA')
                
        # Utworzenie XML
                
        root= self.get_jpk_xml()
        
        # Sprawdzenie poprawności JPK
        
        # Sprawdzenie istnienia elementów podrzednych
        
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1', 
                                      './NumerRachunku', './Salda',
                                      './WyciagWiersz', './WyciagCtrl'))
        
        nr_rachunku= self.assertXpath(root, './NumerRachunku')
        self.assertXmlEquivalentOutputs(self.node_xml(nr_rachunku), """
            <NumerRachunku>PL34105012141000000700407299</NumerRachunku>
        """)

        salda= self.assertXpath(root, './Salda')
        self.assertXmlEquivalentOutputs(self.node_xml(salda), """
            <Salda>
                <SaldoPoczatkowe>0.00</SaldoPoczatkowe>
                <SaldoKoncowe>100.00</SaldoKoncowe>
            </Salda>
        """)
        
        wyciag_wiersz= self.assertXpath(root, './WyciagWiersz')
        self.assertXmlEquivalentOutputs(self.node_xml(wyciag_wiersz), """
            <WyciagWiersz typ="G">
                <NumerWiersza>1</NumerWiersza>
                <DataOperacji>2016-07-02</DataOperacji>
                <NazwaPodmiotu>DOSTAWCA</NazwaPodmiotu>
                <OpisOperacji>ZAPŁATA</OpisOperacji>
                <KwotaOperacji>100.00</KwotaOperacji>
                <SaldoOperacji>100.00</SaldoOperacji>
            </WyciagWiersz>
        """)
        
        wyciag_ctrl= self.assertXpath(root, './WyciagCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(wyciag_ctrl), """
            <WyciagCtrl>
                <LiczbaWierszy>1</LiczbaWierszy>
                <SumaObciazen>0.00</SumaObciazen>
                <SumaUznan>100.00</SumaUznan>    
            </WyciagCtrl>
        """)
        
