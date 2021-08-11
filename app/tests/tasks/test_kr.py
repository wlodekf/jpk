# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from app import tasks
from app.models import Plik
import datetime, decimal
import re
from .. import JpkTestCase
import logging
from django.test import override_settings
from fk import models as fk

logging.disable(logging.CRITICAL)



class KrTestCase(JpkTestCase):

    def setUp(self):
        self.jpk= Plik.objects.create(kod= 'JPK_KR',
                                      dataod= datetime.date(2016,7,1),
                                      datado= datetime.date(2016,7,31),
                                      utworzony_user= 'test')
        
        fk.SysPar.testowe('DZI', '2016/07')
        
                
    def get_jpk_xml(self):
        self.jpk= tasks.JpkTask(self.jpk.id).run()
        
        self.assertXmlDocument(self.jpk.xml.encode('utf-8'))
        
        # Dla ułatwienia dalszego sprawdzania wywalany jest domyślny namespace
        return self.assertXmlDocument(re.sub('xmlns="http://jpk.mf.gov.pl/wzor/2016/03/09/03091/"', '', self.jpk.xml).encode('utf-8'))


    @override_settings(FIRMA='gig')                
    def test_jedno_konto(self):
        
        # Przygotowanie kontekstu 
        
        # Prawidłowe księgowanie w okresie raportu
        ana= fk.Ana.testowe('201330001', 'KONTRAHENT', wn_0= 100.00, wn_7=100.00, ma_7= 300.21)
        syn= fk.Syn.testowe('201', 'ROZRACHUNKI Z KONTRAHENTAMI')
        kto= fk.Uzy.testowe('ktos')
        dow= fk.Dow.testowe('55001/07', '2016/07', '2016-07-10', 1, 100.00, 
                            kto= kto, d_operacji= '2016-07-11', d_dowodu='2016-07-12', opis_operacji= 'OPIS OPERACJI')
        ksi= fk.Ksi.testowe(dow, '55001/07', '2016/07', '2016-07-10', 1, '201330001', 'W', 100.00, 'FAK1', )

        # Konto pozabilansowe - nieuwzględniane w ZOiS
        ana= fk.Ana.testowe('0101', 'POZABILANSOWE', ma_0= 100.00, wn_7=100.00, ma_7= 100.00)
        syn= fk.Syn.testowe('010', 'POZABILANSOWE', bilans= 'P') 
                
        # Konto bez obrotów w okresie - nieuwzględniane w ZOiS
        ana= fk.Ana.testowe('0201', 'BEZ OBROTÓW', wn_8=100.00, ma_8= 100.00)
        syn= fk.Syn.testowe('020', 'BEZ OBROTÓW') 
                        
        # Utworzenie XML
                
        root= self.get_jpk_xml()
        
        # Sprawdzenie poprawności JPK
        
        # Sprawdzenie istnienia elementów podrzednych
        
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1', 
                                      './ZOiS', 
                                      './Dziennik[@typ="G"]', './DziennikCtrl',
                                      './KontoZapis[@typ="G"]', './KontoZapisCtrl'))

        # Zestawienie obrotów i sald
        
        faktura= self.assertXpath(root, './ZOiS')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura), """
            <ZOiS typ="G">
                <KodKonta>201-330001</KodKonta>
                <OpisKonta>KONTRAHENT</OpisKonta>
                
                <TypKonta>bilansowe</TypKonta>
                
                <KodZespolu>2</KodZespolu>
                <OpisZespolu>ROZRACHUNKI I ROSZCZENIA</OpisZespolu>
                
                <KodKategorii>201</KodKategorii>
                <OpisKategorii>ROZRACHUNKI Z KONTRAHENTAMI</OpisKategorii>
                
                <BilansOtwarciaWinien>100.00</BilansOtwarciaWinien>
                <BilansOtwarciaMa>0.00</BilansOtwarciaMa>
                
                <ObrotyWinien>100.00</ObrotyWinien>
                <ObrotyMa>300.21</ObrotyMa>
                
                <ObrotyWinienNarast>200.00</ObrotyWinienNarast>
                <ObrotyMaNarast>300.21</ObrotyMaNarast>
                
                <SaldoWinien>0.00</SaldoWinien>
                <SaldoMa>100.21</SaldoMa>
            </ZOiS>
        """)
        
        
        # Dziennik księgowań
        
        faktura= self.assertXpath(root, './Dziennik')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura), """
            <Dziennik typ="G">
                <LpZapisuDziennika>1</LpZapisuDziennika>
                <NrZapisuDziennika>1</NrZapisuDziennika>
                <OpisDziennika>dziennik</OpisDziennika>
                
                <NrDowoduKsiegowego>55001/07</NrDowoduKsiegowego>
                <RodzajDowodu>55001/07</RodzajDowodu>
                
                <DataOperacji>2016-07-11</DataOperacji>
                <DataDowodu>2016-07-12</DataDowodu>
                <DataKsiegowania>2016-07-10<!-- 2016/07 --></DataKsiegowania>
                
                <KodOperatora>-</KodOperatora>
                <OpisOperacji>OPIS OPERACJI</OpisOperacji>
                <DziennikKwotaOperacji>100.00</DziennikKwotaOperacji>
            </Dziennik>
        """)
                
                
        # Podsumowanie dziennika
        
        faktura_ctrl= self.assertXpath(root, './DziennikCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_ctrl), """
            <DziennikCtrl>
                <LiczbaWierszyDziennika>1</LiczbaWierszyDziennika>
                <SumaKwotOperacji>100.00</SumaKwotOperacji>
            </DziennikCtrl>
        """)

        # Zapisy na kontach
        
        faktura_wiersz= self.assertXpath(root, './KontoZapis')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_wiersz), """
            <KontoZapis typ="G">
                <LpZapisu>1</LpZapisu>
                <NrZapisu>1</NrZapisu>
                
                <KodKontaWinien>201-330001</KodKontaWinien>
                <KwotaWinien>100.00</KwotaWinien>
                
                <OpisZapisuWinien>FAK1</OpisZapisuWinien>
                
                <KodKontaMa>null</KodKontaMa>
                <KwotaMa>0.00</KwotaMa>
            </KontoZapis>
        """)
        
        # Podsumowanie zapisów na kontach
        
        faktura_wiersz_ctrl= self.assertXpath(root, './KontoZapisCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_wiersz_ctrl), """
            <KontoZapisCtrl>
                <LiczbaWierszyKontoZapisj>1</LiczbaWierszyKontoZapisj>
                <SumaWinien>100.00</SumaWinien>
                <SumaMa>0.00</SumaMa>
            </KontoZapisCtrl>
        """)

             
    @override_settings(FIRMA='gig')                
    def test_zois_bledy_konta(self):
        
        # Przygotowanie kontekstu 
        
        # Konto bez nazwy
        fk.Ana.testowe('201330001', '', wn_0= 100.00, wn_7=100.00, ma_7= 300.21)
        fk.Syn.testowe('201', '')

        # Utworzenie XML
                
        root= self.get_jpk_xml()
        
        # Sprawdzenie istnienia elementów podrzednych
        
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1', 
                                      './ZOiS', 
                                      './DziennikCtrl',
                                      './KontoZapisCtrl'))

        self.assertJpkBlad('ZOiS', '201-330001', 'Brak nazwy konta')
        self.assertJpkBlad('ZOiS', '201-330001', 'Nieokreślony opis kategorii kont (syntetyki)')  


    @override_settings(FIRMA='gig') 
    def test_ustal_zrodlowe(self):
        
        # Przygotowanie kontekstu 
        
        kto= fk.Uzy.testowe('ktos')
        dow= fk.Dow.testowe('S730477', '2016/07', '2016-07-10', 1, 200.00, 
                            kto= kto, opis_operacji= 'OPIS OPERACJI')
        ksi= fk.Ksi.testowe(dow, '55001/07', '2016/07', '2016-07-10', 1, '201330001', 'W', 200.00, 'FAK1', )
        
        kon= fk.Kon.testowe('330001', '6665554433')
        fak= fk.MagDok.testowe('73', 477, kon, '2016-07-10', '2016-07-22', '2016-07-23', 
                               kod_wydz= '330', uwagi= 'UWAGI DO FAKTURY SPRZEDAŻY')

        # Utworzenie XML
                
        root= self.get_jpk_xml()
        
        # Sprawdzenie poprawności JPK
        
        # Dziennik księgowań
        
        faktura= self.assertXpath(root, './Dziennik')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura), """
            <Dziennik typ="G">
                <LpZapisuDziennika>1</LpZapisuDziennika>
                <NrZapisuDziennika>1</NrZapisuDziennika>
                <OpisDziennika>dziennik</OpisDziennika>
                
                <NrDowoduKsiegowego>S730477</NrDowoduKsiegowego>
                <RodzajDowodu>S</RodzajDowodu>
                
                <DataOperacji>2016-07-22</DataOperacji>
                <DataDowodu>2016-07-10</DataDowodu>
                <DataKsiegowania>2016-07-10<!-- 2016/07 --></DataKsiegowania>
                
                <KodOperatora>-</KodOperatora>
                <OpisOperacji>SPRZEDAŻ, 730477/330/16, UWAGI DO FAKTURY SPRZEDAŻY</OpisOperacji>
                <DziennikKwotaOperacji>200.00</DziennikKwotaOperacji>
            </Dziennik>
        """)
                
                
        # Podsumowanie dziennika
        
        faktura_ctrl= self.assertXpath(root, './DziennikCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_ctrl), """
            <DziennikCtrl>
                <LiczbaWierszyDziennika>1</LiczbaWierszyDziennika>
                <SumaKwotOperacji>200.00</SumaKwotOperacji>
            </DziennikCtrl>
        """)

        