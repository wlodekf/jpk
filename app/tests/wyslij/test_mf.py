# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from django.test import mock

from app import mf
from .. import JpkTestCase


class MFTestCase(JpkTestCase):

    def setUp(self):
        self.m_reference= '9b3476ca01569d3c000000b0739ca385'
        self.m_blob_name= '046c4db1-64a9-4ba4-afda-85dcc07fe784'
        self.m_initupload= b'<xml>7</xml>'
        self.m_jpk_aes= b'0987654321'
        
        
    def setup_init_upload(self, m_post):
        m_post.return_value= mock.Mock(status_code= 200, text= '''{{
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
        }}'''.format(self.m_reference, self.m_blob_name)
        )
        
        
    @mock.patch('requests.post')
    def test_initupload(self, m_post):
        """
        1. Zapytanie (POST) pod poprawny adres (produkcyjny)
        2. Ustalenie reference i listy plików ze zwróconego JSON'a
        """

        self.setup_init_upload(m_post)
        
        bramka= mf.BramkaProdukcyjna()
        bramka.init_upload(self.m_initupload)
        
        
        # Sprawdzenie wszystkich argumentów wywołania
        m_post.assert_called_once_with('https://e-dokumenty.mf.gov.pl/api/Storage/InitUploadSigned', 
                                       data= self.m_initupload,
                                       headers= {'Content-Type': 'application/xml'}, 
                                       verify= False
                                    )
        
        # Sprawdzenie, że poprawnie został ustalony numer referencyjny i file_list
        self.assertEqual(self.m_reference, bramka.reference, 'Niepoprawny numer referencyjny')
        self.assertEqual(self.m_blob_name, bramka.file_list[0].get('BlobName'), 'Niepoprawna nazwa bloba')


    @mock.patch('requests.post')
    def test_initupload_nie_200_brak_reference(self, m_post):
        """
        Przy odpowiedzi 400 i 500 nie ma numeru referencyjnego ani listy plików.
        """

        m_post.return_value= mock.Mock(status_code= 400, text= '''{
                "Message": "Podpis negatywnie zweryfikowany",
                "Code": 120,
                "RequestId": "172dc3cc-5b97-48de-91dd-6903587cba19"
            }'''
        )
        
        
        bramka= mf.BramkaTestowa()
        bramka.init_upload(self.m_initupload)
        

        self.assertTrue(bramka.reference is None, 'Brak numeru referencyjnego')
        
        
    @mock.patch('requests.put')
    @mock.patch('requests.post')
    def test_upload(self, m_post, m_put):
        """
        1. Wykonywany jest PUT pod właściwy adres
        2. Numer referencyjny i list plików są przechowywane
        """
        
        # Przygotowanie
        self.setup_init_upload(m_post)
        m_put.return_value= mock.Mock(status_code= 201)        
        
        # Testowane czynności
        bramka= mf.BramkaTestowa()
        bramka.init_upload(self.m_initupload)
        bramka.upload(self.m_jpk_aes)
        
        # Sprawdzenie wszystkich argumentów wywołania InitUploadSigned
        m_post.assert_called_once_with('https://test-e-dokumenty.mf.gov.pl/api/Storage/InitUploadSigned', 
                                       data= self.m_initupload,
                                       headers= {'Content-Type': 'application/xml'}, 
                                       verify= False
                                    )
                
        # Sprawdzenie wszystkich argumentów wywołania PUT
        m_put.assert_called_once_with(
                    'https://taxdocumentstorage07tst.blob.core.windows.net/9b3476ca01569d3c000000b0739ca385/046c4db1-64a9-4ba4-afda-85dcc07fe784?sv=2015-07-08&sr=b&si=9b3476ca01569d3c000000b0739ca385&sig=vvjFBD1abUa%2B%2FIPHSgY03ty1v94suS0NbBPIu4HkQLE%3D', 
                    data= b'0987654321', 
                    headers= {'Content-MD5': '7hmBCcHZmhg02LtUWP5oCg==', 'x-ms-blob-type': 'BlockBlob'}, 
                    verify= False                 
                )
        
        # Sprawdzenie, że poprawnie został ustalony numer referencyjny i file_list
        self.assertEqual(self.m_reference, bramka.reference, 'Niepoprawny numer referencyjny')
        self.assertEqual([self.m_blob_name], bramka.blobs, 'Niepoprawna lista blobów') 
        
        
    @mock.patch('requests.post')
    def test_finish_upload(self, m_post):
        """
        1. Wykonywany jest POST pod właściwy adres
        2. Numer referencyjny i lista plików są przechowywane
        """
        
        # Testowane czynności
        bramka= mf.BramkaTestowa()
        
        # Poniższe wartości powinny pochodzić z initupload i upload
        bramka.reference= self.m_reference
        bramka.blobs= [self.m_blob_name]

        bramka.finish_upload()
        
        # Sprawdzenie wszystkich argumentów wywołania
        m_post.assert_called_once_with(
                          'https://test-e-dokumenty.mf.gov.pl/api/Storage/FinishUpload', 
                          data= json.dumps({"ReferenceNumber": "9b3476ca01569d3c000000b0739ca385", "AzureBlobNameList": ["046c4db1-64a9-4ba4-afda-85dcc07fe784"]}), 
                          headers= {'Content-Type': 'application/json'}, 
                          verify= False                                  
                )

        
    @mock.patch('requests.get')
    def test_status(self, m_get):
        """
        1. Wykonywany jest GET pod właściwy adres
        """
        
        # Testowane czynności
        bramka= mf.BramkaProdukcyjna()
        
        bramka.status(self.m_reference)
        
        # Sprawdzenie wszystkich argumentów wywołania
        m_get.assert_called_once_with(
                          'https://e-dokumenty.mf.gov.pl/api/Storage/Status/{}'.format(self.m_reference), 
                          verify= False                                  
                )
        
