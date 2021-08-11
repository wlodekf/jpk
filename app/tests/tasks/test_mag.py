# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from app import tasks
from app.models import Plik
import datetime, decimal
import re
from .. import JpkTestCase
import logging
from fk import models as fk

logging.disable(logging.CRITICAL)

        
class MagTestCase(JpkTestCase):

    def setUp(self):
        self.jpk= Plik.objects.create(kod= 'JPK_MAG',
                                      dataod= datetime.date(2016,7,1),
                                      datado= datetime.date(2016,7,31),
                                      magazyn= 'M50 Magazyn Wyrobow Gotowych',
                                      utworzony_user= 'test')

        self.kon= fk.Kon.testowe('330001', '6665554433')
        self.zlc= fk.Zlc.testowe('00000001', 'TEMAT1')
        
    def get_jpk_xml(self):
        self.jpk= tasks.JpkTask(self.jpk.id).run()
        
        self.assertXmlDocument(self.jpk.xml.encode('utf-8'))
        
        # Dla ułatwienia dalszego sprawdzania wywalany jest domyślny namespace
        return self.assertXmlDocument(re.sub('xmlns="http://jpk.mf.gov.pl/wzor/2016/03/09/03093/"', '', self.jpk.xml).encode('utf-8'))

    def test_mag(self):
        
        # Przygotowanie kontekstu 
        
        towar= fk.MagTowar.testowe('001', 'NAZWA TOWARU')
        kart= fk.MagKart.testowe('001', towar)
        
        dok= fk.MagDok.testowe('57', 1, self.kon, '2016-07-02', '2016-07-19', '2016-07-22',
                               symbol= 'PZ', dzial= 'M50', )
        fk.MagWiersz.testowe(dok, self.zlc, 100, '23%', 
                             id_kart_id= kart.id, znak= '+',
                             il_real= decimal.Decimal(1), cena_ewid= decimal.Decimal(100), wartosc= decimal.Decimal(100))

        dok= fk.MagDok.testowe('57', 1, self.kon, '2016-07-02', '2016-07-19', '2016-07-22',
                               symbol= 'RW', dzial= 'M50', )
        fk.MagWiersz.testowe(dok, self.zlc, 100, '23%', 
                             id_kart_id= kart.id, znak= '-',
                             il_real= decimal.Decimal(1), cena_ewid= decimal.Decimal(100), wartosc= decimal.Decimal(100))
                
        # Utworzenie XML
                
        root= self.get_jpk_xml()
        
        # Sprawdzenie poprawności JPK
        
        # Sprawdzenie istnienia elementów podrzednych
        
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1', './PZ', './RW'))
        
        # Przyjęcie z zewnątrz
        
        pz= self.assertXpath(root, './PZ')
        self.assertXpathsExist(pz, ('./PZWartosc', './PZWiersz', './PZCtrl'))                

        pz_wartosc= self.assertXpath(pz, './PZWartosc')
        self.assertXmlEquivalentOutputs(self.node_xml(pz_wartosc), """
            <PZWartosc>
                <NumerPZ>PZ 1/M50/16</NumerPZ>
                <DataPZ>2016-07-02</DataPZ>
                <WartoscPZ>100.00</WartoscPZ>
                <DataOtrzymaniaPZ>2016-07-02</DataOtrzymaniaPZ>
                <Dostawca>FIRMA1, WARSZAWA</Dostawca>
            </PZWartosc>
        """)
        
        pz_wiersz= self.assertXpath(pz, './PZWiersz')
        self.assertXmlEquivalentOutputs(self.node_xml(pz_wiersz), """
            <PZWiersz>
                <Numer2PZ>PZ 1/M50/16</Numer2PZ>
                <KodTowaruPZ>001</KodTowaruPZ>
                <NazwaTowaruPZ>NAZWA TOWARU</NazwaTowaruPZ>
                <IloscPrzyjetaPZ>1.000000</IloscPrzyjetaPZ>
                <JednostkaMiaryPZ>szt</JednostkaMiaryPZ>
                <CenaJednPZ>100.00</CenaJednPZ>
                <WartoscPozycjiPZ>100.00</WartoscPozycjiPZ>
            </PZWiersz>
        """)
                
        pz_ctrl= self.assertXpath(pz, './PZCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(pz_ctrl), """
            <PZCtrl>
                <LiczbaPZ>1</LiczbaPZ>
                <SumaPZ>100.00</SumaPZ>
            </PZCtrl>
        """)

        # Wydania na zewnątrz

        rw= self.assertXpath(root, './RW')
        self.assertXpathsExist(rw, ('./RWWartosc', './RWWiersz', './RWCtrl')) 
        
        rw_wartosc= self.assertXpath(rw, './RWWartosc')
        self.assertXmlEquivalentOutputs(self.node_xml(rw_wartosc), """
            <RWWartosc>
                <NumerRW>RW 1/M50/16</NumerRW>
                <DataRW>2016-07-02</DataRW>
                <WartoscRW>-100.00</WartoscRW>
                <DataWydaniaRW>2016-07-02</DataWydaniaRW>
                <SkadRW>-</SkadRW>
                <DokadRW>None</DokadRW>
            </RWWartosc>
        """)
        
        rw_wiersz= self.assertXpath(rw, './RWWiersz')
        self.assertXmlEquivalentOutputs(self.node_xml(rw_wiersz), """
            <RWWiersz>
                <Numer2RW>RW 1/M50/16</Numer2RW>
                <KodTowaruRW>001</KodTowaruRW>
                <NazwaTowaruRW>NAZWA TOWARU</NazwaTowaruRW>
                <IloscWydanaRW>-1.000000</IloscWydanaRW>
                <JednostkaMiaryRW>szt</JednostkaMiaryRW>
                <CenaJednRW>100.00</CenaJednRW>
                <WartoscPozycjiRW>-100.00</WartoscPozycjiRW>
            </RWWiersz>
        """)
                
        rw_ctrl= self.assertXpath(rw, './RWCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(rw_ctrl), """
            <RWCtrl>
                <LiczbaRW>1</LiczbaRW>
                <SumaRW>-100.00</SumaRW>
            </RWCtrl>
        """)
        


    def test_pz_nr_faktury_1faktura_1pz(self):
        """
        Test sposobu ustalania numeru faktury zakupu do dokumentów PZ.
        """
        
        # Przygotowanie kontekstu 
        
        towar= fk.MagTowar.testowe('001', 'NAZWA TOWARU')
        kart= fk.MagKart.testowe('001', towar)
        
        dok= fk.MagDok.testowe('57', 1, self.kon, '2016-07-02', '2016-07-19', '2016-07-22',
                               symbol= 'PZ', dzial= 'M50', )
        fk.MagWiersz.testowe(dok, self.zlc, 100, '23%', 
                             id_kart_id= kart.id, znak= '+',
                             il_real= decimal.Decimal(1), cena_ewid= decimal.Decimal(100), wartosc= decimal.Decimal(100))

        fk.Zak.testowe('ZKM', 'FAK1', self.kon, '2016-07-02', '2016-07-02', '2016/07',
                       d_wyst= '2016-07-02', d_zak= '2016-07-02', mag= 'M50', pz='1') 
        
        # Utworzenie XML
                
        root= self.get_jpk_xml()
        
        # Sprawdzenie poprawności JPK
        # Sprawdzenie istnienia elementów podrzednych
        
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1', './PZ'))
        
        # Przyjęcie z zewnątrz
        
        pz= self.assertXpath(root, './PZ')
        self.assertXpathsExist(pz, ('./PZWartosc', './PZWiersz', './PZCtrl'))                

        pz_wartosc= self.assertXpath(pz, './PZWartosc')
        self.assertXmlEquivalentOutputs(self.node_xml(pz_wartosc), """
            <PZWartosc>
                <NumerPZ>PZ 1/M50/16</NumerPZ>
                <DataPZ>2016-07-02</DataPZ>
                <WartoscPZ>100.00</WartoscPZ>
                <DataOtrzymaniaPZ>2016-07-02</DataOtrzymaniaPZ>
                <Dostawca>FIRMA1, WARSZAWA</Dostawca>
                <NumerFaPZ>FAK1</NumerFaPZ>
                <DataFaPZ>2016-07-02</DataFaPZ>                                
            </PZWartosc>
        """)
        
        pz_wiersz= self.assertXpath(pz, './PZWiersz')
        self.assertXmlEquivalentOutputs(self.node_xml(pz_wiersz), """
            <PZWiersz>
                <Numer2PZ>PZ 1/M50/16</Numer2PZ>
                <KodTowaruPZ>001</KodTowaruPZ>
                <NazwaTowaruPZ>NAZWA TOWARU</NazwaTowaruPZ>
                <IloscPrzyjetaPZ>1.000000</IloscPrzyjetaPZ>
                <JednostkaMiaryPZ>szt</JednostkaMiaryPZ>
                <CenaJednPZ>100.00</CenaJednPZ>
                <WartoscPozycjiPZ>100.00</WartoscPozycjiPZ>
            </PZWiersz>
        """)
                
        pz_ctrl= self.assertXpath(pz, './PZCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(pz_ctrl), """
            <PZCtrl>
                <LiczbaPZ>1</LiczbaPZ>
                <SumaPZ>100.00</SumaPZ>
            </PZCtrl>
        """)


    def test_pz_nr_faktury_1faktura_wiele_pz(self):
        """
        Test sposobu ustalania numeru faktury zakupu do dokumentów PZ.
        """
        
        # Przygotowanie kontekstu 
        
        towar= fk.MagTowar.testowe('001', 'NAZWA TOWARU')
        kart= fk.MagKart.testowe('001', towar)
        
        # Pierwszy PZ
        
        dok= fk.MagDok.testowe('57', 1, self.kon, '2016-07-02', '2016-07-19', '2016-07-22',
                               symbol= 'PZ', dzial= 'M50', )
        fk.MagWiersz.testowe(dok, self.zlc, 100, '23%', 
                             id_kart_id= kart.id, znak= '+',
                             il_real= decimal.Decimal(1), cena_ewid= decimal.Decimal(100), wartosc= decimal.Decimal(100))

        # Drugi PZ
        
        dok= fk.MagDok.testowe('57', 2, self.kon, '2016-07-03', '2016-07-20', '2016-07-23',
                               symbol= 'PZ', dzial= 'M50', )
        fk.MagWiersz.testowe(dok, self.zlc, 10, '23%', 
                             id_kart_id= kart.id, znak= '+',
                             il_real= decimal.Decimal(1), cena_ewid= decimal.Decimal(10), wartosc= decimal.Decimal(10))
        
        # Trzeci PZ
        
        dok= fk.MagDok.testowe('57', 3, self.kon, '2016-07-04', '2016-07-21', '2016-07-24',
                               symbol= 'PZ', dzial= 'M50', )
        fk.MagWiersz.testowe(dok, self.zlc, 30, '23%', 
                             id_kart_id= kart.id, znak= '+',
                             il_real= decimal.Decimal(3), cena_ewid= decimal.Decimal(10), wartosc= decimal.Decimal(30))
                
        # Faktura do obu PZ
        
        fk.Zak.testowe('ZKM', 'FAK1', self.kon, '2016-07-02', '2016-07-02', '2016/07',
                       d_wyst= '2016-07-02', d_zak= '2016-07-02', mag= 'M50', pz='1 2/M50/16 M50/3') 

        # Faktura z podobnymi (takimi samymi numerami PZ ale z innego roku)
        # Dalej oddalona od PZ niż ta z 2016
        
        fk.Zak.testowe('ZKM', 'FAK2', self.kon, '2015-03-02', '2015-03-02', '2015/07',
                       d_wyst= '2015-07-02', d_zak= '2015-07-02', mag= 'M50', pz='1 2/M50 M50/3') 
        
        # Utworzenie XML
                
        root= self.get_jpk_xml()
        
        # Sprawdzenie poprawności JPK
        # Sprawdzenie istnienia elementów podrzednych
        
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1', './PZ'))
        
        # Przyjęcie z zewnątrz
        
        pz= self.assertXpath(root, './PZ')
        self.assertXmlEquivalentOutputs(self.node_xml(pz), """
        <PZ>
            <PZWartosc>
                <NumerPZ>PZ 1/M50/16</NumerPZ>
                <DataPZ>2016-07-02</DataPZ>
                <WartoscPZ>100.00</WartoscPZ>
                <DataOtrzymaniaPZ>2016-07-02</DataOtrzymaniaPZ>
                <Dostawca>FIRMA1, WARSZAWA</Dostawca>
                <NumerFaPZ>FAK1</NumerFaPZ>
                <DataFaPZ>2016-07-02</DataFaPZ>                                
            </PZWartosc>
            
            <PZWartosc>
                <NumerPZ>PZ 2/M50/16</NumerPZ>
                <DataPZ>2016-07-03</DataPZ>
                <WartoscPZ>10.00</WartoscPZ>
                <DataOtrzymaniaPZ>2016-07-03</DataOtrzymaniaPZ>
                <Dostawca>FIRMA1, WARSZAWA</Dostawca>
                <NumerFaPZ>FAK1</NumerFaPZ>
                <DataFaPZ>2016-07-02</DataFaPZ>                                
            </PZWartosc>
                     
            <PZWartosc>
                <NumerPZ>PZ 3/M50/16</NumerPZ>
                <DataPZ>2016-07-04</DataPZ>
                <WartoscPZ>30.00</WartoscPZ>
                <DataOtrzymaniaPZ>2016-07-04</DataOtrzymaniaPZ>
                <Dostawca>FIRMA1, WARSZAWA</Dostawca>
                <NumerFaPZ>FAK1</NumerFaPZ>
                <DataFaPZ>2016-07-02</DataFaPZ>                                
            </PZWartosc>
                                    
            <PZWiersz>
                <Numer2PZ>PZ 1/M50/16</Numer2PZ>
                <KodTowaruPZ>001</KodTowaruPZ>
                <NazwaTowaruPZ>NAZWA TOWARU</NazwaTowaruPZ>
                <IloscPrzyjetaPZ>1.000000</IloscPrzyjetaPZ>
                <JednostkaMiaryPZ>szt</JednostkaMiaryPZ>
                <CenaJednPZ>100.00</CenaJednPZ>
                <WartoscPozycjiPZ>100.00</WartoscPozycjiPZ>
            </PZWiersz>
                
            <PZWiersz>
                <Numer2PZ>PZ 2/M50/16</Numer2PZ>
                <KodTowaruPZ>001</KodTowaruPZ>
                <NazwaTowaruPZ>NAZWA TOWARU</NazwaTowaruPZ>
                <IloscPrzyjetaPZ>1.000000</IloscPrzyjetaPZ>
                <JednostkaMiaryPZ>szt</JednostkaMiaryPZ>
                <CenaJednPZ>10.00</CenaJednPZ>
                <WartoscPozycjiPZ>10.00</WartoscPozycjiPZ>
            </PZWiersz>
              
            <PZWiersz>
                <Numer2PZ>PZ 3/M50/16</Numer2PZ>
                <KodTowaruPZ>001</KodTowaruPZ>
                <NazwaTowaruPZ>NAZWA TOWARU</NazwaTowaruPZ>
                <IloscPrzyjetaPZ>3.000000</IloscPrzyjetaPZ>
                <JednostkaMiaryPZ>szt</JednostkaMiaryPZ>
                <CenaJednPZ>10.00</CenaJednPZ>
                <WartoscPozycjiPZ>30.00</WartoscPozycjiPZ>
            </PZWiersz>
                                        
            <PZCtrl>
                <LiczbaPZ>3</LiczbaPZ>
                <SumaPZ>140.00</SumaPZ>
            </PZCtrl>
        </PZ>
        """)
        