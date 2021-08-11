# -*- coding: utf-8 -*- 

from __future__ import unicode_literals

import base64, zipfile, datetime, re
import io
import logging

from django.template import loader
from django.utils import six

from Crypto import Random
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.Hash import MD5
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

from . import models, mf
from app.utils import OperacjaNiedozwolona

logger= logging.getLogger(__name__)


class InituploadMF(object): 
    """
    Przygotowanie pliku kontrolego do inicjalizacji sesji wysyłki.
    """
    
    key_size= 32 # AES256
    BS= 16 # block size
    
    def __init__(self, jpk):
        self.jpk= jpk
     
       
    def plik_kontrolny(self, user, bramka):
        """
        Przygotowanie (utworzenie) pliku kontrolnego XML.
        
        Tworzony jest Storage z informacjami o wysyłce.
        
        Wydobycie klucza z certyfikatu    
        openssl x509 -inform pem -in cert_mf.pem -pubkey -noout > klucz_mf.pem
        """
        
        # Sprawdzenie czy initupload może być generowany dla danego pliku
        
        # Plik musi być utworzony
        if not self.jpk.jest_utworzony(): raise OperacjaNiedozwolona("Plik nie jest jeszcze utworzony")
        # Plik nie może być nietykalny
        if self.jpk.nietykalny(): raise OperacjaNiedozwolona('Plik nie może być modyfikowany')
        # Plik nie może mieć błędów
        if self.jpk.bledy_error(): raise OperacjaNiedozwolona('Plik został utworzony na podstawie danych zawierających błędy')
        
        
        # Ustalenie interfejsu MF (adres, klucz)
        self.mf_api= WysylkaMF.bramka_api_mf(bramka[0])

        # Inicjalizacja informacji o wysyłce
        storage= models.Storage(jpk= self.jpk, sign_time= datetime.datetime.now(), sign_user= user)
        
        # Losowy klucz szyfrowania 256 bitowy (32 bajty)
        aes_key= self.new_aes_key()
        
        # Zakodowanie klucza szyfrowania
        storage.aes_key= base64.b64encode(aes_key)

        # Zaszyfrowanie algorytmem RSA klucza szyfrowania AES pliku JPK        
        storage.enc_key= self.zaszyfruj_klucz_aes(aes_key)
        
        # Przygotowanie pliku JPK.xml
        jpk_xml= self.przygotuj_jpk_xml()
        
        # Zapisanie informacji o pliku JPK.xml
        storage.xml_name= self.jpk.nazwa_pliku() + '.xml'
        storage.xml_len= len(jpk_xml)
        
        # Policzenie skrótu SHA256 dla pliku
        storage.xml_hash= self.xml_hash(jpk_xml)
        
        # Utworzenie archiwum ZIP z plikiem JPK.xml
        jpk_zip= self.zip(jpk_xml, storage.xml_name)
        
        # Zaszyfrowanie algorytmem AES archiwum ZIP 
        storage.jpk_aes, storage.aes_iv= self.zaszyfruj_zip(jpk_zip, aes_key)

        # Policzenie skrótu MD5 zaszyfrowanego archiwum ZIP        
        storage.zip_hash= self.zip_hash(storage.jpk_aes)
        
        # Zapisanie informacji o archiwum zip
        storage.zip_name= self.jpk.nazwa_pliku() + '.zip'
        storage.zip_len= len(jpk_zip)
    
        # Utworzenie pliku kontrolnego initupload.xml
        storage.sign_xml= self.utworz_initupload_xml(storage)

        # Zapisanie informacji o stanie wysyłki
        storage.save()
        
        return storage

      
    def unpad(self, s):
        return s[:-ord(s[len(s)-1:])]

    def pad(self, s):
        """
        PKCS#7 padding opisany w https://tools.ietf.org/html/rfc5652#section-6.3
        """
        c= self.BS - len(s) % self.BS
        p= c * chr(c)
        return s + (bytes(p, encoding= 'iso-8859-1') if six.PY3 else p)
                
    def new_aes_key(self):
        """
        Nowy losowy klucz szyfrowania AES - 256 bitowy (32 bajty)
        """        
        return Random.new().read(self.key_size)
           
    def new_aes_iv(self):
        """
        Losowa wartość inicjalizacyjna dla algorytmu AES - 128 bitów (16 bajtów)
        """
        return Random.new().read(self.BS)               
                
    def rsa_public_key(self):
        """
        Zaimportowanie odpowiedniego do interfejsu klucza publicznego MF
        """
        return RSA.importKey(open(self.mf_api.PLIK_KLUCZA, 'r').read())
             
    def zaszyfruj_klucz_aes(self, aes_key):
        """
        Zaszyfrowanie algorytmem RSA klucza AES szyfrowania pliku JPK.
        Do szyfrowania wykorzystywany jest odpowiedni klucz publiczny MF
        (inny dla środowiska testowego i produkcyjnego).
        
        Szyfrowanie RSA z PKCS1 powoduje, że szyfrowanie tej samej wartości
        za każdym razem daje inny wynik (uwaga przy testowaniu)!
        """
        
        # Klucz publiczy MF do zaszyfrowania klucza AES algorytmem RSA
        klucz_rsa= self.rsa_public_key()
        
        # Padding PKCS1 dodaje losowe wartości do szyfrowania co powoduje
        # że każde szyfrowanie tej samej wartości daje inny wynik
        rsa_cipher= PKCS1_v1_5.new(klucz_rsa)
        
        # Klucz szyfrowania aes_key zaszyfrowany kluczem publicznym MF 
        # Aby odszyfrować trzeba mieć klucz prywatny MF
        enc_key= rsa_cipher.encrypt(aes_key) 
        
        # Zakodowanie base64, zaszyfrowanego klucza
        return base64.b64encode(enc_key)
                   
    def przygotuj_jpk_xml(self):
        """
        Przygotowanie pliku JPK.xml.
        Usunięcie komentarzy i zamiana na bajty.
        """
        
        # Usunięcie komentarzy (pól pomocniczych)
        jpk_xml= re.sub('<!--.*?-->', '', self.jpk.xml)
        
        # To musi być zrobione po powyższych podstawieniach
        # w przeciwnym razie jest EncodeDecodeError
        return jpk_xml.encode('utf-8')
        
    def xml_hash(self, jpk_xml):
        """
        Policzenie skrótu SHA256 dla pliku JPK.xml
        Skrót jest również kodowany Base64.
        """
        
        xml_hash= SHA256.new()
        xml_hash.update(jpk_xml)
        return base64.b64encode(xml_hash.digest())
        
    def zip(self, jpk_xml, nazwa_pliku):
        """
        Utworzenie archiwum ZIP zawierającego plik JPK.xml.
        ZIP tego samego pliku jest za każdym razem inny bo 
        zawiera informacje o dacie utworzenia!
        """
        zipio= io.BytesIO()
        with zipfile.ZipFile(zipio, mode='w', compression= zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(nazwa_pliku, jpk_xml)
        return zipio.getvalue()
        
    def zaszyfruj_zip(self, jpk_zip, aes_key):
        """
        Zaszyfrowanie algorytmem AES losowo wygenerowanym kluczem
        archiwum ZIP zawierającego plik JPK.xml.
        """
        
        # Losowa wartość inicjalizacyjna AES - 16 bajtów
        iv= self.new_aes_iv()
        
        # Zaszyfrowanie pliku ZIP algorytmem AES
        aes= AES.new(aes_key, AES.MODE_CBC, iv)
        jpk_aes= aes.encrypt(self.pad(jpk_zip))
        
        aes_iv= base64.b64encode(iv)
        
        return jpk_aes, aes_iv
        
    def zip_hash(self, jpk_aes):
        """
        Policzenie skrótu MD5 dla zaszyfrowanego archiwum ZIP.
        Skrót jest kodowany Base64. 
        """
        md5= MD5.new()
        md5.update(jpk_aes)
        return base64.b64encode(md5.digest())
        
    def utworz_initupload_xml(self, storage):
        """
        Wygenerowanie pliku kontrolnego do podpisu
        """
         
        template= loader.get_template('app/initupload.xml')    
        return template.render({'jpk': self.jpk, 'storage': storage})
        


class WysylkaMF(object): 
    """
    Przygotowanie, wysyłka, sprawdzanie statusu, pobranie UPO plików JPK do 
    interfejsu MF.
    """
      
    def __init__(self, jpk):
        self.jpk= jpk
        
        # Ustalenie informacji o przebiegu wysyłki
        if jpk:
            self.storage= jpk.get_storage()
        
        # Jeżeli znany jest storage to ustalenie mf_api (z informacjąo bramce)
        # Nieznany dla initupload ale tam nie jest potrzebny
        # Jest znany dla upload i status.
        if self.storage:
            self.mf_api= WysylkaMF.bramka_api_mf(self.storage.bramka)

    
    @staticmethod                  
    def bramka_api_mf(bramka):
        """
        Ustalenie interfejsu, na który będzie wysyłka.
        Interfejs określa adres URL API oraz klucz szyfrowania.
        """
        return {'P': mf.BramkaProdukcyjna(), 'T': mf.BramkaTestowa()}.get(bramka) 
    
                                                                                        
    def wyslij(self, user):
        """
        Wysłanie pliku JPK.
        Informacja o stanie wysyłki przekazywana jest w statusie pliku oraz w storage.
        """
        self.user= user
        
        self.wysylka_initupload()
        
        self.wysylka_zip()
        
        self.wysylka_finish()
        
        self.wysylka_status()

    
    def status(self, user):
        """
        Sprawdzenie statusu wysyłki JPK.
        """
        
        if not self.storage.reference:
            return
        
        self.user= user
    
        self.wysylka_status()
        

    def wysylka_initupload(self):
        """
        Wysłanie pliku kontrolnego initupload.xml
        
        Jeżeli wysyłka nie zakończy się statusem 200 to 
        a) stan pliku ustawiany jest na 'BŁĄD WYSYŁKI'
        b) reference nie jest znany
        c) dalsze przetwarzanie powinno być przerwane (wyjątek)
        """
        
        # Wysłanie podpisanego pliku kontrolnego do MF
        
        try:
            resp= self.mf_api.init_upload(self.storage.xades_xml.encode('utf-8'))
            _code, _text= resp.status_code, resp.text
        except Exception as exc:
            _code, _text= 401, '''{{
                "Message": "{}",
                "Code": 401
            }}'''.format(exc)
        
        # Zapisanie stanu wysyłki
        
        self.storage.init_time= datetime.datetime.now()
        self.storage.init_user= self.user
        self.storage.init_code= _code
        self.storage.init_text= _text
        
        logger.info('Initupload status: {} {!r}'.format(_code, _text))
        
        if _code != 200:
            # Jeżeli wysyłka pliku kontrolnego się nie powiodła to kończymy wysyłkę
            self.storage.save()
            self.jpk.set_stan('BŁĄD WYSYŁKI', save= True)
            
            raise Exception('Błąd podczas wysyłki pliku archiwum ZIP: {}/{}'.format(_code, _text))
        
        self.storage.reference= self.mf_api.reference  
        self.storage.save()
        
        
    def wysylka_zip(self):
        """
        Wysłanie zaszyfrowanego pliku JPK.xml.
        Wysyłka odbywa się do MS Azure, pod adres określony w odpowiedzi 
        na zapytanie InitUpload.
        
        Poprawne przesłanie pliku sygnalizowane jest status codem 201 (CREATED)
        a status pliku ustawiany jest na WYSYŁANY.
        Obiekt interfejsu zawiera listę przesłanych plików (potrzebne do 
        zakończenia sesji/FinishUpload).
        
        W przeciwnym razie status pliku ustawiany jest na NIE WYSŁANY 
        i wyrzucany wyjątek aby przerwać dalsze przetwarzanie (wysyłkę).
        """

        # Wysłanie zaszyfrowanego pliku JPK.xml
        try:        
            resp= self.mf_api.upload(self.storage.jpk_aes)
            _code, _text= resp.status_code, resp.text            
        except Exception as exc:
            _code, _text= 402, str(exc)
        
        # Zapisanie stanu wysyłki
        
        self.storage.put_time= datetime.datetime.now()
        self.storage.put_user= self.user
        
        self.storage.put_code= _code
        self.storage.put_text= _text 
        
        logger.info('Upload status: {} {!r}'.format(_code, _text))
            
        if _code != 201:
            self.storage.save()
            self.jpk.set_stan('NIE WYSŁANY', save= True)
            
            raise Exception('Błąd podczas wysyłki pliku XML: {}/{}'.format(_code, _text))
        
        self.jpk.set_stan('WYSYŁANY', save= True)
    
                   
    def wysylka_finish(self):
        """
        Zakończenie (sesji) wysyłki pliku JPK do MF.
        Jako dane do zakończenia sesji wysyłany jest numer referencyjny oraz lista blobów.
        
        Jeżeli zapytanie zwróci status kod 200 to sesja zakończyła się poprawnie.
        W takim przypadku stan pliku ustawiany jest na "SPRAWDZANY" (co powoduje 
        zablokowanie go do zmian).
        
        Jeżeli zostanie zwrócony inny status kod to stan pliku ustawiany jest na
        "NIE ODEBRANY".
        
        """
        
        try:
            resp= self.mf_api.finish_upload()
            _code, _text= resp.status_code, resp.text
        except Exception as exc:
            _code, _text= 403, '''{{
                "Message": "{}",
                "Code": 403
            }}'''.format(exc)            

        # Zapisanie stanu wysyłki
        
        self.storage.finish_time= datetime.datetime.now()
        self.storage.finish_user= self.user
        self.storage.finish_code= _code
        self.storage.finish_text= _text
        self.storage.save()
        
        logger.info('Finish status: {} {!r}'.format(_code, _text))
        
        self.jpk.set_stan('SPRAWDZANY' if _code == 200 else 'NIE ODEBRANY', save= True)
    
              
    def wysylka_status(self):
        """
        Sprawdzenie statusu wysyłki pliku JPK do MF.
        
        Jeżeli kod statusu odpowiedzi jest równy 200 to wysyłka zakończyła się pomyślnie
        a) status ustawiany jest na DOSTARCZONY, 
        b) a storage zawiera UPO
        
        Jeżeli status odpowiedzi (CODE) jest 1*, lub 31* lub w czasie sprawdzania
        wystąpił błąd połączenia to sprawdzanie należy powtórzyć 
        a) status ustawiany jest na SPRAWDZANY
        
        Jeżeli status odpowiedzi (CODE) jest 300, 4* to przesyłanie zakończyło się
        trwałym niepowodzeniem i dalsze próby sprawdzania statusu nie
        powinny być robione. 
        a) status ustawiany jest na NIE PRZYJĘTY
        """        
        try:
            resp= self.mf_api.status(self.storage.reference)
            _code, _text= resp.status_code, resp.text
        except Exception as exc:
            _code, _text= 404, '''{{
                "Message": "{}",
                "RequestId": "172dc3cc-5b97-48de-91dd-6903587cba19"
            }}'''.format(exc) 
            
                    
        # Zapisanie stanu wysyłki
        
        status= models.Status.objects.create(storage= self.storage, 
                                             time= datetime.datetime.now(),
                                             code= _code,
                                             text= _text,
                                             user= self.user)
        
        kod= status.json().get('Code')
        
        if _code == 200 and kod == 200:
            stan= 'DOSTARCZONY'
        elif _code == 200 and (kod < 200 or (kod > 300 and kod< 400)):
            stan= 'SPRAWDZANY'            
        elif _code == 404:
            stan= 'SPRAWDZANY'
        else:
            stan= 'NIE PRZYJĘTY'
            
        self.storage.jpk.set_stan(stan)
        if kod == 200:
            # Zapamiętanie UPO w Plik
            self.storage.jpk.upo= status.upo_xml()
        self.storage.jpk.save()
        
        logger.info('Status: {} {!r}'.format(_code, _text))
        
