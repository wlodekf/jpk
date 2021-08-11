# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.test import TestCase
from django.conf import settings

from app.models import Plik, Storage, Status
import datetime


class PlikTestCase(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        self.plik= Plik(kod= 'JPK_VAT', 
                        dataod= datetime.date(2015,7,1),
                        datado= datetime.date(2015,7,31))
        
    def test_fkdbs(self):
        self.assertEqual('fk15', self.plik.fkdbs('Baza odpowiadająca plikowi'))
        self.assertEqual('fk15', self.plik.fkdbs('Baza wskazanej daty', dataod= datetime.date(2015,4,1)))        
        self.assertEqual('fk14', self.plik.fkdbs('Baza wskazanej daty', dataod= datetime.date(2014,4,1)))
        with self.assertRaises(Exception):
            self.assertEqual('fk08', self.plik.fkdbs('Baza zbyt wczesna', dataod= datetime.date(2009,4,1)))                     
        self.assertEqual(settings.DEVDBS[list(settings.DEVDBS.keys())[0]], self.plik.fkdbs('Baza developerska', dataod= datetime.date(list(settings.DEVDBS.keys())[0],5,1)))
        
    def test_document_type(self):
        self.assertEqual('JPK', Plik(kod= 'JPK_VAT').document_type())
        self.assertEqual('JPKAH', Plik(kod= 'JPK_FA').document_type())
        self.assertEqual('JPKAH', Plik(kod= 'JPK_KR').document_type())
        self.assertEqual('JPKAH', Plik(kod= 'JPK_WB').document_type())
        self.assertEqual('JPKAH', Plik(kod= 'JPK_MAG').document_type())

    def test_nietykalny(self):
        self.assertTrue(Plik(upo= 'UPO').nietykalny())
        self.assertTrue(Plik(stan= 'SPRAWDZANY').nietykalny())
        self.assertTrue(Plik(stan= 'DOSTARCZONY', upo= 'UPO').nietykalny())                                                           
        
        self.assertFalse(Plik(stan= 'W KOLEJCE').nietykalny())   
        self.assertFalse(Plik(stan= 'TWORZENIE').nietykalny())
        self.assertFalse(Plik(stan= 'PROBLEMY').nietykalny())   
        self.assertFalse(Plik(stan= 'GOTOWY').nietykalny())
        self.assertFalse(Plik(stan= 'PODPISYWANY').nietykalny())
        self.assertFalse(Plik(stan= 'DOSTARCZONY').nietykalny())


class PlikStatusCase(TestCase):
    
    def setUp_plik(self, stan, xml= None):
                 
        # Pusty JPK_VAT za 2016/07
        self.jpk= Plik.objects.create(
                    kod= 'JPK_VAT', 
                    dataod= datetime.date(2016,7,1),
                    datado= datetime.date(2016,7,31),
                    utworzony_user= 'test',
                    stan= stan,
                    xml= xml,

                    # Fiksujemy id aby nazwa pliku była zawsze taka sama (JPK_VAT-100)
                    id= 100,
                    # Fiksujemy moment utworzenia bo jest w pliku XML                                    
                    utworzony= datetime.datetime(2016, 10, 5, 17, 24, 29),
                ) 
            
    def setUp_storage(self, **kwargs):
        pola= dict(
                sign_xml= b'', sign_user= 'test', aes_key= '', enc_key= '', aes_iv= '', 
                jpk_aes= b'', xml_name= '',
                xml_len= 0, xml_hash= '', zip_name= '', zip_len= 0, zip_hash= '',
                xades_time= datetime.datetime.now(),
                xades_xml= '<xml></xml>',
                xades_user= 'test', 
            )
        pola.update(kwargs)
        self.storage= Storage.objects.create(jpk= self.jpk, **pola)

    def setUp_status(self, **kwargs):
        pola= dict(
                user= 'user', 
                code= 200,
                text= ''
            )
        pola.update(kwargs)
        self.status= Status.objects.create(storage= self.storage, **pola)        
        
    def test_przygotowywany_z_xml(self):
                  
        self.setUp_plik('W KOLEJCE', '<xml/>')
        self.jpk.get_status()
        self.assertEqual('Plik został utworzony', self.jpk.status.get('title'))
        
        
    def test_przygotowywany_bez_xml(self):
                  
        self.setUp_plik('W KOLEJCE')
        self.jpk.get_status()
        self.assertEqual('Błąd podczas tworzenia pliku. Spróbuj ponownie.', self.jpk.status.get('title'))

    
    def test_initupload_ok(self):
                  
        self.setUp_plik('PODPISYWANY')
        self.setUp_storage()
        
        self.jpk.get_status()
        self.assertEqual('Wygenerowano plik kontrolny/uwierzytelniający', self.jpk.status.get('title'))
        
    def test_initupload_error(self):
                  
        init_code= 400
        self.setUp_plik('PODPISYWANY')
        self.setUp_storage(init_code= init_code, init_text= """
            {
            "Message": "Podpis negatywnie zweryfikowany",
            "Code": 120,
            "RequestId": "172dc3cc-5b97-48de-91dd-6903587cba19"
            }
        """)
        
        self.jpk.get_status()
        self.assertEqual('{} - Błąd przy wysyłaniu pliku kontrolnego'.format(init_code), self.jpk.status.get('title'))
        
                
    def test_put_error(self):
        put_code= 400
        self.setUp_plik('PODPISYWANY')
        self.setUp_storage(init_code= 200, put_code= put_code, put_text= """
            <Error>
                <Code>AuthenticationFailed</Code>
                <Message>Server failed to authenticate the request. Make sure the value of Authorization header is
                formed correctly including the signature.
                RequestId:a5124e1c-0001-0056-06b3-ddc62c000000 Time:2016-07-14T09:40:13.7833645Z</Message>
                <AuthenticationErrorDetail>SAS identifier cannot be found for specified signed identifier</AuthenticationErrorDetail>
            </Error>
        """)
        
        self.jpk.get_status()
        self.assertEqual('{} - Błąd przy wysyłaniu zaszyfrowanego pliku JPK'.format(put_code), self.jpk.status.get('title'))
        
    def test_finish_error(self):
        finish_code= 400
        self.setUp_plik('PODPISYWANY')
        self.setUp_storage(init_code= 200, put_code= 201, finish_code= finish_code, finish_text= """
            {
            "Message": "Żądanie jest nieprawidłowe",
            "Errors": "[‘Reference number jest wymagany’]",
            "RequestId": "172dc3cc-5b97-48de-91dd-6903587cba19"
            }
        """        
        ) 
        
        self.jpk.get_status()
        self.assertEqual('{} - Błąd przy kończeniu sesji wysyłania pliku JPK'.format(finish_code), self.jpk.status.get('title'))
       
    def test_status_error(self):
        status_code= 400
        self.setUp_plik('SPRAWDZANY')
        self.setUp_storage(init_code= 200, put_code= 201, finish_code= 200)
        self.setUp_status(code= status_code, text= """
            {
            "Message": "Żądanie jest nieprawidłowe",
            "RequestId": "172dc3cc-5b97-48de-91dd-6903587cba19"
            }        
        """)
        self.jpk.get_status()
        self.assertEqual('{} - Błąd przy sprawdzaniu statusu wysyłania pliku JPK'.format(status_code), self.jpk.status.get('title'))
        
    def test_status_processing(self):
        self.setUp_plik('SPRAWDZANY')
        self.setUp_storage(init_code= 200, put_code= 201, finish_code= 200)
        self.setUp_status(code= 200, text= """
            {
            "Message": "Żądanie jest nieprawidłowe",
            "Code": 120,
            "RequestId": "172dc3cc-5b97-48de-91dd-6903587cba19"
            }        
        """)
        self.jpk.get_status()
        self.assertEqual('120 - Plik JPK został przesłany, trwa weryfikacja', self.jpk.status.get('title'))
        
    def test_status_processing_error(self):
        self.setUp_plik('SPRAWDZANY')
        self.setUp_storage(init_code= 200, put_code= 201, finish_code= 200)
        self.setUp_status(code= 200, text= """
            {
            "Message": "Dokument z niepoprawnym podpisem.",
            "Code": "403",
            "RequestId": "172dc3cc-5b97-48de-91dd-6903587cba19"
            }        
        """)
        self.jpk.get_status()
        self.assertEqual('403 - Plik JPK nieprzyjęty z powodu błędów', self.jpk.status.get('title'))


    def test_status_dostarczony(self):
        self.setUp_plik('DOSTARCZONY')
        self.setUp_storage(init_code= 200, put_code= 201, finish_code= 200)
        self.setUp_status(code= 200, text= """
        {
            "Code": 200,
            "Description": "Przetwarzanie dokumentu zakończone poprawnie. Wygenerowano UPO",
            "Upo": "",
            "Details": "",
            "Timestamp": "2016-06-17T09:37:40.773976+00:00"
        }        
        """)
        self.jpk.get_status()
        self.assertEqual('Plik JPK został poprawnie dostarczony.', self.jpk.status.get('title'))
        