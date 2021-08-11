# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, os
from django.test import mock

from app import wyslij
from app.models import Plik, Storage, Blad
from app.utils import OperacjaNiedozwolona

from .. import JpkTestCase

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto import Random
from Crypto.Hash import SHA

import logging
logging.disable(logging.ERROR)


class WyslijTests(JpkTestCase):
    """
    Zakładamy tutaj BS=16
    """

    JPK_VAT_100_FILENAME= os.path.join(os.path.dirname(__file__), 'JPK_VAT-100.xml')
    status_p_json= os.path.join(os.path.dirname(__file__), 'status-p.json')
    status_t_json= os.path.join(os.path.dirname(__file__), 'status-t.json')
        
    M_REFERENCE= '9b3476ca01569d3c000000b0739ca385'
    M_BLOB_NAME= '046c4db1-64a9-4ba4-afda-85dcc07fe784'

    INITUPLOAD_200= '''{{
        "ReferenceNumber":"{}",
        "TimeoutInSec":900,
        "RequestToUploadFileList":[{{
             "BlobName":"{}",
             "FileName":"jpk6.zip",
             "Url":"https://taxdocumentstorage07tst.blob.core.windows.net/9b3476ca01569d3c000000b0739ca385/046c4db1-64a9-4ba4-afda-85dcc07fe784?sv=2015-07-08&sr=b&si=9b3476ca01569d3c000000b0739ca385&sig=vvjFBD1abUa%2B%2FIPHSgY03ty1v94suS0NbBPIu4HkQLE%3D",
             "Method":"PUT",
             "HeaderList":[{{
                 "Key":"Content-MD5",
                 "Value":"7hmBCcHZmhg02LtUWP5oCg=="
                }},{{
                 "Key":"x-ms-blob-type",
                 "Value":"BlockBlob"
                }}
            ]
        }}]
    }}'''.format(M_REFERENCE, M_BLOB_NAME)
                     
    def setUp(self):
                 
        # Pusty JPK_VAT za 2016/07
        self.jpk= Plik.objects.create(
                    kod= 'JPK_VAT', 
                    dataod= datetime.date(2016,7,1),
                    datado= datetime.date(2016,7,31),
                    utworzony_user= 'test',
                    stan= 'GOTOWY',

                    # Fiksujemy id aby nazwa pliku była zawsze taka sama (JPK_VAT-100)
                    id= 100,
                    # Fiksujemy moment utworzenia bo jest w pliku XML                                    
                    utworzony= datetime.datetime(2016, 10, 5, 17, 24, 29),
                ) 
            
            
    def setup_wysylka(self, **kwargs):
        
        Storage.objects.create(
                        jpk= self.jpk,
                        sign_xml= b'', sign_user= 'test', aes_key= '', enc_key= '', aes_iv= '', 
                        jpk_aes= b'', xml_name= '',
                        xml_len= 0, xml_hash= '', zip_name= '', zip_len= 0, zip_hash= '',
                        xades_time= datetime.datetime.now(),
                        xades_xml= '<xml></xml>',
                        xades_user= 'test', 
                        **kwargs
                    )
        
        wysylka= wyslij.WysylkaMF(self.jpk)
        wysylka.user= 'test'
        
        return wysylka
    
    
    def setup_initupload(self, m_post):
        m_post.return_value= mock.Mock(status_code= 200, text= self.INITUPLOAD_200)
    
    
    def setup_finish(self, m_post, rc2):
        
        m_post.side_effect= [
            mock.Mock(status_code= 200, text= self.INITUPLOAD_200), 
            rc2
        ]
        
                                            
    def test_pad(self):
        w= wyslij.InituploadMF(self.jpk)
        
        self.assertEqual(16, w.BS, 'Block size')
        self.assertEqual(b'\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10', w.pad(b''), 'Padding 0')
        self.assertEqual(b'1234567890123456\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10', w.pad(b'1234567890123456'), 'Padding 16')
        self.assertEqual(b'123456789012345\x01', w.pad(b'123456789012345'), 'Padding 1')               
        self.assertEqual(b'12345678901234\x02\x02', w.pad(b'12345678901234'), 'Padding 2')
        self.assertEqual(b'12345678'+(b'\x08'*8), w.pad(b'12345678'), 'Padding 8')
        self.assertEqual(b'1'+(b'\x0f'*15), w.pad(b'1'), 'Padding 15')


    def test_unpad(self):
        w= wyslij.InituploadMF(self.jpk)
                
        for x in (b'', b'1234567890123456', b'12345678', b'123', b'1'):        
            self.assertEqual(x, w.unpad(w.pad(x)), 'Unpadding {}'.format(x))


    def test_rsa_decryption(self):
        
        random_generator= Random.new().read
        key= RSA.generate(1024, random_generator)
        
        message= b'Lorem ipsum dolor sit amet'
        
        # aby później rozkodować potrzebna jest para kluczy
        # aby tylko zakodować wystarczyłby public_key
        # public_key= key.publickey()
        
        rsa_cipher= PKCS1_v1_5.new(key) 
        enc_key= rsa_cipher.encrypt(message)
        
        sentinel= Random.new().read(15+SHA.digest_size)
        dec= rsa_cipher.decrypt(enc_key, sentinel)
        
        self.assertEqual(message, dec)
        
                        
    @mock.patch('app.wyslij.Random')
    @mock.patch('time.time')
    def test_plik_kontrolny(self, m_time, m_random):
        """
        1. Generowanie pliku kontrolnego
        """

        # Zawartość pliku jest nieistotna, ważne aby była stała
        self.jpk.xml= open(self.JPK_VAT_100_FILENAME, 'r').read()
        
        # W zipie wpisywana jest data/czas modyfikacji ustalany z time.time()
        # dlatego określamy stałą wartość aby zip był zawsze jednakowy
        m_time.return_value= 1475692250.8109133
                         
        # Fiksujemy klucz szyfrowania i wartość inicjalizacyjną dla AES
        # które są ustalane z Random.new().read()
        m_read= mock.Mock(side_effect= [
            b'w\xe2\xa8\xe3\x0cw\x00\xdfVv\xc0/\xceg\xb4y\x89xO%\xa8\x8c \x99\x0e~F8\xe2+\xdc\xc9', 
            b'\xc5\xber\x03T\xfb\x05\xf9\xff\x8c\xf2am2L&'])
        m_random.new.return_value.read= m_read

        
        storage= wyslij.InituploadMF(self.jpk).plik_kontrolny('wlodek', 'T')
    
    
        # Sprawdzenie poprawności wywołań Random.new().read
        self.assertEqual([mock.call(32), mock.call(16)], m_read.mock_calls)
        
        self.assertXmlDocument(storage.sign_xml.encode('utf-8'))
                
        # Zaszyfrowany RSA/PKCS1 klucz szyfrowania za każdym razem jest inny więc go pomijamy
        # Co najwyżej możemy sprawdzić jego długość
        self.assertXmlEquivalentOutputs(storage.sign_xml.encode('utf-8'), """
            <InitUpload xmlns="http://e-dokumenty.mf.gov.pl">
                <DocumentType>JPK</DocumentType>
                <Version>01.02.01.20160617</Version>
                <EncryptionKey algorithm="RSA" mode="ECB" padding="PKCS#1" encoding="Base64">...</EncryptionKey>
                <DocumentList>
                    <Document>
                        <FormCode systemCode="JPK_VAT (1)" schemaVersion="1-0">JPK_VAT</FormCode>
                        <FileName>JPK_VAT-100.xml</FileName>
                        <ContentLength>1400</ContentLength>
                        <HashValue algorithm="SHA-256" encoding="Base64">m/pHd29tyhswP51uvX4XE3XCF/+beljHc+Puk2ZGrNk=</HashValue>
                        <FileSignatureList filesNumber="1">
                            <Packaging>
                                <SplitZip type="split" mode="zip"/>
                            </Packaging>
                            <Encryption>
                                <AES size="256" block="16" mode="CBC" padding="PKCS#7">
                                    <IV bytes="16" encoding="Base64">xb5yA1T7Bfn/jPJhbTJMJg==</IV>
                                </AES>
                            </Encryption>
                            <FileSignature>
                                <OrdinalNumber>1</OrdinalNumber>
                                <FileName>JPK_VAT-100.zip</FileName>
                                <ContentLength>802</ContentLength>
                                <HashValue algorithm="MD5" encoding="Base64">VyjvIVrNAEfhjPRthQt79w==</HashValue>
                            </FileSignature>
                        </FileSignatureList>
                    </Document>
                </DocumentList>
            </InitUpload>
        """)


    def test_plik_kontrolny_plik_nie_utworzony(self):
        """
        Plik musi być utworzony aby można było generować dla niego initupload.xml
        Jeżeli plik ma stan 'W KOLEJCE', 'TWORZENIE', 'PROBLEMY' to nie jest utworzony.
        """

        self.jpk.xml= ''
        self.jpk.save()
        for stan in ('W KOLEJCE', 'TWORZENIE', 'PROBLEMY'):
            self.jpk.stan= stan
            self.jpk.save()
            with self.assertRaises(OperacjaNiedozwolona):        
                wyslij.InituploadMF(self.jpk).plik_kontrolny('wlodek', 'T')
        

    def test_plik_kontrolny_plik_nietykalny(self):
        """
        Jeżeli plik jest nietykalny to nie można dla niego tworzyć pliku kontrolnego.
        Plik jest nietykalny jeżeli
        a) ma UPO
        b) ma status 'SPRAWDZANY'
        c) ostatni status ma kod (120, 301, 302, 303) - czyli stan = SPRAWDZANY?
        """

        self.jpk.xml= ''
        self.jpk.upo= 'UPO'
        self.jpk.save()
        with self.assertRaises(OperacjaNiedozwolona):        
            wyslij.InituploadMF(self.jpk).plik_kontrolny('wlodek', 'P')

        self.jpk.upo= None
        self.jpk.stan= 'SPRAWDZANY'
        with self.assertRaises(OperacjaNiedozwolona):        
            wyslij.InituploadMF(self.jpk).plik_kontrolny('wlodek', 'T')
                    
           
    def test_plik_kontrolny_bledy(self):
        """
        Plik nie może mieć błędów aby można było generować dla niego initupload.xml
        """

        self.jpk.xml= ''
        self.jpk.save()
        
        blad= Blad(zrodlo='', dokument='D', blad= 'B')
        self.jpk.blad_set.add(blad, bulk= False)
        
        with self.assertRaises(OperacjaNiedozwolona):        
            wyslij.InituploadMF(self.jpk).plik_kontrolny('wlodek', 'P')
                
                                        
    @mock.patch('requests.post')        
    def test_wysylka_initupload(self, m_post):
        """
        Jeżeli wysyłka pliku kontrolnego zakończy się sukcesem 
        (status code 200) to 
        
        a) storage pliku zawiera numer referencyjny
        b) obiekt interfejsu/bramki zawiera listę plików (file_list)
        """        
        
        m_post.return_value= mock.Mock(status_code= 200, text= self.INITUPLOAD_200)

        wysylka= self.setup_wysylka(bramka= 'P')
    
        # Jeżeli wysyłka pliku kontrolnego zakończy się powodzeniem (no exception)

        wysylka.wysylka_initupload()

        # Storage pliku zawiera numer referencyjny
        self.assertEquals(self.M_REFERENCE, self.jpk.get_storage().reference, 'Niepoprawny numer referencyjny sesji')
        
        # Obiekt interfejsu zawiera listę plików
        self.assertEquals(self.M_BLOB_NAME, wysylka.mf_api.file_list[0].get('BlobName'), 'Niepoprawna lista plików do wysłania')
        
        
    @mock.patch('requests.post')        
    def test_wysylka_initupload_blad_polaczenia(self, m_post):
        """
        Jeżeli w czasie wysyłki wystąpi błąd sieciowy to 
        
        a) wyrzucany jest wyjątek
        b) odpowiednio ustawiany jest stan pliku
        
        c) sprawdzanie statusu jest przerywane
        """        
        
        m_post.side_effect= ConnectionError('Błąd połączenia')
        
        wysylka= self.setup_wysylka(bramka= 'T')
    
        # Jeżeli podczas wysyłki pliku kontrolnegowystąpi błąd połączenia 

        # Wyrzucany jest wyjątek
        with self.assertRaises(Exception) as e:
            wysylka.wysylka_initupload()

        # Stan pliku ustawiany jest odpowiednio    
        self.assertEquals('BŁĄD WYSYŁKI', self.jpk.stan, 'Niepoprawny stan pliku')
    
    
    @mock.patch('requests.post')        
    def test_wysylka_initupload_nie_200(self, m_post):
        
        m_post.return_value= mock.Mock(status_code= 400, text= '''{
                "Message": "Podpis negatywnie zweryfikowany",
                "Code": 120,
                "RequestId": "172dc3cc-5b97-48de-91dd-6903587cba19"
            }'''
        )
        
        wysylka= self.setup_wysylka(bramka= 'P')
    
        # Jeżeli wysyłka pliku kontrolnego się nie powiedzie to 
    
        # Wyrzucany jest wyjątek
        with self.assertRaises(Exception) as e:
            wysylka.wysylka_initupload()
            
        # Pdpowiedno ustawiany jest stan pliku
        self.assertEquals('BŁĄD WYSYŁKI', self.jpk.stan, 'Niepoprawny stan pliku')


    @mock.patch('requests.put')   
    @mock.patch('requests.post')        
    def test_wysylka_zip(self, m_post, m_put):
        """
        Jeżeli wysyłka archiwum zip zakończy się sukcesem 
        (status code 201) to 

        a) status pliku ustawiany jest na WYSYŁANY
        b) interfejs zawiera listę wysłanych plików
        """        
        
        self.setup_initupload(m_post)
        m_put.return_value= mock.Mock(status_code= 201, text= '')
        
        wysylka= self.setup_wysylka(bramka= 'P')
        wysylka.wysylka_initupload()
    
        # Jeżeli wysyłka archiwum zip zawierającego plik XML zakończy się 
        # powodzeniem (status code 201)

        wysylka.wysylka_zip()
        
        # Storage pliku zawiera numer referencyjny
        self.assertEqual('WYSYŁANY', self.jpk.stan, 'Niepoprawny status pliku')
        
        # Interfejs zawiera listę wysłanych plików
        self.assertEqual([self.M_BLOB_NAME], wysylka.mf_api.blobs, 'Niepoprawna lista wysłanych plików')
        

    @mock.patch('requests.put')   
    @mock.patch('requests.post')        
    def test_wysylka_zip_blad_polaczenia(self, m_post, m_put):
        """
        Jeżeli wysyłka archiwum zip zakończy się błędem połączenia 

        a) wyrzucany jest wyjątek aby przerwać przetwarzanie
        b) status pliku ustawiany jest na NIE WYSŁANY
        """        
        self.setup_initupload(m_post)
        m_put.side_effect= ConnectionError('Błąd połączenia')
        
        wysylka= self.setup_wysylka(bramka= 'T')
        wysylka.wysylka_initupload()
    
        # Jeżeli wysyłka archiwum zip zawierającego plik XML zakończy się 
        # niepowodzeniem

        with self.assertRaises(Exception) as e:
            wysylka.wysylka_zip()
        
        # Storage pliku zawiera numer referencyjny
        self.assertEqual('NIE WYSŁANY', self.jpk.stan, 'Niepoprawny status pliku')
        

    @mock.patch('requests.put')   
    @mock.patch('requests.post')        
    def test_wysylka_finish(self, m_post, m_put):
        """
        Jeżeli zapytanie zwróci status kod 200 to sesja zakończyła się poprawnie.
        W takim przypadku 
        
        a) stan pliku ustawiany jest na "SPRAWDZANY" (co powoduje 
        zablokowanie go do zmian).
        """        
        
        self.setup_finish(m_post, mock.Mock(status_code= 200, text= ''))
        m_put.return_value= mock.Mock(status_code= 201, text= '')
        
        wysylka= self.setup_wysylka(bramka= 'P')
        wysylka.wysylka_initupload()
        wysylka.wysylka_zip()
    
        # Jeżeli sesja zostanie zakończona poprawnie

        wysylka.wysylka_finish()
                
        # Storage pliku zawiera numer referencyjny
        self.assertEqual('SPRAWDZANY', self.jpk.stan, 'Niepoprawny status pliku')
        
        
    @mock.patch('requests.post')        
    def test_wysylka_finish_blad_polaczenia(self, m_post):
        """
        Jeżeli wystąpi błąd to stan pliku ustawiany jest na "NIE ODEBRANY".
        """        
        
        m_post.side_effect= Exception('Błąd połączenia')
        
        wysylka= self.setup_wysylka(bramka= 'T')
        wysylka.reference= self.M_REFERENCE
        wysylka.blobs= [self.M_BLOB_NAME]
    
        # Jeżeli sesja nie zakończyła się poprawnie

        wysylka.wysylka_finish()
                
        # Storage pliku zawiera numer referencyjny
        self.assertEqual('NIE ODEBRANY', self.jpk.stan, 'Niepoprawny status pliku')
                
  
    @mock.patch('requests.post')        
    def test_wysylka_finish_nie_200(self, m_post):
        """
        Jeżeli zostanie zwrócony inny status kod niż 200
        to stan pliku ustawiany jest na "NIE ODEBRANY".
        """        
        
        m_post.return_value= mock.Mock(status_code= 400, text= '')
        
        wysylka= self.setup_wysylka(bramka= 'T')
        wysylka.reference= self.M_REFERENCE
        wysylka.blobs= [self.M_BLOB_NAME]
    
        # Jeżeli sesja nie zakończyła się poprawnie

        wysylka.wysylka_finish()
                
        # Storage pliku zawiera numer referencyjny
        self.assertEqual('NIE ODEBRANY', self.jpk.stan, 'Niepoprawny status pliku')
        
        
    @mock.patch('requests.get')   
    def test_wysylka_status_p(self, m_get):
        """
        Jeżeli status odpowiedzi jest 200 i Code odpowiedzi jest równy 200 to 
        a) plik uznaje się za DOSTARCZONY
        b) pole upo zawiera UPO (podpisany elektronicznie dokument XML)
        """
                
        m_get.return_value= mock.Mock(status_code= 200, text= open(self.status_p_json, 'r').read())
        
        wysylka= self.setup_wysylka(bramka= 'P')
        wysylka.storage.reference= self.M_REFERENCE
        
        # Jeżeli sprawdzanie statusu zakończy się odpowiedzią 200  

        wysylka.wysylka_status()
        
        # Plik ma stan DOSTARCZONY
        self.assertEqual('DOSTARCZONY', self.jpk.stan, 'Niepoprawny status pliku')
        
        # Pole upo pliku zawiera UPO (z podpisem)
        self.assertXmlDocument(self.jpk.upo.encode('utf-8'))


    @mock.patch('requests.get')   
    def test_wysylka_status_t(self, m_get):
        """
        Jeżeli status odpowiedzi jest 200 i Code odpowiedzi jest równy 200 to 
        a) plik uznaje się za DOSTARCZONY
        b) pole upo zawiera UPO (podpisany elektronicznie dokument XML)
        W wersji testowej UPO nie jest podpisane.
        """
                
        m_get.return_value= mock.Mock(status_code= 200, text= open(self.status_t_json, 'r').read())
        
        wysylka= self.setup_wysylka(bramka= 'P')
        wysylka.storage.reference= self.M_REFERENCE
        
        # Jeżeli sprawdzanie statusu zakończy się odpowiedzią 200  

        wysylka.wysylka_status()
        
        # Storage pliku zawiera numer referencyjny
        self.assertEqual('DOSTARCZONY', self.jpk.stan, 'Niepoprawny status pliku')
        
        # Pole upo pliku zawiera UPO (z podpisem)
        self.assertXmlDocument(self.jpk.upo.encode('utf-8'))
        

    @mock.patch('requests.get')   
    def test_wysylka_status_200_1_300(self, m_get):
        """
        Jeżeli status odpowiedzi jest 200 i Code odpowiedzi jest 1* lub 30[^0]* to 
        sprawdzanie należy powtórzyć 
        a) status ustawiany jest na SPRAWDZANY
        """
                
        m_get.return_value= mock.Mock(status_code= 200, text= '''{
            "Code":303,
            "Description":"Dokument w trakcie weryfikacji podpisu, sprawdź wynik następnej weryfikacji dokumentu",
            "Details":"PROCESSING_FINISHED",
            "Timestamp":"2016-09-15T15:08:14.0000000+00:00",
            "Upo":""
        }''')
        
        wysylka= self.setup_wysylka(bramka= 'P')
        wysylka.storage.reference= self.M_REFERENCE
        
        # Jeżeli sprawdzanie statusu zakończy się odpowiedzią 200  

        wysylka.wysylka_status()
        
        # Storage pliku zawiera numer referencyjny
        self.assertEqual('SPRAWDZANY', self.jpk.stan, 'Niepoprawny status pliku')
        
        
    @mock.patch('requests.get')   
    def test_wysylka_status_200_400(self, m_get):
        """
        Jeżeli status odpowiedzi (CODE) jest 300, 4* to przesyłanie zakończyło się
        trwałym niepowodzeniem i dalsze próby sprawdzania statusu nie
        powinny być robione. 
        
        a) status ustawiany jest na NIE PRZYJĘTY
        """
                
        m_get.return_value= mock.Mock(status_code= 200, text= '''{
            "Code":412,
            "Description":"Dokument nieprawidłowo zaszyfrowany",
            "Details":"ERROR_DECOMPRESS",
            "Timestamp":"2016-09-22T09:27:38.0000000+00:00",
            "Upo":""
        }''')
        
        wysylka= self.setup_wysylka(bramka= 'P')
        wysylka.storage.reference= self.M_REFERENCE
        
        # Jeżeli sprawdzanie statusu zakończy się odpowiedzią 200  

        wysylka.wysylka_status()
        
        # Storage pliku zawiera numer referencyjny
        self.assertEqual('NIE PRZYJĘTY', self.jpk.stan, 'Niepoprawny status pliku')
                

    @mock.patch('requests.get')   
    def test_wysylka_status_blad_polaczenia(self, m_get):
        """
        Jeżeli w czasie sprawdzania statusu wystąpił błąd połączenia to 
        sprawdzanie należy powtórzyć 
        a) status ustawiany jest na SPRAWDZANY
        """
                
        m_get.side_effect= Exception('Błąd połączenia')
        
        wysylka= self.setup_wysylka(bramka= 'P')
        wysylka.storage.reference= self.M_REFERENCE
        
        # Jeżeli sprawdzanie statusu zakończy się odpowiedzią 200  

        wysylka.wysylka_status()
        
        # Storage pliku zawiera numer referencyjny
        self.assertEqual('SPRAWDZANY', self.jpk.stan, 'Niepoprawny status pliku')
        

    @mock.patch('requests.get')   
    def test_wysylka_status_400_500(self, m_get):
        """
        Jeżeli status odpowiedzi jest 4*, 5* to przesyłanie zakończyło się
        trwałym niepowodzeniem i dalsze próby sprawdzania statusu nie
        powinny być robione. 
        
        a) status ustawiany jest na NIE PRZYJĘTY
        """
                
        m_get.return_value= mock.Mock(status_code= 400, text= '''{
            "Message": "Żądanie jest nieprawidłowe",
            "RequestId": "172dc3cc-5b97-48de-91dd-6903587cba19"
        }''')
        
        wysylka= self.setup_wysylka(bramka= 'P')
        wysylka.storage.reference= self.M_REFERENCE
        
        # Jeżeli sprawdzanie statusu zakończy się odpowiedzią 200  

        wysylka.wysylka_status()
        
        # Storage pliku zawiera numer referencyjny
        self.assertEqual('NIE PRZYJĘTY', self.jpk.stan, 'Niepoprawny status pliku')

