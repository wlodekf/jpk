# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import override_settings

from app import tasks, utils
from app.models import Plik
import datetime
import decimal
import re
from .. import JpkTestCase
from fk import models as fk
import logging
from django.conf import settings

logging.disable(logging.CRITICAL)


def dec(d):
    return decimal.Decimal(d)


class VatTestCase(object):

    def setUp(self):
        self.jpk= Plik.objects.create(kod= 'JPK_VAT',
                                      dataod= datetime.date(2016,7,1),
                                      datado= datetime.date(2016,7,31),
                                      utworzony_user= 'test')
        
        # Dane ogólne
        
        self.kon= fk.Kon.testowe('330001', '6665554433')
        self.kon_ue= fk.Kon.testowe('440001', 'DE6665554433', idtyp= 'NIPUE')
        self.zlc= fk.Zlc.testowe('00000001', 'TEMAT1')
        fk.SysPar.testowe('ZAK-BEZ-BRUTTO', 'nie')
        
        # Prewspółczynniki
        
        fk.DefZrv.testowe(2016, 'OZN', 90) # +10%
        fk.DefZrv.testowe(2015, 'OZN', 80)

        fk.DefZrv.testowe(2016, 'OZ', 70) # -10%
        fk.DefZrv.testowe(2015, 'OZ', 80)        
        
        
    def get_jpk_xml(self):
        
        self.jpk= tasks.JpkTask(self.jpk.id).run()
        
        self.assertXmlDocument(self.jpk.xml.encode('utf-8'))
        
        # Dla ułatwienia dalszego sprawdzania wywalany jest domyślny namespace
        return self.assertXmlDocument(re.sub('xmlns="http://jpk.mf.gov.pl/wzor/2016/03/09/03094/"', '', self.jpk.xml).encode('utf-8'))

        
    def test_ogolna_struktura(self):
        
        dok= fk.MagDok.testowe('57', 1, self.kon, '2016-07-02', '2016-07-19', '2016-07-22')
        fk.MagWiersz.testowe(dok, self.zlc, 50, '23%')
        fk.MagWiersz.testowe(dok, self.zlc, 50, '23%')
                
        fk.Zak.testowe('ZKU', 'FAK1', self.kon, '2016-07-02', '2016-07-02', '2016/07', 
                  kos_w_net= 2400.00, kos_w_vat= 552.00,
                  soz_p_net= 100.00, soz_p_vat= 23.00)
        
        fk.Zak.testowe('ZKU', 'FAK2', self.kon, '2016-07-02', '2016-07-02', '2016/07', 
                  soz_p_net= 0.00, soz_p_vat= 0.00)
                
        root= self.get_jpk_xml()
        
        # Sprawdzenie istnienia elementów podrzednych
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1',
                                      './SprzedazWiersz[@typ="G"]', './SprzedazCtrl', 
                                      './ZakupWiersz[@typ="G"]', './ZakupCtrl'))

        # Sprzedaż
        
        sprzedaz= self.assertXpath(root, './SprzedazWiersz')
        self.assertXmlEquivalentOutputs(self.node_xml(sprzedaz), """
            <SprzedazWiersz typ="G">
                <LpSprzedazy>1</LpSprzedazy>
                 <DataSprzedazy>2016-07-19</DataSprzedazy>
                <DataWystawienia>2016-07-02</DataWystawienia>
                
                <NrDokumentu>570001/323/16<!--...--></NrDokumentu>
                <NazwaNabywcy>FIRMA1</NazwaNabywcy>
                <AdresNabywcy>WARSZAWA 01-920, KOPERNIKA 1</AdresNabywcy>
                
                <K_19>100.00</K_19><K_20>23.00</K_20>    
            </SprzedazWiersz>
        """)
        
        # Podsumowanie sprzedaży
        
        sprzedaz_ctrl= self.assertXpath(root, './SprzedazCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(sprzedaz_ctrl), """
            <SprzedazCtrl>
                <LiczbaWierszySprzedazy>1</LiczbaWierszySprzedazy>
                <PodatekNalezny>23.00</PodatekNalezny>
            </SprzedazCtrl>
        """)

        # Zakup w miesiącu
        
        if settings.FIRMA == 'gig':
            netto, vat= '2230.00', '512.90'
        else:
            netto, vat= '100.00', '16.10' 
        
        zakup= self.assertXpath(root, './ZakupWiersz')
        self.assertXmlEquivalentOutputs(self.node_xml(zakup), """
            <ZakupWiersz typ="G">
                <LpZakupu>1</LpZakupu>
                <NazwaWystawcy>FIRMA1</NazwaWystawcy>
                <AdresWystawcy>WARSZAWA 01-920, KOPERNIKA 1</AdresWystawcy>
                <NrIdWystawcy>6665554433</NrIdWystawcy>
                <NrFaktury>FAK1<!--ZKU--></NrFaktury>
                <DataWplywuFaktury>2016-07-02</DataWplywuFaktury>
                
                <K_45>{}</K_45><K_46>{}</K_46>    
            </ZakupWiersz>
        """.format(netto, vat))
        
        # Podsumowanie zakupów
        
        zakup_ctrl= self.assertXpath(root, './ZakupCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(zakup_ctrl), """
            <ZakupCtrl>
                <LiczbaWierszyZakupow>1</LiczbaWierszyZakupow>
                <PodatekNaliczony>{}</PodatekNaliczony>
            </ZakupCtrl>
        """.format(vat))
        
        
    def test_brak_prewspolczynnikow(self):

        # Skorygowanie początku okresu aby policzyła się korekta
        self.jpk.dataod= datetime.date(2016,1,1)
        self.jpk.datado= datetime.date(2016,1,31)        
        self.jpk.save()
        
        # Usunięcie prewspółczynników utworzonych przez setUp        
        fk.DefZrv.objects.using(utils.test_dbs({})).all().delete()
        kon_pusty= fk.Kon.testowe('990001', None, nazwa= None, kod= None, miejsc= None, ulica= None)
                
        fk.Zak.testowe('ZKU', 'FAK1', self.kon, '2016-01-02', '2016-01-02', '2016/01', 
                  kos_w_net= 2400.00, kos_w_vat= 552.00,
                  soz_p_net= 100.00, soz_p_vat= 23.00,
                  netto= 2000.00, vat= 552.00, brutto=2552.00)

        fk.Zak.testowe('ZKU', 'FAK2', kon_pusty, '2016-01-02', '2016-01-02', '2016/01', 
                  soz_p_net= 0.00, soz_p_vat= 0.00, # zerowy podatek - pozycja pomijana
                  netto= 100.00, vat= 7.00) # VAT nie rozliczony
                
        root= self.get_jpk_xml()
        
        # Sprawdzenie istnienia elementów podrzednych
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1',
                                      './SprzedazCtrl', 
                                      './ZakupWiersz[@typ="G"]', './ZakupCtrl'))

        # Podsumowanie sprzedaży
        
        sprzedaz_ctrl= self.assertXpath(root, './SprzedazCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(sprzedaz_ctrl), """
            <SprzedazCtrl>
                <LiczbaWierszySprzedazy>0</LiczbaWierszySprzedazy>
                <PodatekNalezny>0.00</PodatekNalezny>
            </SprzedazCtrl>
        """)

        # Zakup w miesiącu

        # Błędy o braku współczynników => liczenie prewspółczynnikami 100.00
        self.assertJpkBlad('ZAK', 'WSP', 'Nie znaleziono prewspółczynnika dla {} w bazie {}'.format(self.jpk.dataod.year, utils.test_dbs({})))
        self.assertJpkBlad('ZAK', 'PRE', 'Nie znaleziono prewspółczynnika dla {} w bazie {}'.format(self.jpk.dataod.year-1, utils.test_dbs({})))
        
        # Błędy o nierozliczeniu faktury FAK1
        self.assertJpkBlad('ZAK', 'FAK1', 'Netto z ekranu rozliczenia jest różne od netto faktury')        
        self.assertJpkBlad('ZAK', 'FAK1', 'VAT z ekranu rozliczenia jest różny od VAT faktury')
        self.assertJpkBlad('ZAK', 'FAK1', 'Brutto z ekranu rozliczenia jest różny od wartości faktury')
        
        self.assertJpkBlad('ZAK', 'FAK2', 'W tej fakturze VAT nie jest rozliczony')  

        # Błędy niepełnych danych kontrahenta
        self.assertJpkBlad('ZAK', 'FAK2', 'Nieokreślona nazwa dostawcy')
        self.assertJpkBlad('ZAK', 'FAK2', 'Brak adresu dostawcy')
        self.assertJpkBlad('ZAK', 'FAK2', 'Brak NIP dostawcy')

                        
        if settings.FIRMA == 'gig':
            nv= ('2500.00', '575.00')
        else:
            nv= ('100.00', '23.00') 
                    
        zakup= self.assertXpath(root, './ZakupWiersz')
        self.assertXmlEquivalentOutputs(self.node_xml(zakup), """
            <ZakupWiersz typ="G">
                <LpZakupu>1</LpZakupu>
                <NazwaWystawcy>FIRMA1</NazwaWystawcy>
                <AdresWystawcy>WARSZAWA 01-920, KOPERNIKA 1</AdresWystawcy>
                <NrIdWystawcy>6665554433</NrIdWystawcy>
                <NrFaktury>FAK1<!--ZKU--></NrFaktury>
                <DataWplywuFaktury>2016-01-02</DataWplywuFaktury>
                
                <K_45>{}</K_45><K_46>{}</K_46>    
            </ZakupWiersz>
        """.format(*nv))
        
        # Podsumowanie zakupów
        
        zakup_ctrl= self.assertXpath(root, './ZakupCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(zakup_ctrl), """
            <ZakupCtrl>
                <LiczbaWierszyZakupow>1</LiczbaWierszyZakupow>
                <PodatekNaliczony>{}</PodatekNaliczony>
            </ZakupCtrl>
        """.format(nv[1]))
        
        
    def test_zakup_pozycje_zak(self):

        # Skorygowanie początku okresu aby policzyła się korekta
        self.jpk.dataod= datetime.date(2016,7,1)
        self.jpk.datado= datetime.date(2016,7,31)        
        self.jpk.save()

        # Prewspółczynniki
        
        fk.DefZrv.testowe(2016, 'OZN', 50)
        fk.DefZrv.testowe(2016, 'OZ', 25)

        # Faktury zakupowe
                
        # Nieuwzględniana z powodu okresu daty deklaracji
        fk.Zak.testowe('ZKU', 'FAK1', self.kon, '2016-08-02', '2016-08-02', '2016/08', 
                       kos_w_net= 240.00, kos_w_vat= 55.20)

        # Faktury uwzględniane
                
        fk.Zak.testowe('ZKU', 'FAK2', self.kon, '2016-07-02', '2016-07-02', '2016/07',
            kos_w_net= 100.00, kos_w_vat= 23.00, # OZN/50% - 11.50
            soz_p_net= 250.00, soz_p_vat= 17.50, # OZ/25% - 4,38
            )
        
        zak= fk.Zak.testowe('ZKU', 'FAK3', self.kon, '2016-07-12', '2016-07-12', '2015/07', 
            kos_w_net= 200.00, kos_w_vat= 46.00, # OZN/50% +23,00
            soz_i_net= 100.00, soz_i_vat= 23.00, # OZ/25% 5,75
            )
        fk.ZakZrv.testowe(zak, 200, 46, 'OZN', 'P', 50)
        fk.ZakZrv.testowe(zak, 100, 23, 'OZ', 'I', 25)

        # Utworzenie XML
                                    
        root= self.get_jpk_xml()
        
        # Sprawdzenie istnienia elementów podrzednych
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1',
                                      './SprzedazCtrl', 
                                      './ZakupWiersz[@typ="G"]', './ZakupCtrl'))
        
        
        self.assertXpathCount(root, './ZakupWiersz', 2)
        
        if settings.FIRMA == 'gig':
            nv2= ('112.50', '15.88')
        else:
            nv2= ('250.00', '4.38')
            
        zakup= self.assertXpath(root, './ZakupWiersz[NrFaktury="FAK2"]')
        self.assertXmlEquivalentOutputs(self.node_xml(zakup), """
            <ZakupWiersz typ="G">
                <LpZakupu>1</LpZakupu>
                <NazwaWystawcy>FIRMA1</NazwaWystawcy>
                <AdresWystawcy>WARSZAWA 01-920, KOPERNIKA 1</AdresWystawcy>
                <NrIdWystawcy>6665554433</NrIdWystawcy>
                <NrFaktury>FAK2<!--ZKU--></NrFaktury>
                <DataWplywuFaktury>2016-07-02</DataWplywuFaktury>
                
                <K_45>{}</K_45><K_46>{}</K_46>    
            </ZakupWiersz>
        """.format(*nv2))            
            
        if settings.FIRMA == 'gig':
            nv3= ('25.00', '5.75', '100.00', '23.00')
        else:
            nv3= ('100.00', '5.75', '200.00', '23.00')
            
        zakup= self.assertXpath(root, './ZakupWiersz[NrFaktury="FAK3"]')
        self.assertXmlEquivalentOutputs(self.node_xml(zakup), """
            <ZakupWiersz typ="G">
                <LpZakupu>2</LpZakupu>
                <NazwaWystawcy>FIRMA1</NazwaWystawcy>
                <AdresWystawcy>WARSZAWA 01-920, KOPERNIKA 1</AdresWystawcy>
                <NrIdWystawcy>6665554433</NrIdWystawcy>
                <NrFaktury>FAK3<!--ZKU--></NrFaktury>
                <DataWplywuFaktury>2016-07-12</DataWplywuFaktury>
                
                <K_43>{}</K_43><K_44>{}</K_44>
                <K_45>{}</K_45><K_46>{}</K_46>    
            </ZakupWiersz>
        """.format(*nv3))
                    
        # Podatek naliczony od zakupów inwestycyjnych
        self.assertXpathSum(root, './ZakupWiersz/K_43', dec(nv3[0])) # netto * wsp
        self.assertXpathSum(root, './ZakupWiersz/K_44', dec(nv3[1])) # vat * wsp
        
        # Podatek naliczony od pozostałych zakupów
        self.assertXpathSum(root, './ZakupWiersz/K_45', dec(nv2[0])+dec(nv3[2])) # netto * wsp
        self.assertXpathSum(root, './ZakupWiersz/K_46', dec(nv2[1])+dec(nv3[3])) # vat * wsp           
            
        # Podsumowanie zakupów
        
        zakup_ctrl= self.assertXpath(root, './ZakupCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(zakup_ctrl), """
            <ZakupCtrl>
                <LiczbaWierszyZakupow>2</LiczbaWierszyZakupow>
                <PodatekNaliczony>{}</PodatekNaliczony>
            </ZakupCtrl>
        """.format('44.63' if settings.FIRMA == 'gig' else '33.13'))

        
    def test_korekta_pozostalych_nabyc(self):

        # Skorygowanie początku okresu aby policzyła się korekta
        self.jpk.dataod= datetime.date(2016,1,1)
        self.jpk.datado= datetime.date(2016,1,31)        
        self.jpk.save()

        # Faktura z bieżącego roku nie uwzględniana w korekcie z powodu okresu
        fk.Zak.testowe('ZKU', 'FAK1', self.kon, '2016-07-02', '2016-07-02', '2016/07', kos_w_net= 240.00, kos_w_vat= 55.20) 
        
        # Faktury do korekty

        # Faktury z roku korygowanego
        
        kon15= fk.Kon.testowe('330001', '6665554433', dbs= 'fk15')
                
        # Zerowa => nieuwzględniana        
        fk.Zak.testowe('ZKU', 'FAK0', kon15, '2015-04-01', '2015-04-01', '2015/04', kos_w_net= 0.00, kos_w_vat= 0.00, dbs= 'fk15') 
        
        fk.Zak.testowe('ZKU', 'FAK2', kon15, '2015-07-02', '2015-07-02', '2015/07',
             kos_w_net= 100.00, kos_w_vat= 23.00, # OZN - korekta +2,3
             soz_p_net= 100.00, soz_p_vat= 10.00, # OZ - korekta -1,0
             dbs= 'fk15')
        
        zak= fk.Zak.testowe('ZKU', 'FAK3', kon15, '2015-08-02', '2015-08-02', '2015/08', 
            kos_w_net= 200.00, kos_w_vat= 14.00, # OZN +1,4
            soz_p_net= 100.00, soz_p_vat= 7.00, # OZ -0.7
            dbs= 'fk15') 
        fk.ZakZrv.testowe(zak, 200, 14, 'OZN', 'P', 80, dbs= 'fk15') # +1,4
        fk.ZakZrv.testowe(zak, 100, 7, 'OZ', 'P', 80, dbs= 'fk15') # -0,7        
        # inwestycyjne więc nie uwzględniane, niezgodność z rozliczeniem faktury
        fk.ZakZrv.testowe(zak, 100, 7, 'OZ', 'I', 80, dbs= 'fk15') 

        # Faktury z roku poprzedzającego korygowany
        kon14= fk.Kon.testowe('330001', '6665554433', dbs= 'fk14')         
        fk.Zak.testowe('ZKU', 'FAK4', kon14, '2015-01-02', '2015-01-02', '2014/12', 
            kos_w_net= 300.00, kos_w_vat= 37.00, dbs= 'fk14') # OZN +3,7
        
        # Utworzenie XML
                                    
        root= self.get_jpk_xml()
        
        # Sprawdzenie istnienia elementów podrzednych
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1',
                                      './SprzedazCtrl', 
                                      './ZakupWiersz[@typ="G"]', './ZakupCtrl'))
        
        if settings.KOREKTA_VAT_LACZNIE:
            
            zakup= self.assertXpath(root, './ZakupWiersz')
            
            if settings.FIRMA == 'gig':
                self.assertXmlEquivalentOutputs(self.node_xml(zakup), """
                    <ZakupWiersz typ="G">
                        <LpZakupu>1</LpZakupu>
                        <NazwaWystawcy>Główny Instytut Górnictwa</NazwaWystawcy>
                        <AdresWystawcy>Katowice 40-166, Plac Gwarków 1</AdresWystawcy>
                        <NrIdWystawcy>6340126016</NrIdWystawcy>
                        <NrFaktury>KOREKTA ROCZNA<!--KOR-P--></NrFaktury>
                        <DataWplywuFaktury>2016-01-01</DataWplywuFaktury>
                        
                        <K_48>5.70</K_48>    
                    </ZakupWiersz>
                """)
                
            if settings.FIRMA == 'ichp':      
                self.assertXmlEquivalentOutputs(self.node_xml(zakup), """
                    <ZakupWiersz typ="G">
                        <LpZakupu>1</LpZakupu>
                        <NazwaWystawcy>Instytut Chemii Przemysłowej, im. prof. I. Mościckiego</NazwaWystawcy>
                        <AdresWystawcy>Warszawa 01-793, Rydygiera 8</AdresWystawcy>
                        <NrIdWystawcy>5250007939</NrIdWystawcy>
                        <NrFaktury>KOREKTA ROCZNA<!--KOR-P--></NrFaktury>
                        <DataWplywuFaktury>2016-01-01</DataWplywuFaktury>
                        
                        <K_48>-0.30</K_48>    
                    </ZakupWiersz>
                """)
                        
        # Podsumowanie zakupów
        
        zakup_ctrl= self.assertXpath(root, './ZakupCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(zakup_ctrl), """
            <ZakupCtrl>
                <LiczbaWierszyZakupow>1</LiczbaWierszyZakupow>
                <PodatekNaliczony>{}</PodatekNaliczony>
            </ZakupCtrl>
        """.format('5.70' if settings.FIRMA == 'gig' else '-0.30'))
        
        
        
@override_settings(FIRMA='gig')
class GigVatTestCase(VatTestCase, JpkTestCase):

    def test_gig_sprzedaz_stawki_fak(self):

        dok= fk.MagDok.testowe('57', 1, self.kon, '2016-07-02', '2016-07-19', '2016-07-22')
        # Wszystkie poprawne stawki VAT
        for stawka in ('23%', '22%', ' 8%', ' 7%', ' 5%', ' 0%', 'ZW.', 'W0%', 'E0%', 'NO.', 'OO.', 'AA.'):
            fk.MagWiersz.testowe(dok, self.zlc, 100, stawka)
                
        root= self.get_jpk_xml()
        
        # Sprawdzenie istnienia elementów podrzednych
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1',
                                      './SprzedazWiersz[@typ="G"]', './SprzedazCtrl', 
                                      './ZakupCtrl'))

        # Sprzedaż

        # Wiersz/pozycja z niepoprawną stawką nie będzie uwzględniony w pliku JPK         
        self.assertJpkBlad('SPR', '570001/323/16', 'Stawka VAT AA. niezakwalifikowana do żadnego pola deklaracji')
        
        sprzedaz= self.assertXpath(root, './SprzedazWiersz')
        self.assertXmlEquivalentOutputs(self.node_xml(sprzedaz), """
            <SprzedazWiersz typ="G">
                <LpSprzedazy>1</LpSprzedazy>
                 <DataSprzedazy>2016-07-19</DataSprzedazy>
                <DataWystawienia>2016-07-02</DataWystawienia>
                
                <NrDokumentu>570001/323/16<!--FV--></NrDokumentu>
                <NazwaNabywcy>FIRMA1</NazwaNabywcy>
                <AdresNabywcy>WARSZAWA 01-920, KOPERNIKA 1</AdresNabywcy>
                
                <K_10>100.00</K_10>
                <K_11>100.00</K_11>
                <K_13>100.00</K_13>
                <K_15>100.00</K_15>
                <K_16>5.00</K_16>
                <K_17>200.00</K_17>
                <K_18>15.00</K_18>
                <K_19>200.00</K_19>
                <K_20>45.00</K_20>
                <K_21>100.00</K_21>
                <K_22>100.00</K_22>
                <K_31>100.00</K_31>   
            </SprzedazWiersz>
        """)
        
        # Podsumowanie sprzedaży
        
        sprzedaz_ctrl= self.assertXpath(root, './SprzedazCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(sprzedaz_ctrl), """
            <SprzedazCtrl>
                <LiczbaWierszySprzedazy>1</LiczbaWierszySprzedazy>
                <PodatekNalezny>65.00</PodatekNalezny>
            </SprzedazCtrl>
        """)

                
    def test_gig_sprzedaz_faktury_zakupowe(self):

        RODZAJE_ZAKUPOW= {'WNT/1': 23, 'IU/1': 27, 'IU/2': 29, 'PN/1': 32, 'OO/1': 34}
        for nr_faktury in RODZAJE_ZAKUPOW:
            rodzaj= nr_faktury.split('/')[0]
            kon= self.kon_ue if nr_faktury == 'IU/2' else self.kon 
            fk.Zak.testowe(rodzaj, nr_faktury, kon, '2016-07-02', '2016-07-02', '2016/07', 
                 kos_w_net= 240.00, kos_w_vat= 55.20, 
                 d_wyst= '2016-07-11' if nr_faktury != 'IU/2' else None)

        # Nieokreślony numer faktury => sygnalizacja błędu
        zak_nrf= fk.Zak.testowe('WNT', None, kon, '2016-07-02', '2016-07-02', '2016/07', 
             kos_w_net= 100.00, kos_w_vat= 23.00, 
             d_wyst= '2016-07-11')
        
        # NIP kontrahenta wygląda jak UE ale nie jest tak oznaczony => sygnalizacja błędu danych
        kon_ue= fk.Kon.testowe('550001', 'DE6665554433', idtyp= 'NIP')
        fk.Zak.testowe('WNT', 'FAK1', kon_ue, '2016-07-02', '2016-07-02', '2016/07', 
             kos_w_net= 0.00, kos_w_vat= 0.00, 
             d_wyst= '2016-07-11')        
            
        root= self.get_jpk_xml()
        
        # Sprawdzenie istnienia elementów podrzednych
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1',
                                      './SprzedazWiersz[@typ="G"]', './SprzedazCtrl', 
                                      './ZakupWiersz[@typ="G"]', './ZakupCtrl'))

        # Sprzedaż
        
        self.assertJpkBlad('SPR/ZAK', 'IU/2', 'Nieokreślona data wystawienia faktury zakupu')
        self.assertJpkBlad('SPR/ZAK', zak_nrf.zak_id, 'Nieokreślony numer dokumentu/faktury zakupu') 
        self.assertJpkBlad('SPR/ZAK', 'FAK1', 'NIP kontrahenta ({}) wygląda na NIPUE ale nie jest tak oznaczony'.format(kon_ue.nr_kon))        
                                
        self.assertXpathCount(root, './SprzedazWiersz', len(RODZAJE_ZAKUPOW)+2)
        self.assertXpathsUniqueValue(root, './SprzedazWiersz/LpSprzedazy')
        self.assertXpathValues(root, './SprzedazWiersz/LpSprzedazy/text()', [repr(x) for x in range(1,len(RODZAJE_ZAKUPOW)+3)])
        
        for nr_faktury in RODZAJE_ZAKUPOW:
            rodzaj= nr_faktury.split('/')[0]
            sprzedaz= self.assertXpath(root, './SprzedazWiersz[NrDokumentu="{}"]'.format(nr_faktury))
            self.assertXmlEquivalentOutputs(self.node_xml(sprzedaz), """
                <SprzedazWiersz typ="G">
                    <LpSprzedazy>...</LpSprzedazy>
                     
                    <DataWystawienia>{4}</DataWystawienia>
                    
                    <NrDokumentu>{0}<!--{1}--></NrDokumentu>
                    <NazwaNabywcy>FIRMA1</NazwaNabywcy>
                    <AdresNabywcy>WARSZAWA 01-920, KOPERNIKA 1</AdresNabywcy>

                    <K_{2}>240.00</K_{2}><K_{3}>55.20</K_{3}>
                </SprzedazWiersz>
            """.format(nr_faktury, rodzaj, RODZAJE_ZAKUPOW[nr_faktury], RODZAJE_ZAKUPOW[nr_faktury]+1,
                       '2016-07-11' if nr_faktury != 'IU/2' else '')
            )
        
        # Podsumowanie sprzedaży
        
        sprzedaz_ctrl= self.assertXpath(root, './SprzedazCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(sprzedaz_ctrl), """
            <SprzedazCtrl>
                <LiczbaWierszySprzedazy>7</LiczbaWierszySprzedazy>
                <PodatekNalezny>299.00</PodatekNalezny>
            </SprzedazCtrl>
        """)
        
        # Zakupy
        
        self.assertXpathCount(root, './ZakupWiersz', len(RODZAJE_ZAKUPOW)+1)
        self.assertXpathsUniqueValue(root, './ZakupWiersz/LpZakupu')
        self.assertXpathValues(root, './ZakupWiersz/LpZakupu/text()', [repr(x) for x in range(1,len(RODZAJE_ZAKUPOW)+3)])
        self.assertXpathSum(root, './ZakupWiersz/K_45', decimal.Decimal('1170.00'))
        self.assertXpathSum(root, './ZakupWiersz/K_46', decimal.Decimal('269.10'))
                        
        for nr_faktury in RODZAJE_ZAKUPOW:
            rodzaj= nr_faktury.split('/')[0]            
            zakup= self.assertXpath(root, './ZakupWiersz[NrFaktury="{}"]'.format(nr_faktury))
            nip= 'DE' if RODZAJE_ZAKUPOW[nr_faktury] == 29 else ''
            self.assertXmlEquivalentOutputs(self.node_xml(zakup), """
                <ZakupWiersz typ="G">
                    <LpZakupu>...</LpZakupu>
                    <NazwaWystawcy>FIRMA1</NazwaWystawcy>
                    <AdresWystawcy>WARSZAWA 01-920, KOPERNIKA 1</AdresWystawcy>
                    <NrIdWystawcy>{2}6665554433</NrIdWystawcy>
                    <NrFaktury>{0}<!--{1}--></NrFaktury>
                    <DataWplywuFaktury>2016-07-02</DataWplywuFaktury>
                    
                    <K_45>216.00</K_45><K_46>49.68</K_46>    
                </ZakupWiersz>
            """.format(nr_faktury, rodzaj, nip))
                    
        # Podsumowanie zakupów
        
        zakup_ctrl= self.assertXpath(root, './ZakupCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(zakup_ctrl), """
            <ZakupCtrl>
                <LiczbaWierszyZakupow>6</LiczbaWierszyZakupow>
                <PodatekNaliczony>269.10</PodatekNaliczony>
            </ZakupCtrl>
        """)


    def test_gig_korekta_srodkow_trwalych(self):

        # Skorygowanie początku okresu aby policzyła się korekta
        self.jpk.dataod= datetime.date(2016,1,1)
        self.jpk.save()

        mkv1= fk.SrtMkv.testowe('800/1', 'NAZWA1')
        fk.SrtVat.testowe(mkv1, 11.22)
        
        # Nie uwzględniana w raporcie
        mkv2= fk.SrtMkv.testowe('800/2', 'NAZWA2')
        fk.SrtVat.testowe(mkv2, 0.00)
                
        with self.settings(KOREKTA_VAT_LACZNIE= True):
            
            root= self.get_jpk_xml()
                    
            # Sprawdzenie istnienia elementów podrzednych
            self.assertXpathsExist(root, ('./Naglowek', './Podmiot1',
                                          './SprzedazCtrl', 
                                          './ZakupWiersz[@typ="G"]', './ZakupCtrl'))
            
            # Jedną sumaryczną pozycją
            
            zakup= self.assertXpath(root, './ZakupWiersz')
            self.assertXmlEquivalentOutputs(self.node_xml(zakup), """
                <ZakupWiersz typ="G">
                    <LpZakupu>1</LpZakupu>
                    <NazwaWystawcy>Główny Instytut Górnictwa</NazwaWystawcy>
                    <AdresWystawcy>Katowice 40-166, Plac Gwarków 1</AdresWystawcy>
                    <NrIdWystawcy>6340126016</NrIdWystawcy>
                    <NrFaktury>KOREKTA ROCZNA<!--KOR-T--></NrFaktury>
                    <DataWplywuFaktury>2016-01-01</DataWplywuFaktury>
                    
                    <K_47>11.22</K_47>    
                </ZakupWiersz>
            """) 
                
        with self.settings(KOREKTA_VAT_LACZNIE= False): 
            
            root= self.get_jpk_xml()
                    
            # Sprawdzenie istnienia elementów podrzednych
            self.assertXpathsExist(root, ('./Naglowek', './Podmiot1',
                                          './SprzedazCtrl', 
                                          './ZakupWiersz[@typ="G"]', './ZakupCtrl'))
                                          
            # Każda pozycja inwentarzowa osobno
            
            zakup= self.assertXpath(root, './ZakupWiersz')
            self.assertXmlEquivalentOutputs(self.node_xml(zakup), """
                <ZakupWiersz typ="G">
                    <LpZakupu>1</LpZakupu>
                    <NazwaWystawcy>NAZWA1</NazwaWystawcy>
                    <AdresWystawcy>ZMIANA PRZEZNACZENIA</AdresWystawcy>
                    <NrIdWystawcy>800/1</NrIdWystawcy>
                    <NrFaktury>FAK1<!--KVM--></NrFaktury>
                    <DataWplywuFaktury>2016-02-01</DataWplywuFaktury>
                    
                    <K_47>11.22</K_47>    
                </ZakupWiersz>
            """)            
        
        # Podsumowanie zakupów
        
        zakup_ctrl= self.assertXpath(root, './ZakupCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(zakup_ctrl), """
            <ZakupCtrl>
                <LiczbaWierszyZakupow>1</LiczbaWierszyZakupow>
                <PodatekNaliczony>11.22</PodatekNaliczony>
            </ZakupCtrl>
        """)          
        


@override_settings(FIRMA='ichp')
class IchpVatTestCase(VatTestCase, JpkTestCase):

    def test_ichp_sprzedaz_rodzaje_stawki_fak(self):
        
        RODZAJE= ('ET', 'EU', 'UI', 'UT', 'UU', '40')
        for rodz_te in RODZAJE:
            dok= fk.MagDok.testowe(rodz_te, 1, self.kon, '2016-07-02', '2016-07-19', '2016-07-22')
            # Wszystkie poprawne stawki VAT
            for stawka in ('23%', '22%', ' 8%', ' 7%', ' 5%', ' 3%', ' 0%', 'ZW.', 'NP.', 'OO.', 'AA.'):
                fk.MagWiersz.testowe(dok, self.zlc, 100, stawka)
              
        dok= fk.MagDok.testowe('57', 1, self.kon, '2016-07-02', '2016-07-19', '2016-07-22')
        # Wszystkie poprawne stawki VAT
        for stawka in ('23%', '22%', ' 8%', ' 7%', ' 5%', ' 3%', ' 0%', 'ZW.', 'NP.', 'OO.', 'AA.'):
            fk.MagWiersz.testowe(dok, self.zlc, 100, stawka)
                                
        root= self.get_jpk_xml()
        
        # Sprawdzenie istnienia elementów podrzednych
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1',
                                      './SprzedazWiersz[@typ="G"]', './SprzedazCtrl', 
                                      './ZakupCtrl'))

        # Sprzedaż

        # Wiersz/pozycja z niepoprawną stawką nie będzie uwzględniony w pliku JPK
        self.assertJpkBlad('SPR', '570001/323/16', 'Pozycja: rodzaj sprzedaży(57 )/stawka VAT(AA.) niezakwalifikowana do żadnego pola deklaracji')

        self.assertXpathCount(root, './SprzedazWiersz', len(RODZAJE)+1)
        
        for rodz_te, pozycje in {
                'EU': [(10, 100), (11, 1000), (12, 1000)],
                'ET': [(21, 1100)],
                '40': [(22, 1100)],                                
                'UT': [(23, 1100), (24, 68)],
                'UI': [(27, 1100), (28, 68)],
                'UU': [(29, 1100), (30, 68)],
            }.items(): 
             
            pola= ""
            for p, w in pozycje:
                pola += '<K_{0}>{1}.00</K_{0}>'.format(p, w)
                
            sprzedaz= self.assertXpath(root, './SprzedazWiersz[NrDokumentu="{}0001/323/16"]'.format(rodz_te))
            self.assertXmlEquivalentOutputs(self.node_xml(sprzedaz), """
                <SprzedazWiersz typ="G">
                    <LpSprzedazy>...</LpSprzedazy>
                     <DataSprzedazy>2016-07-19</DataSprzedazy>
                    <DataWystawienia>2016-07-02</DataWystawienia>
                    
                    <NrDokumentu>{0}0001/323/16<!--{0}--></NrDokumentu>
                    <NazwaNabywcy>FIRMA1</NazwaNabywcy>
                    <AdresNabywcy>WARSZAWA 01-920, KOPERNIKA 1</AdresNabywcy>
                    {1}
                </SprzedazWiersz>
            """.format(rodz_te, pola))
        
        sprzedaz= self.assertXpath(root, './SprzedazWiersz[NrDokumentu="570001/323/16"]')
        self.assertXmlEquivalentOutputs(self.node_xml(sprzedaz), """
            <SprzedazWiersz typ="G">
                <LpSprzedazy>...</LpSprzedazy>
                 <DataSprzedazy>2016-07-19</DataSprzedazy>
                <DataWystawienia>2016-07-02</DataWystawienia>
                
                <NrDokumentu>570001/323/16<!--57--></NrDokumentu>
                <NazwaNabywcy>FIRMA1</NazwaNabywcy>
                <AdresNabywcy>WARSZAWA 01-920, KOPERNIKA 1</AdresNabywcy>
                
                <K_10>200.00</K_10>
                <K_11>100.00</K_11>
                <K_13>100.00</K_13>
                <K_15>200.00</K_15><K_16>8.00</K_16>
                <K_17>200.00</K_17><K_18>15.00</K_18>
                <K_19>200.00</K_19><K_20>45.00</K_20> 
            </SprzedazWiersz>
        """)
                    
        # Podsumowanie sprzedaży
        
        sprzedaz_ctrl= self.assertXpath(root, './SprzedazCtrl')
        self.assertXmlEquivalentOutputs(self.node_xml(sprzedaz_ctrl), """
            <SprzedazCtrl>
                <LiczbaWierszySprzedazy>7</LiczbaWierszySprzedazy>
                <PodatekNalezny>476.00</PodatekNalezny>
            </SprzedazCtrl>
        """)
    