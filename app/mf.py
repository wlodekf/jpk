# -*- coding: utf-8 -*- 

from __future__ import unicode_literals

import requests, json

import logging
logger= logging.getLogger(__name__)


class InterfejsMF(object):
    """
    Interfejs do wysyłania plików JPK do MF/US.
    """
    
    URL= 'e-dokumenty.mf.gov.pl/api/Storage'

    
    def init_upload(self, initupload_xml):
        """
        Wysłanie pliku kontrolnego initupload.xml podpisanego
        podpisem kwalifikowanym (inicjalizacja sesji klienta).

        Jeżeli odpowiedź jest poprawna to ustalany jest numer referencyjny
        oraz lista plików (blobów) do wysłania.
        
        S1. Numer referencyjny i lista plików są podawane tylko przy odpowiedzi 200.
        
        Przy odpowiedzi 400, 500 json ma inną zawartość.
        """
        
        url= self.url_interfejsu('/InitUploadSigned?enableValidateQualifiedSignature=false')
        
        logger.info('mf.init_upload(POST): {} {}'.format(url, len(initupload_xml)))
        resp= requests.post(url, 
                            data= initupload_xml, 
                            headers= {'Content-Type': 'application/xml'}, 
                            verify= False)
        
        resj= json.loads(resp.text)
        
        # Jeżeli odpowiedź != 200 to wartości będą puste
        self.reference= resj.get('ReferenceNumber')
        self.file_list= resj.get('RequestToUploadFileList')
            
        return resp
    
    
    def upload(self, jpk_aes):
        """
        Wysłaniepliku JPK.xml.
        Zakładamy, że wysyłany jest plik jednoczęściowy!
        """
        self.blobs= []
        for upload_req in self.file_list:
            headers= {header.get('Key'): header.get('Value') for header in upload_req.get('HeaderList')}
            self.blobs.append(upload_req.get('BlobName'))
            url= upload_req.get('Url') 
            
            logger.info('mf.upload(PUT): {} {}'.format(url, len(jpk_aes)))
            resp= requests.put(url, 
                               data= jpk_aes, 
                               headers= headers, 
                               verify= False)
            
        return resp
    
            
    def finish_upload(self):
        """
        Zakończenie (sesji) wysyłki pliku JPK do MF.
        """
        finish_data= {'ReferenceNumber': self.reference, 'AzureBlobNameList': self.blobs}
        url= self.url_interfejsu('/FinishUpload')
        data= json.dumps(finish_data)
        
        logger.info('mf.finish_upload(POST): {} {}'.format(url, len(data)))
        return requests.post(url,
                             data= data, 
                             headers= {'Content-Type': 'application/json'}, 
                             verify= False)
    
    
    def status(self, reference):
        """
        Sprawdzenie statusu.
        """
        url= self.url_interfejsu('/Status/'+reference)
        
        logger.info('mf.status(GET): {}'.format(url))
        return requests.get(url,
                            verify= False)

    
    def mf_api_url(self):
        return self.URL

    

class BramkaTestowa(InterfejsMF):

    PLIK_KLUCZA= 'klucz_mf.pem'
    
    def url_interfejsu(self, api):
        url= 'https://test-' + self.mf_api_url() + api
        logger.info(url)
        return url    



class BramkaProdukcyjna(InterfejsMF):

    PLIK_KLUCZA= 'klucz_mf_p.pem'
    
    def url_interfejsu(self, api):
        url= 'https://' + self.mf_api_url() + api
        logger.info(url)
        return url
     
 