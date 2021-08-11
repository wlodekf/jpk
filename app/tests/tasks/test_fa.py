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


        
        
class BezFakturPustyXml(JpkTestCase):

    def setUp(self):
        self.jpk= Plik.objects.create(kod= 'JPK_FA',
                                      dataod= datetime.date(2016,7,1),
                                      datado= datetime.date(2016,7,31),
                                      utworzony_user= 'test')

    def get_jpk_xml(self):
        self.jpk= tasks.JpkTask(self.jpk.id).run()
        
        
    @override_settings(FIRMA='gig')
    def test_bez_faktur(self):
        
        self.get_jpk_xml()
                
        root= self.assertXmlDocument(self.jpk.xml.encode('utf-8'))
        
        # Sprawdzenie namespaceów
        
        self.assertXmlNamespace(root, None, 'http://jpk.mf.gov.pl/wzor/2016/03/09/03095/')        
        self.assertXmlNamespace(root, 'etd', 'http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2016/01/25/eD/DefinicjeTypy/')
        
        # Dla ułatwienia dalszego sprawdzania wywalany jest domyślny namespace
        
        root= self.assertXmlDocument(re.sub('xmlns="http://jpk.mf.gov.pl/wzor/2016/03/09/03095/"', '', self.jpk.xml).encode('utf-8'))
                
        self.assertXmlNode(root)
        self.assertXmlNode(root, tag= 'JPK')
        
        # Sprawdzenie istnienia elementów podrzednych
        
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1', './FakturaCtrl', './StawkiPodatku', './FakturaWierszCtrl'))

        # Sprawdzenie poprawności kolejnych elementów pustego pliku
        # Dla pliku JPK_FA

        # Nagłówek pliku JPK
                
        naglowek= self.assertXpath(root, './Naglowek')
        self.assertXmlEquivalentOutputs(self.node_xml(naglowek), """
            <Naglowek>
                <KodFormularza kodSystemowy="JPK_FA (1)" wersjaSchemy="1-0">JPK_FA</KodFormularza>
                <WariantFormularza>1</WariantFormularza>
                <CelZlozenia>1</CelZlozenia>
                <DataWytworzeniaJPK>...</DataWytworzeniaJPK>
                <DataOd>2016-07-01</DataOd>
                <DataDo>2016-07-31</DataDo>
                <DomyslnyKodWaluty>PLN</DomyslnyKodWaluty>
                <KodUrzedu>...</KodUrzedu>
            </Naglowek>
        """)
        
        # Podmiot1 dla ustalonej firmy
        
        podmiot1= self.assertXpath(root, './Podmiot1')
        self.assertXmlEquivalentOutputs(self.node_xml(podmiot1), """        
            <Podmiot1 xmlns:etd="http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2016/01/25/eD/DefinicjeTypy/">
            
            <IdentyfikatorPodmiotu>
                <etd:NIP>6340126016</etd:NIP>
                <etd:PelnaNazwa>Główny Instytut Górnictwa</etd:PelnaNazwa>
                <etd:REGON>000023461</etd:REGON>
            </IdentyfikatorPodmiotu>
            
            <AdresPodmiotu>
                <etd:KodKraju>PL</etd:KodKraju>
                <etd:Wojewodztwo>śląskie</etd:Wojewodztwo>
                <etd:Powiat>m. Katowice</etd:Powiat>
                <etd:Gmina>m. Katowice</etd:Gmina>
                <etd:Ulica>Plac Gwarków</etd:Ulica>
                <etd:NrDomu>1</etd:NrDomu>
                
                <etd:Miejscowosc>Katowice</etd:Miejscowosc>
                <etd:KodPocztowy>40-166</etd:KodPocztowy>
                <etd:Poczta>Katowice</etd:Poczta>
            </AdresPodmiotu>
            
            </Podmiot1>
        """)
                
        # Dla JPK_FA i pustego pliku
        
        faktura_ctrl= self.assertXpath(root, './FakturaCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_ctrl), """
            <FakturaCtrl>
                <LiczbaFaktur>0</LiczbaFaktur>
                <WartoscFaktur>0.00</WartoscFaktur>
            </FakturaCtrl>
        """)

        # Dla JPK_FA
        
        stawki_podatku= self.assertXpath(root, './StawkiPodatku')
        self.assertXmlEquivalentOutputs(self.node_xml(stawki_podatku), """
            <StawkiPodatku>
                <Stawka1>0.23</Stawka1>
                <Stawka2>0.08</Stawka2>
                <Stawka3>0.05</Stawka3>
                <Stawka4>0.00</Stawka4>
                <Stawka5>0.00</Stawka5>
            </StawkiPodatku>
        """)
        
        # Dla JPK_FA i pustego pliku
        
        faktura_wiersz_ctrl= self.assertXpath(root, './FakturaWierszCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_wiersz_ctrl), """
            <FakturaWierszCtrl>
                <LiczbaWierszyFaktur>0</LiczbaWierszyFaktur>
                <WartoscWierszyFaktur>0.00</WartoscWierszyFaktur>
            </FakturaWierszCtrl>
        """)


class JednaFaktura(JpkTestCase):

    def setUp(self):
        self.jpk= Plik.objects.create(kod= 'JPK_FA',
                                      dataod= datetime.date(2016,7,1),
                                      datado= datetime.date(2016,7,31),
                                      utworzony_user= 'test')
        
        self.kon= fk.Kon.testowe('330001', '6665554433')
        self.zlc= fk.Zlc.testowe('00000001', 'TEMAT1')
                
    def get_jpk_xml(self):
        self.jpk= tasks.JpkTask(self.jpk.id).run()
        
        self.assertXmlDocument(self.jpk.xml.encode('utf-8'))
        
        # Dla ułatwienia dalszego sprawdzania wywalany jest domyślny namespace
        return self.assertXmlDocument(re.sub('xmlns="http://jpk.mf.gov.pl/wzor/2016/03/09/03095/"', '', self.jpk.xml).encode('utf-8'))

                
    @override_settings(FIRMA='gig')
    def test_jedna_faktura(self):
        
        # Przygotowanie kontekstu 
        # Pojedyncza faktura z 23% VAT
        
        dok= fk.MagDok.testowe('57', 1, self.kon, '2016-07-02', '2016-07-19', '2016-07-22')
        fk.MagWiersz.testowe(dok, self.zlc, 100, '23%')
        
        # Utworzenie XML
                
        root= self.get_jpk_xml()
        
        # Sprawdzenie poprawności JPK
        
        # Sprawdzenie istnienia elementów podrzednych
        
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1', 
                                      './Faktura[@typ="G"]', './FakturaCtrl', 
                                      './StawkiPodatku', 
                                      './FakturaWiersz[@typ="G"]', './FakturaWierszCtrl'))

        # Sprawdzenie poprawności kolejnych elementów pustego pliku
        # Dla pliku JPK_FA

        # Podsumowanie nagłówków faktur
        
        faktura= self.assertXpath(root, './Faktura')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura), """
            <Faktura typ="G">
                <P_1>2016-07-02</P_1>
                <P_2A>570001/323/16</P_2A>
                <P_3A>FIRMA1</P_3A>
                <P_3B>WARSZAWA 01-920, KOPERNIKA 1</P_3B>
                
                <P_3C>Główny Instytut Górnictwa</P_3C>
                <P_3D>Katowice 40-166, ul. Gwarków 1</P_3D>
                <P_4A>PL</P_4A>
                <P_4B>6340126016</P_4B>
                
                <P_5B>6665554433</P_5B>
                <P_6>2016-07-19</P_6>
                
                <P_13_1>100.00</P_13_1>
                <P_14_1>23.00</P_14_1>
                <P_15>123.00</P_15>
                <P_16>false</P_16>
                <P_17>false</P_17>
                <P_18>false</P_18>
                <P_19>false</P_19>
                <P_20>false</P_20>
                <P_21>false</P_21>
                <P_23>false</P_23>
                
                <P_106E_2>false</P_106E_2>
                <RodzajFaktury>VAT</RodzajFaktury>
            </Faktura>
        """)
        
        # Podsumowanie nagłówków faktur
        
        faktura_ctrl= self.assertXpath(root, './FakturaCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_ctrl), """
            <FakturaCtrl>
                <LiczbaFaktur>1</LiczbaFaktur>
                <WartoscFaktur>123.00</WartoscFaktur>
            </FakturaCtrl>
        """)

        faktura_wiersz= self.assertXpath(root, './FakturaWiersz')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_wiersz), """
            <FakturaWiersz typ="G">
                <P_2B>570001/323/16</P_2B>
                <P_7>TEMAT1 /zlec: 00000001/</P_7>
                <P_8A>szt</P_8A>
                <P_8B>1.000000</P_8B>
                
                <P_9A>100.00</P_9A>
                <P_11>100.00</P_11>
                
                <P_12>23</P_12>
            </FakturaWiersz>
        """)
        
        # Podsumowanie wierszy
        
        faktura_wiersz_ctrl= self.assertXpath(root, './FakturaWierszCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_wiersz_ctrl), """
            <FakturaWierszCtrl>
                <LiczbaWierszyFaktur>1</LiczbaWierszyFaktur>
                <WartoscWierszyFaktur>100.00</WartoscWierszyFaktur>
            </FakturaWierszCtrl>
        """)


    @override_settings(FIRMA='gig')
    def test_faktura_korygujaca(self):
        
        # Przygotowanie kontekstu 
        # Faktura korygująca
        
        kor= fk.MagDok.testowe('55', 101, self.kon, '2016-03-09', '2016-03-09', '2016-03-09')
        dok= fk.MagDok.testowe('57', 1, self.kon, '2016-07-02', '2016-07-19', '2016-07-22', korekta='K', korygowana=kor)
        fk.MagWiersz.testowe(dok, self.zlc, 100, ' 7%')
        fk.FakRes.testowe(dok, przyczyna='KOREKTA STAWKI VAT')
        
        # Utworzenie XML
                
        root= self.get_jpk_xml()
        
        # Sprawdzenie poprawności JPK
        
        # Sprawdzenie istnienia elementów podrzednych
        
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1', 
                                      './Faktura[@typ="G"]', './FakturaCtrl', 
                                      './StawkiPodatku', 
                                      './FakturaWiersz[@typ="G"]', './FakturaWierszCtrl'))

        # Nagłówek faktury
        
        faktura= self.assertXpath(root, './Faktura')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura), """
            <Faktura typ="G">
                <P_1>2016-07-02</P_1>
                <P_2A>570001/323/16</P_2A>
                <P_3A>FIRMA1</P_3A>
                <P_3B>WARSZAWA 01-920, KOPERNIKA 1</P_3B>
                
                <P_3C>Główny Instytut Górnictwa</P_3C>
                <P_3D>Katowice 40-166, ul. Gwarków 1</P_3D>
                <P_4A>PL</P_4A>
                <P_4B>6340126016</P_4B>
                
                <P_5B>6665554433</P_5B>
                <P_6>2016-07-19</P_6>
                
                <P_13_2>100.00</P_13_2>
                <P_14_2>7.00</P_14_2>
                <P_15>107.00</P_15>
                
                <P_16>false</P_16>
                <P_17>false</P_17>
                <P_18>false</P_18>
                <P_19>false</P_19>
                <P_20>false</P_20>
                <P_21>false</P_21>
                <P_23>false</P_23>
                <P_106E_2>false</P_106E_2>
                
                <RodzajFaktury>KOREKTA</RodzajFaktury>
                <PrzyczynaKorekty>KOREKTA STAWKI VAT</PrzyczynaKorekty>
                <NrFaKorygowanej>550101/323/16</NrFaKorygowanej>
                <OkresFaKorygowanej>2016-03</OkresFaKorygowanej>

            </Faktura>
        """)
        
        # Podsumowanie nagłówków faktur
        
        faktura_ctrl= self.assertXpath(root, './FakturaCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_ctrl), """
            <FakturaCtrl>
                <LiczbaFaktur>1</LiczbaFaktur>
                <WartoscFaktur>107.00</WartoscFaktur>
            </FakturaCtrl>
        """)

        faktura_wiersz= self.assertXpath(root, './FakturaWiersz')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_wiersz), """
            <FakturaWiersz typ="G">
                <P_2B>570001/323/16</P_2B>
                <P_7>TEMAT1 /zlec: 00000001/</P_7>
                <P_8A>szt</P_8A>
                <P_8B>1.000000</P_8B>
                
                <P_9A>100.00</P_9A>
                <P_11>100.00</P_11>
                
                <P_12>7</P_12>
            </FakturaWiersz>
        """)
        
        # Podsumowanie wierszy
        
        faktura_wiersz_ctrl= self.assertXpath(root, './FakturaWierszCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_wiersz_ctrl), """
            <FakturaWierszCtrl>
                <LiczbaWierszyFaktur>1</LiczbaWierszyFaktur>
                <WartoscWierszyFaktur>100.00</WartoscWierszyFaktur>
            </FakturaWierszCtrl>
        """)
        
        
    @override_settings(FIRMA='gig')
    def test_faktura_korygujaca_brak_korygowanej(self):
        
        # Przygotowanie kontekstu 
        # Faktura korygująca
        
        dok= fk.MagDok.testowe('57', 1, self.kon, '2016-07-02', '2016-07-19', '2016-07-22', korekta='K', korygowana_id=0)
        fk.MagWiersz.testowe(dok, self.zlc, 100, ' 7%')
        fk.FakRes.testowe(dok, przyczyna='KOREKTA STAWKI VAT')
        
        # Utworzenie XML
                
        root= self.get_jpk_xml()
        
        # Sprawdzenie poprawności JPK
        
        # Sprawdzenie istnienia elementów podrzednych
        
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1', 
                                      './Faktura[@typ="G"]', './FakturaCtrl', 
                                      './StawkiPodatku', 
                                      './FakturaWiersz[@typ="G"]', './FakturaWierszCtrl'))

        self.assertJpkBlad('Faktura', '570001/323/16', 'Nie znaleziono faktury korygowanej')
        
        # Nagłówek faktury
        
        faktura= self.assertXpath(root, './Faktura')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura), """
            <Faktura typ="G">
                <P_1>2016-07-02</P_1>
                <P_2A>570001/323/16</P_2A>
                <P_3A>FIRMA1</P_3A>
                <P_3B>WARSZAWA 01-920, KOPERNIKA 1</P_3B>
                
                <P_3C>Główny Instytut Górnictwa</P_3C>
                <P_3D>Katowice 40-166, ul. Gwarków 1</P_3D>
                <P_4A>PL</P_4A>
                <P_4B>6340126016</P_4B>
                
                <P_5B>6665554433</P_5B>
                <P_6>2016-07-19</P_6>
                
                <P_13_2>100.00</P_13_2>
                <P_14_2>7.00</P_14_2>
                <P_15>107.00</P_15>
                
                <P_16>false</P_16>
                <P_17>false</P_17>
                <P_18>false</P_18>
                <P_19>false</P_19>
                <P_20>false</P_20>
                <P_21>false</P_21>
                <P_23>false</P_23>
                <P_106E_2>false</P_106E_2>
                
                <RodzajFaktury>KOREKTA</RodzajFaktury>
                <PrzyczynaKorekty>KOREKTA STAWKI VAT</PrzyczynaKorekty>
                <NrFaKorygowanej>-</NrFaKorygowanej>
                <OkresFaKorygowanej>-</OkresFaKorygowanej>

            </Faktura>
        """)
        
        # Podsumowanie nagłówków faktur
        
        faktura_ctrl= self.assertXpath(root, './FakturaCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_ctrl), """
            <FakturaCtrl>
                <LiczbaFaktur>1</LiczbaFaktur>
                <WartoscFaktur>107.00</WartoscFaktur>
            </FakturaCtrl>
        """)

        faktura_wiersz= self.assertXpath(root, './FakturaWiersz')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_wiersz), """
            <FakturaWiersz typ="G">
                <P_2B>570001/323/16</P_2B>
                <P_7>TEMAT1 /zlec: 00000001/</P_7>
                <P_8A>szt</P_8A>
                <P_8B>1.000000</P_8B>
                
                <P_9A>100.00</P_9A>
                <P_11>100.00</P_11>
                
                <P_12>7</P_12>
            </FakturaWiersz>
        """)
        
        # Podsumowanie wierszy
        
        faktura_wiersz_ctrl= self.assertXpath(root, './FakturaWierszCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_wiersz_ctrl), """
            <FakturaWierszCtrl>
                <LiczbaWierszyFaktur>1</LiczbaWierszyFaktur>
                <WartoscWierszyFaktur>100.00</WartoscWierszyFaktur>
            </FakturaWierszCtrl>
        """)
        
                
    @override_settings(FIRMA='gig')
    def test_stawki_vat(self):
        
        # Przygotowanie kontekstu 
        # Faktura korygująca
        
        STAWKI_VAT= ('22%', '23%', ' 7%', ' 8%', ' 3%', ' 5%', ' 0%', 'ZW.', 'OO.', 'NP.', 'NO.', 'W0%', )
        dok= fk.MagDok.testowe('57', 1, self.kon, '2016-07-02', '2016-07-19', '2016-07-22')
        for i, stawka in enumerate(STAWKI_VAT):
            fk.MagWiersz.testowe(dok, self.zlc, (i+1)*10, stawka)
        
        # Utworzenie XML
                
        root= self.get_jpk_xml()
        
        # Sprawdzenie poprawności JPK
        
        # Sprawdzenie istnienia elementów podrzednych
        
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1', 
                                      './Faktura[@typ="G"]', './FakturaCtrl', 
                                      './StawkiPodatku', 
                                      './FakturaWiersz[@typ="G"]', './FakturaWierszCtrl'))

        # Nagłówek faktury
        
        faktura= self.assertXpath(root, './Faktura')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura), """
            <Faktura typ="G">
                <P_1>2016-07-02</P_1>
                <P_2A>570001/323/16</P_2A>
                <P_3A>FIRMA1</P_3A>
                <P_3B>WARSZAWA 01-920, KOPERNIKA 1</P_3B>
                <P_3C>Główny Instytut Górnictwa</P_3C>
                <P_3D>Katowice 40-166, ul. Gwarków 1</P_3D>
                <P_4A>PL</P_4A>
                <P_4B>6340126016</P_4B>
                
                <P_5B>6665554433</P_5B>
                <P_6>2016-07-19</P_6>
                
                <P_13_1>30.00</P_13_1>
                <P_14_1>6.80</P_14_1>
                <P_13_2>70.00</P_13_2>
                <P_14_2>5.30</P_14_2>
                <P_13_3>110.00</P_13_3>
                <P_14_3>4.50</P_14_3>
                <P_13_4>90.00</P_13_4>
                <P_14_4>0.00</P_14_4>
                <P_13_5>210.00</P_13_5>
                <P_14_5>0.00</P_14_5>
                <P_13_6>190.00</P_13_6>
                <P_13_7>80.00</P_13_7>
                <P_15>796.60</P_15>
                
                <P_16>false</P_16>
                <P_17>false</P_17>
                <P_18>false</P_18>
                <P_19>false</P_19>
                <P_20>false</P_20>
                <P_21>false</P_21>
                <P_23>false</P_23>
                <P_106E_2>false</P_106E_2>
                    
                <RodzajFaktury>VAT</RodzajFaktury>
            </Faktura>
        """)
        
        # Podsumowanie nagłówków faktur
        
        faktura_ctrl= self.assertXpath(root, './FakturaCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_ctrl), """
            <FakturaCtrl>
                <LiczbaFaktur>1</LiczbaFaktur>
                <WartoscFaktur>796.60</WartoscFaktur>
            </FakturaCtrl>
        """)

        self.assertXpathCount(root, './FakturaWiersz', len(STAWKI_VAT))

        self.assertXpathSum(root, './FakturaWiersz/P_9A', decimal.Decimal('780.00'))
        self.assertXpathSum(root, './FakturaWiersz/P_11', decimal.Decimal('780.00'))
        self.assertXpathCount(root, './FakturaWiersz/P_12[text()="0"]', 2) 
        self.assertXpathCount(root, './FakturaWiersz/P_12', 9) 
                                        
        # Podsumowanie wierszy
        
        faktura_wiersz_ctrl= self.assertXpath(root, './FakturaWierszCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_wiersz_ctrl), """
            <FakturaWierszCtrl>
                <LiczbaWierszyFaktur>12</LiczbaWierszyFaktur>
                <WartoscWierszyFaktur>780.00</WartoscWierszyFaktur>
            </FakturaWierszCtrl>
        """)
        
         
    @override_settings(FIRMA='gig')
    def test_faktura_zaliczkowa_zal_wiersze(self):
        
        # Przygotowanie kontekstu 
        
        dok= fk.MagDok.testowe('57', 1, self.kon, '2016-07-02', '2016-07-19', '2016-07-22', ciagla='T')
        fk.MagWiersz.testowe(dok, self.zlc, 100, ' 7%', zaliczka= 107.00)
        
        # Utworzenie XML
                
        root= self.get_jpk_xml()
        
        # Sprawdzenie poprawności JPK
        
        # Sprawdzenie istnienia elementów podrzednych
        
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1', 
                                      './Faktura[@typ="G"]', './FakturaCtrl', 
                                      './StawkiPodatku', 
                                      './FakturaWiersz[@typ="G"]', './FakturaWierszCtrl'))

        # Nagłówek faktury
        
        faktura= self.assertXpath(root, './Faktura')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura), """
            <Faktura typ="G">
                <P_1>2016-07-02</P_1>
                <P_2A>570001/323/16</P_2A>
                <P_3A>FIRMA1</P_3A>
                <P_3B>WARSZAWA 01-920, KOPERNIKA 1</P_3B>
                <P_3C>Główny Instytut Górnictwa</P_3C>
                <P_3D>Katowice 40-166, ul. Gwarków 1</P_3D>
                <P_4A>PL</P_4A>
                <P_4B>6340126016</P_4B>
                
                <P_5B>6665554433</P_5B>
                <P_6>2016-07-19</P_6>
                    
                <P_13_2>100.00</P_13_2>
                <P_14_2>7.00</P_14_2>
                <P_15>107.00</P_15>
                
                <P_16>false</P_16>
                <P_17>false</P_17>
                <P_18>false</P_18>
                <P_19>false</P_19>
                <P_20>false</P_20>
                <P_21>false</P_21>
                <P_23>false</P_23>
                <P_106E_2>false</P_106E_2>
                    
                <RodzajFaktury>ZAL</RodzajFaktury>
                <ZALZaplata>107.00</ZALZaplata>
                <ZALPodatek>7.00</ZALPodatek>
            </Faktura>
        """)
        
        # Podsumowanie nagłówków faktur
        
        faktura_ctrl= self.assertXpath(root, './FakturaCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_ctrl), """
            <FakturaCtrl>
                <LiczbaFaktur>1</LiczbaFaktur>
                <WartoscFaktur>107.00</WartoscFaktur>
            </FakturaCtrl>
        """)

        faktura_wiersz= self.assertXpath(root, './FakturaWiersz')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_wiersz), """
            <FakturaWiersz typ="G">
                <P_2B>570001/323/16</P_2B>
                <P_7>TEMAT1 /zlec: 00000001/</P_7>
                <P_8A>szt</P_8A>
                <P_8B>1.000000</P_8B>
                
                <P_9A>100.00</P_9A>
                <P_11>100.00</P_11>
                
                <P_12>7</P_12>
            </FakturaWiersz>
        """)
        
        # Podsumowanie wierszy
        
        faktura_wiersz_ctrl= self.assertXpath(root, './FakturaWierszCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_wiersz_ctrl), """
            <FakturaWierszCtrl>
                <LiczbaWierszyFaktur>1</LiczbaWierszyFaktur>
                <WartoscWierszyFaktur>100.00</WartoscWierszyFaktur>
            </FakturaWierszCtrl>
        """)
        
              
    @override_settings(FIRMA='gig')
    def test_faktura_zaliczkowa(self):
        
        # Przygotowanie kontekstu 
        
        dok= fk.MagDok.testowe('57', 1, self.kon, '2016-07-02', '2016-07-19', '2016-07-22', ciagla='T')
        fk.MagWiersz.testowe(dok, self.zlc, 100, ' 7%')
        
        # Utworzenie XML
                
        root= self.get_jpk_xml()
        
        # Sprawdzenie poprawności JPK
        
        # Sprawdzenie istnienia elementów podrzednych
        
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1', 
                                      './Faktura[@typ="G"]', './FakturaCtrl', 
                                      './StawkiPodatku', 
                                      './FakturaWiersz[@typ="G"]', './FakturaWierszCtrl'))

        # Nagłówek faktury
        
        faktura= self.assertXpath(root, './Faktura')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura), """
            <Faktura typ="G">
                <P_1>2016-07-02</P_1>
                <P_2A>570001/323/16</P_2A>
                <P_3A>FIRMA1</P_3A>
                <P_3B>WARSZAWA 01-920, KOPERNIKA 1</P_3B>
                <P_3C>Główny Instytut Górnictwa</P_3C>
                <P_3D>Katowice 40-166, ul. Gwarków 1</P_3D>
                <P_4A>PL</P_4A>
                <P_4B>6340126016</P_4B>
                
                <P_5B>6665554433</P_5B>
                <P_6>2016-07-19</P_6>
                    
                <P_13_2>100.00</P_13_2>
                <P_14_2>7.00</P_14_2>
                <P_15>107.00</P_15>
                
                <P_16>false</P_16>
                <P_17>false</P_17>
                <P_18>false</P_18>
                <P_19>false</P_19>
                <P_20>false</P_20>
                <P_21>false</P_21>
                <P_23>false</P_23>
                <P_106E_2>false</P_106E_2>
                    
                <RodzajFaktury>ZAL</RodzajFaktury>
                <ZALZaplata>107.00</ZALZaplata>
                <ZALPodatek>7.00</ZALPodatek>
            </Faktura>
        """)
        
        # Podsumowanie nagłówków faktur
        
        faktura_ctrl= self.assertXpath(root, './FakturaCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_ctrl), """
            <FakturaCtrl>
                <LiczbaFaktur>1</LiczbaFaktur>
                <WartoscFaktur>107.00</WartoscFaktur>
            </FakturaCtrl>
        """)

        faktura_wiersz= self.assertXpath(root, './FakturaWiersz')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_wiersz), """
            <FakturaWiersz typ="G">
                <P_2B>570001/323/16</P_2B>
                <P_7>TEMAT1 /zlec: 00000001/</P_7>
                <P_8A>szt</P_8A>
                <P_8B>1.000000</P_8B>
                
                <P_9A>100.00</P_9A>
                <P_11>100.00</P_11>
                
                <P_12>7</P_12>
            </FakturaWiersz>
        """)
        
        # Podsumowanie wierszy
        
        faktura_wiersz_ctrl= self.assertXpath(root, './FakturaWierszCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_wiersz_ctrl), """
            <FakturaWierszCtrl>
                <LiczbaWierszyFaktur>1</LiczbaWierszyFaktur>
                <WartoscWierszyFaktur>100.00</WartoscWierszyFaktur>
            </FakturaWierszCtrl>
        """)
                      
                      
    @override_settings(FIRMA='gig')
    def test_rodzaj_faktury(self):
        
        # Przygotowanie kontekstu 
        
        dok= fk.MagDok.testowe('57', 1, self.kon, '2016-07-02', '2016-07-19', '2016-07-22', rodzaj='KSOZ431EIT')
        fk.MagWiersz.testowe(dok, self.zlc, 100, ' 7%')
        fk.Spo.testowe('SPPOD', '431', 'ART. 43 UST. 1 RÓŻNE PUNKTY USTAWY')
        
        # Utworzenie XML
                
        root= self.get_jpk_xml()
        
        # Sprawdzenie istnienia elementów podrzednych
        
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1', 
                                      './Faktura[@typ="G"]', './FakturaCtrl', 
                                      './StawkiPodatku', 
                                      './FakturaWiersz[@typ="G"]', './FakturaWierszCtrl'))

        # Nagłówek faktury
        
        faktura= self.assertXpath(root, './Faktura')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura), """
            <Faktura typ="G">
                <P_1>2016-07-02</P_1>
                <P_2A>570001/323/16</P_2A>
                <P_3A>FIRMA1</P_3A>
                <P_3B>WARSZAWA 01-920, KOPERNIKA 1</P_3B>
                <P_3C>Główny Instytut Górnictwa</P_3C>
                <P_3D>Katowice 40-166, ul. Gwarków 1</P_3D>
                <P_4A>PL</P_4A>
                <P_4B>6340126016</P_4B>
                
                <P_5B>6665554433</P_5B>
                <P_6>2016-07-19</P_6>
                    
                <P_13_2>100.00</P_13_2>
                <P_14_2>7.00</P_14_2>
                <P_15>107.00</P_15>
                
                <P_16>true</P_16>
                <P_17>true</P_17>
                <P_18>true</P_18>
                <P_19>true</P_19>
                <P_19A>ART. 43 UST. 1 RÓŻNE PUNKTY USTAWY</P_19A>
                <P_20>true</P_20>
                <P_21>true</P_21>
                <P_23>true</P_23>
                
                <P_106E_2>false</P_106E_2>
                    
                <RodzajFaktury>VAT</RodzajFaktury>
            </Faktura>
        """)
        
        # Podsumowanie nagłówków faktur
        
        faktura_ctrl= self.assertXpath(root, './FakturaCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_ctrl), """
            <FakturaCtrl>
                <LiczbaFaktur>1</LiczbaFaktur>
                <WartoscFaktur>107.00</WartoscFaktur>
            </FakturaCtrl>
        """)

        faktura_wiersz= self.assertXpath(root, './FakturaWiersz')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_wiersz), """
            <FakturaWiersz typ="G">
                <P_2B>570001/323/16</P_2B>
                <P_7>TEMAT1 /zlec: 00000001/</P_7>
                <P_8A>szt</P_8A>
                <P_8B>1.000000</P_8B>
                
                <P_9A>100.00</P_9A>
                <P_11>100.00</P_11>
                
                <P_12>7</P_12>
            </FakturaWiersz>
        """)
        
        # Podsumowanie wierszy
        
        faktura_wiersz_ctrl= self.assertXpath(root, './FakturaWierszCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_wiersz_ctrl), """
            <FakturaWierszCtrl>
                <LiczbaWierszyFaktur>1</LiczbaWierszyFaktur>
                <WartoscWierszyFaktur>100.00</WartoscWierszyFaktur>
            </FakturaWierszCtrl>
        """)
             
             
    @override_settings(FIRMA='gig')
    def test_wycena_brutto(self):
        
        # Przygotowanie kontekstu 
        # Faktura korygująca
        
        dok= fk.MagDok.testowe('57', 1, self.kon, '2016-07-02', '2016-07-19', '2016-07-22')
        fk.MagWiersz.testowe(dok, self.zlc, 100, ' 7%', wsk_wyc= 'B')
        
        # Utworzenie XML
                
        root= self.get_jpk_xml()
        
        # Sprawdzenie poprawności JPK
        # Sprawdzenie istnienia elementów podrzednych
        
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1', 
                                      './Faktura[@typ="G"]', './FakturaCtrl', 
                                      './StawkiPodatku', 
                                      './FakturaWiersz[@typ="G"]', './FakturaWierszCtrl'))

        # Nagłówek faktury
        
        faktura= self.assertXpath(root, './Faktura')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura), """
            <Faktura typ="G">
                <P_1>2016-07-02</P_1>
                <P_2A>570001/323/16</P_2A>
                <P_3A>FIRMA1</P_3A>
                <P_3B>WARSZAWA 01-920, KOPERNIKA 1</P_3B>
                <P_3C>Główny Instytut Górnictwa</P_3C>
                <P_3D>Katowice 40-166, ul. Gwarków 1</P_3D>
                <P_4A>PL</P_4A>
                <P_4B>6340126016</P_4B>
                
                <P_5B>6665554433</P_5B>
                <P_6>2016-07-19</P_6>
                    
                <P_13_2>93.46</P_13_2>
                <P_14_2>6.54</P_14_2>
                <P_15>100.00</P_15>
                
                <P_16>false</P_16>
                <P_17>false</P_17>
                <P_18>false</P_18>
                <P_19>false</P_19>
                
                <P_20>false</P_20>
                <P_21>false</P_21>
                <P_23>false</P_23>
                
                <P_106E_2>false</P_106E_2>
                    
                <RodzajFaktury>VAT</RodzajFaktury>
            </Faktura>
        """)
        
        # Podsumowanie nagłówków faktur
        
        faktura_ctrl= self.assertXpath(root, './FakturaCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_ctrl), """
            <FakturaCtrl>
                <LiczbaFaktur>1</LiczbaFaktur>
                <WartoscFaktur>100.00</WartoscFaktur>
            </FakturaCtrl>
        """)

        faktura_wiersz= self.assertXpath(root, './FakturaWiersz')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_wiersz), """
            <FakturaWiersz typ="G">
                <P_2B>570001/323/16</P_2B>
                <P_7>TEMAT1 /zlec: 00000001/</P_7>
                <P_8A>szt</P_8A>
                <P_8B>1.000000</P_8B>
                
                <P_9B>100.00</P_9B>
                <P_11A>100.00</P_11A>
                
                <P_12>7</P_12>
            </FakturaWiersz>
        """)
        
        # Podsumowanie wierszy
        
        faktura_wiersz_ctrl= self.assertXpath(root, './FakturaWierszCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(faktura_wiersz_ctrl), """
            <FakturaWierszCtrl>
                <LiczbaWierszyFaktur>1</LiczbaWierszyFaktur>
                <WartoscWierszyFaktur>93.46</WartoscWierszyFaktur>
            </FakturaWierszCtrl>
        """)
                                        