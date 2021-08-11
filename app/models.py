# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import decimal
from io import StringIO, BytesIO

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

from django.db.models import Q, Max
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.template.loader import render_to_string

from app import model_fields
import lxml.etree as ET
 
import datetime
import re
import json

from . import utils
from fk.models import Spo, SysPar

import logging
from app.templatetags.utils import kwota_pl
logger= logging.getLogger(__name__)

    
DEKLARACJA_VAT= [
    ('M', 'Miesięczna'),
    ('K', 'Kwartalna')
]


class Firma(models.Model):
    """
    Dane firmy.
    """
    
    oznaczenie= models.CharField(max_length= 10, unique= True)
    db_ostatnia= models.CharField(max_length= 20)
    db_rok= models.IntegerField()
    
    nip= models.CharField('NIP', max_length=10)
    nazwa= models.CharField('Nazwa', max_length= 100)
    adres= models.CharField('Adres', max_length= 50, null= True, blank= True)
    regon= models.CharField('Regon', max_length= 15, null= True, blank= True)
    krs= models.CharField('Nr KRS', max_length= 11, null= True, blank= True)
    wojewodztwo= models.CharField('Województwo', max_length= 20, null= True, blank= True)
    powiat= models.CharField('Powiat', max_length= 50, null= True, blank= True)
    gmina= models.CharField('Gmina', max_length= 50, null= True, blank= True)
    ulica= models.CharField('Ulica', max_length= 30, null= True, blank= True)
    nr_domu= models.CharField('Nr domu', max_length= 10, null= True, blank= True)
    nr_lokalu= models.CharField('Nr lokalu', max_length= 5, null= True, blank= True)
    miejscowosc= models.CharField('Miejscowość', max_length= 50, null= True, blank= True)
    kod_pocztowy= models.CharField('Kod pocztowy', max_length= 6, null= True, blank= True)
    poczta= models.CharField('Poczta', max_length= 50, null= True, blank= True)
    kod_urzedu= models.CharField('Kod US', max_length= 4, null= True, blank= True)
    email= models.CharField('Email', max_length= 50, null= True, blank= True)
    telefon= models.CharField('Telefon', max_length= 16, null= True, blank= True)
    ostatni_plik= models.ForeignKey('Plik', null= True, related_name= 'firma_ostatni', on_delete= models.SET_NULL)
    api_url= models.CharField('Api URL', max_length= 100, null= True, blank= True)
    api_auth= models.CharField('Klucz API', max_length= 100, null= True, blank= True)

    vat7= models.CharField('Deklaracja VAT', max_length= 1, choices= DEKLARACJA_VAT, null= True, blank= True)
        
    @staticmethod
    def firmy():
        return Firma.objects.all().order_by('oznaczenie')
    
    def par_firmy(self, pole):
        w= getattr(self, pole)
        if isinstance(w, str) and w:
            w=w.strip()
        return w
    
    def ustaw_ostatni_plik(self):
        plik_max_id= Plik.objects.filter(firma=self).aggregate(Max('id'))['id__max']
        self.ostatni_plik_id= plik_max_id if plik_max_id >0 else None
        self.save()
            
    
class Plik(models.Model):
    
    firma= models.ForeignKey(Firma, null= True, on_delete= models.CASCADE)
    kod= models.CharField('Kod pliku JPK', max_length=10)
    dataod= models.DateField('Data Od')
    datado= models.DateField('Data Do')
    rachunek= models.CharField(max_length= 30, null= True, blank= True)
    magazyn= models.CharField(max_length= 50, null= True, blank= True)
    czesc= models.CharField('Miesiąc części', max_length= 7, null=True, blank= True)
    utworzony= models.DateTimeField('Utworzony', default= datetime.datetime.now)
    utworzony_user= models.CharField(max_length= 10, null= True)   
    xml= model_fields.CompressedTextField('Zawartość pliku JPK', null= True)
    stan= models.CharField(max_length= 15, default= 'W KOLEJCE')
    odkad= models.DateTimeField('Odkad', default= datetime.datetime.now)
    task= models.CharField(max_length= 40, null= True)
    upo= model_fields.CompressedTextField('UPO', null= True)
    xls= model_fields.CompressedTextField('Plik kontrolny XLS', null= True)
    nazwa= models.CharField('Nazwa', max_length= 100, null= True, blank= True)
    cel_zlozenia= models.CharField(max_length= 1, default= "0")
    wariant= models.CharField(max_length=1, default= "1")
    wariant_dek= models.SmallIntegerField(default= 21)
    kod_systemowy= models.CharField(max_length= 20, null= True)
    wersja_schemy= models.CharField(max_length= 5, null= True)
    korekta= models.CharField(max_length= 1, null= True)
                
    class Meta:
        ordering= ['id']
        
    def to_json(self):
        """
        Konwersja nagłówka importu do postaci nadającej się do wyświetlenia
        na liście faktur (z grupowaniem pól).
        """
        return {
                'numer': self.id,
                'utworzony': self.utworzony.strftime('%Y-%m-%d %H:%M'),
                'kod': self.kod_systemowy[:7] if self.kod == 'JPK_VAT' and self.kod_systemowy else self.kod,
                'dataod': self.dataod.strftime('%Y-%m-%d'),
                'datado': self.datado.strftime('%Y-%m-%d'),
                'opis': self.opis(),
                'stan': self.stan,
                'czas': self.czas()[:7],
                'bledy': self.bledy_rodzaj()
        }

    def czas(self):
        if not self.jest_utworzony():
            return str(datetime.datetime.now() - self.odkad)
        else:
            return '00:00:00'
        
    def get_ctrl(self, tabela):
        return self.podsumowania.get(tabela= tabela.lower())

    def aktywa_ctrl(self):
        return self.podsumowania.get(tabela= 'aktywa')
    def pasywa_ctrl(self):
        return self.podsumowania.get(tabela= 'pasywa')
    def rzis_ctrl(self):
        return self.podsumowania.get(tabela= 'rzis')
    def kapital_ctrl(self):
        return self.podsumowania.get(tabela= 'kapital')
    def przeplywy_ctrl(self):
        return self.podsumowania.get(tabela= 'przeplywy')
    def podatek_ctrl(self):
        return self.podsumowania.get(tabela= 'podatek')
                
    def zois_ctrl(self):
        return self.podsumowania.get(tabela= 'zois')
    def dziennik_ctrl(self):
        return self.podsumowania.get(tabela= 'dziennik')        
    def konto_zapis_ctrl(self):
        return self.podsumowania.get(tabela= 'konto_zapis')
     
    def sprzedaz_ctrl(self):
        return self.podsumowania.get(tabela= 'sprzedaz')   
    def zakup_ctrl(self):
        return self.podsumowania.get(tabela= 'zakup')
    def deklaracja_ctrl(self):
        return self.podsumowania.get(tabela= 'deklaracja')
           
    def faktura_ctrl(self):
        return self.podsumowania.get(tabela= 'faktura')   
    def faktura_wiersz_ctrl(self):
        return self.podsumowania.get(tabela= 'faktura_wiersz')
      
    def salda_ctrl(self):
        return self.podsumowania.get(tabela= 'salda')        
    def wyciag_ctrl(self):
        return self.podsumowania.get(tabela= 'wyciag')
     
    def pz_ctrl(self):
        return self.podsumowania.get(tabela= 'pz') 
    def wz_ctrl(self):
        return self.podsumowania.get(tabela= 'wz') 
    def rw_ctrl(self):
        return self.podsumowania.get(tabela= 'rw') 
    def mm_ctrl(self):
        return self.podsumowania.get(tabela= 'mm') 
                                
    def od_msc(self):
        return self.dataod.strftime('%Y/%m')
    def do_msc(self):
        return self.datado.strftime('%Y/%m')
    def okres(self):
        pocz= self.od_msc()
        konc= self.do_msc()
        return pocz if pocz == konc else '{}/{}-{}'.format(pocz[:4], pocz[5:], konc[5:])

    def od_msc2(self):
        return self.dataod.strftime('%m')
    def od_rok(self):
        return self.dataod.strftime('%Y')
                
    def rok_01(self, dataod= None):
        """
        Pierwszy miesiąc roku, którego dotyczy plik.
        """
        if not dataod:
            dataod= self.dataod
                    
        return dataod.strftime('%Y/01')
    
    def set_stan(self, nowy_stan, save= False):
        if nowy_stan == 'PENDING': nowy_stan= 'W KOLEJCE'
        if nowy_stan == 'STARTED': nowy_stan= 'TWORZENIE'
        
        if nowy_stan != self.stan:
            self.odkad= datetime.datetime.now()
        self.stan= nowy_stan
        
        if save:
            self.save(update_fields=['stan', 'odkad'])

    def nazwa_pliku(self, sufiks= None):
        if SysPar._bra():
            nazwa= '{}-{}-{:02d}'.format(self.firma.oznaczenie, self.kod, self.dataod.month)
        else:
            nazwa= '{}-{:02d}'.format(self.kod, self.dataod.month)
        if sufiks:
            nazwa += '-'+sufiks.lower()
        return nazwa
    
    def rach(self):
        return self.rachunek[2:4]+' '+self.rachunek[4:8]+' ... '+self.rachunek[-4:]

    def par_firmy(self, pole= None):
        if not pole:
            return {k:v.strip() if isinstance(v,str) else v for k,v in self.firma.__dict__.items()}
            
        w= getattr(self.firma, pole)
        if isinstance(w, str) and w:
            w= w.strip()
        return w
    
    def _firma(self):
        return self.firma.oznaczenie
    
    def firma_(self):
        return self.firma.oznaczenie
    
    def db_name(self, year):
        prefiks= re.sub('\d\d$', '', self.par_firmy('db_ostatnia'))
        return '{}{:02d}'.format(prefiks, year%100) 

    def fkdbs(self, gdzie= None, dataod= None):
        """
        Ustalenie bazy danych dla danego pliku (w zależności od daty początkowej pliku).
        """
        if not dataod:
            dataod= self.dataod
             
        if dataod.year >= self.par_firmy('db_rok'):
            _fkdbs= self.par_firmy('db_ostatnia')
        else:
            _fkdbs= self.db_name(dataod.year) 
             
        self.fkdbs_msg(gdzie, _fkdbs)
        
        if not settings.DATABASES.get(_fkdbs):
            settings.DODAJ_BAZE(_fkdbs)
#             raise Exception('Niepoprawna baza danych {}'.format(_fkdbs))
        
        return _fkdbs 
    
    def fkdbs_1(self, gdzie= None, dataod= None):
        """
        Ustalenie bazy danych poprzedniego roku
        """
        if not dataod:
            dataod= self.dataod
                    
        if settings.DEVDBS.get(dataod.year) or settings.DATABASES.get(self.db_name(dataod.year)) or SysPar._bra():
            # Jeżeli jest bieżąca developerska lub produkcyjna to poprzednia
            dbs= self.db_name(dataod.year-1)
        else:
            # W przeciwnym razie cofamy się o dwa lata
            dbs= self.db_name(dataod.year-2)
                        
        if not settings.DATABASES.get(dbs):
            settings.DODAJ_BAZE(dbs)
                         
        self.fkdbs_msg(gdzie, dbs) 
        
        return dbs        
        
    def fkdbs_msg(self, gdzie, _fkdbs):
        if not hasattr(self, '_fkdbs_msg'):
            self._fkdbs_msg= []
            
        msg= gdzie+' '+_fkdbs
        
        if not msg in self._fkdbs_msg:
            self._fkdbs_msg.append(msg)
            logger.info(msg)
            
    def podmiot(self):
        return self.par_firmy()
            
    def init_slo(self, nr_slo):
        if not hasattr(self, '_spo') or not self._spo:
            self._spo= {}

        if not self._spo.get(nr_slo):        
            self._spo[nr_slo]= {spo[0].strip(): (spo[1].strip() if spo[1] else '') for spo in Spo.objects.using(self.fkdbs('Plik.init_slo '+nr_slo)).filter(nr_slo= nr_slo).values_list('spokod', 'pnazwa').order_by('spokod')}
    
    def slownik(self, nr_slo):
        self.init_slo(nr_slo)
        return self._spo[nr_slo]        
        
    def oczekiwanie(self):
        return self.stan in ('W KOLEJCE', 'TWORZENIE')      
    
    def mag(self):
        m= '{} {}'.format(self.magazyn[:3], self.magazyn[12:])
        return m[:15] if len(m)>15 else m  

    def mag3(self):
        return self.magazyn[:3]
    
    def opis(self):
        if self.nazwa: return self.nazwa
        
        if self.rachunek: opi= self.rach()
        elif self.magazyn: opi= self.mag()
        else: opi= {'JPK_KR': 'Księgi rachunkowe', 
                    'JPK_VAT': 'Rozliczenie VAT',
                    'JPK_FA': 'Faktury sprzedaży',
                    'JPK_SF': 'Sprawozdanie finansowe'
                    }.get(self.kod)
        
        if self.kod == 'JPK_SF':
            opi += ' {}'.format(self.datado.year)
            
        if self.kod == 'JPK_VAT' and self.wariant >= '4' and self.z_deklaracja():
            opi= 'Rozliczenie VAT z deklaracją'

        if (self.kod == 'JPK_VAT' and self.wariant == '3' and self.cel_zlozenia > '0') or \
           (self.kod == 'JPK_VAT' and self.wariant >= '4' and self.cel_zlozenia > '1') or \
            self.cel_zlozenia > '1':
            opi += ' - KOREKTA'
        return opi
                
    def jest_kontrolka(self):
        return self.storage_set.all().exists()

    def jest_wyslany(self):
        storage= self.storage_set.all()
        if not storage: return False
        storage= storage[0]
        return storage.init_time is not None
    
    def jest_utworzony(self):
        return not self.stan in ('W KOLEJCE', 'TWORZENIE', 'PROBLEMY')
        
    def jpk_sprawozdania(self):
        return self.kod == 'JPK_SF'

    def jpk_v7(self):
        return self.kod == 'JPK_VAT' and self.wariant >= '4'
        
    def status(self):
        return self.status
    
    def document_type(self):
        """
        Typ pliku do initupload.xml.
        Na razie ustawione na stałe, że VAT jest wysyłany cyklicznie a 
        pozostałe adhoc.
        """
        return 'JPK' if self.kod == 'JPK_VAT' else 'JPKAH'
    
    def blad(self, zrodlo, dokument, opis, level= 'error'):
        Blad.objects.create(jpk= self, zrodlo= zrodlo, dokument= dokument, blad= opis, level= level)
        
    def bledy(self):
        return self.blad_set.filter().exists()
    
    def bledy_warn(self):
        return self.blad_set.filter(level='warn').exists()
        
    def bledy_error(self):
        return self.blad_set.filter(level='error').exists()
    
    def bledy_rodzaj(self):
        if self.bledy_error(): return 'error'
        if self.bledy_warn(): return 'warn'
        return None
        
    def nietykalny(self):
        """
        Sprawdzenie czy plik jest nietykalny, tzn. nie może być usunięty, regenerowany
        czy w jakikolwiek sposób inaczej zmodyfikowany, bo został dostarczony do MF
        lub jest w trakcie przetwrzania.
        """
        if self.upo: return True
        if self.stan == 'SPRAWDZANY': return True

        storage= self.storage_set.all()
        if not storage: return False
        storage= storage[0]
        if not storage: return False
        
        status= storage.status()
        if not status: return False
        
        rc= status.json().get('Code') in (120, 301, 302, 303)
        return rc

    def sf_mozna_usunac(self):
        """
        Sprawdzenie czy plik sprawozdania można usunąć.
        Sprawozdanie można usunąć jeżeli nie jest ostatnim sprawozdaniem w
        danej firmie.
        """
        if not self.jpk_sprawozdania():
            return True

        # Plik jest sprawozdaniem

        # Można go usunąć jeżeli nie jest ostatniem sprawozdaniem
        # Przynajmniej jedno sprawozdanie musi zostać ponieważ firma
        # może mieć specjalne formuły wyznaczania obrotów
        return Plik.objects.filter(firma= self.firma, kod='JPK_SF').count() > 1

    def podpisany(self):
        return self.stan == 'PODPISANY'


    def ustal_cel_zlozenia(self):
        """
        Ustalenie czy plik jest "normalny" czy może jest korektą.
        Zakładamy, że jeżeli istnieje już dostarczony plik o takim samym kodzie
        i okresie to ten plik jest korektą.
        """
        max_cel= Plik.objects.filter(Q(dataod= self.dataod) | Q(datado= self.datado), 
                               firma= self.firma, 
                               kod= self.kod, 
                               stan= 'DOSTARCZONY').aggregate(Max('cel_zlozenia'))

        # W JPK_VAT wersji 4 1-złożenie, 2-korekta        
        if self.kod == 'JPK_VAT' and self.wariant >= '4':
            return '2' if (max_cel and max_cel['cel_zlozenia__max']) else '1'

        if max_cel and max_cel['cel_zlozenia__max']: 
            max_cel= max_cel['cel_zlozenia__max']
            return str(int(max_cel)+1)
        else:
            return '0' if self.kod == 'JPK_VAT' else '1'

        
    def sprawdz_podpis(self, xades_xml, storage):
        """
        Sprawdzenie czy wgrany podpisany plik kontrolny jest podpisem do ostatnio
        wygenerowanego pliku kontrolnego.
        """
        from io import StringIO
        
        root= ET.parse(StringIO(re.sub(' encoding="UTF-8"', '', xades_xml)))        
        expression= ET.XPath('/InitUpload/EncryptionKey')
        results= expression.evaluate(root)
        
        print(results)
        print(results[0].text)
                    
                        
    def get_storage(self):
        """
        Ustalenie storage danego pliku JPK.
        """
        storage= self.storage_set.all()
        return storage[0] if storage else None
    
            
    def get_status(self):
        """
        Przygotowanie/ustalenie informacji o aktualny statusie pliku do 
        prezentacji/wyświetlenia w rozwinięciu wiersza pliku.
        Prezentowany jest tylko ostatni status pliku.  
        """
        
        self.status= {} 
        
        # Ustalenie informacji o wysyłce
        storage= self.storage_set.all()
        
        # Jeżeli plik nie był wysyłany to informacja o utworzeniu lub błędach podczas tworzenia
        if not storage or self.stan in ('W KOLEJCE', 'TWORZENIE', 'PROBLEMY', 'GOTOWY', 'PODPISANY'):
            if self.xml:
                self.status['title']= 'Plik został utworzony'
                self.status['time']= self.utworzony
                self.status['user']= self.utworzony_user
            else:
                self.status['title']= 'Błąd podczas tworzenia pliku. Spróbuj ponownie.' if self.kod!='JPK_SF'else 'Tryb edycji/przygotowywania danych'
                self.status['time']= self.utworzony
                self.status['user']= self.utworzony_user
            return self.status
        
        # Ostatnia wysyłka
        storage= storage[0]
        
        # Tylko wygenerowano plik kontrolny
        if not storage.init_code:
            self.status['title']= 'Wygenerowano plik kontrolny/uwierzytelniający'
            self.status['time']= storage.sign_time
            self.status['user']= storage.sign_user
            return self.status
            
        # Błąd podczas initupload
        if storage.init_code != 200:
            self.status['title']= '{} - Błąd przy wysyłaniu pliku kontrolnego'.format(storage.init_code)
            txt= json.loads(storage.init_text)
            try:
                self.status['msg']= '{} - {}'.format(txt.get('Code'), txt.get('Message'))
            except:
                self.status['msg']= 'Błąd ustalania kodu/tekstu błędu'                
            self.status['time']= storage.init_time
            self.status['user']= storage.init_user
            return self.status
        
        # Błąd podczas wysyłki pliku jpk.XML
        if storage.put_code != 201:
            self.status['title']= '{} - Błąd przy wysyłaniu zaszyfrowanego pliku JPK'.format(storage.put_code)
            try:
                self.status['msg']= '{} - {}'.format(storage.put().get('Error').get('Code')[0].get('text'),
                                                 storage.put().get('Error').get('Message')[0].get('text'))
            except:
                self.status['msg']= 'Błąd ustalania kodu/tekstu błędu'
            self.status['time']= storage.put_time
            self.status['user']= storage.put_user
            return self.status
            
        # Błąd podczas kończenia sesji (mało prawdopodobny)
        if storage.finish_code != 200:
            errors= storage.finish().get('Errors','')
            if errors:
                errors= ', '.join(errors)
            self.status['title']= '{} - Błąd przy kończeniu sesji wysyłania pliku JPK'.format(storage.finish_code)
            try:
                self.status['msg']= '{} - {}. {}'.format(storage.finish_code,
                                                    storage.finish().get('Message'),
                                                    errors)
            except:
                self.status['msg']= 'Błąd ustalania kodu/tekstu błędu'                
            self.status['time']= storage.finish_time
            self.status['user']= storage.finish_user
            return self.status  
            
        # Sesja wysyłki zakończona pomyślnie
        
        # Sprawdzenie statusu (ostatniego)
        status= storage.status()
        
        # Błędy podczas przetwarzania
        if status.code != 200:
            errors= status.json().get('Errors','')
            if errors:
                errors= ', '.join(errors)
            self.status['title']= '{} - Błąd przy sprawdzaniu statusu wysyłania pliku JPK'.format(status.code)
            try:
                self.status['msg']= '{}. {}'.format(
                                                     status.json().get('Message'),
                                                     errors)
            except:
                self.status['msg']= 'Błąd ustalania kodu/tekstu błędu'                 
            self.status['time']= status.time
            self.status['user']= status.user
            return self.status  
        
        # Plik w trakcie przetwarzania
        if status.json().get('Code') in (120, 301, 302, 303):
            try:
                self.status['title']= '{} - Plik JPK został przesłany, trwa weryfikacja'.format(status.json().get('Code'))
                self.status['msg']= '{} - {}. {}'.format(status.json().get('Code'),
                                                     status.json().get('Description'),
                                                     status.json().get('Details',''))
            except:
                self.status['msg']= 'Błąd ustalania kodu/tekstu błędu'                 
            self.status['time']= status.time
            self.status['user']= status.user
            return self.status
                
        # Przetwarzanie zakończone błędem
        if status.json().get('Code') != 200:
            try:
                self.status['title']= '{} - Plik JPK nieprzyjęty z powodu błędów'.format(status.json().get('Code'))
                self.status['msg']= '{} - {}. {}'.format(status.json().get('Code'),
                                                     status.json().get('Description'),
                                                     status.json().get('Details',''))
            except:
                self.status['msg']= 'Błąd ustalania kodu/tekstu błędu'             
            self.status['time']= status.time
            self.status['user']= status.user
            return self.status
        
        # Plik dostarczony pomyślnie (musi być UPO)
        self.status['title']= 'Plik JPK został poprawnie dostarczony.'
        try:
            self.status['msg']= '{} - {}. <a href="{}" target="_blank">{}</a> (<a href="{}" target="_blank">wydruk</a>)'.format(
                                                 status.json().get('Code'),
                                                 status.json().get('Description'),
                                                 reverse('jpk-upo', args=[self.id]),
                                                 status.json().get('Details',''),
                                                 reverse('jpk-upo-wydruk', args=[self.id])
                                                 )
        except:
            self.status['msg']= 'Błąd ustalania kodu/tekstu błędu'                
        self.status['time']= status.time
        self.status['user']= status.user
        
        return self.status
    
    def deklaracja_xml(self):
        """
        Wygenerowanie XML deklaracji na podstawie pozycji deklaracji zapisanych w modelu Deklaracja.
        Wygenerowany XML wpisywany jest we właściwe miejsce głównego XML pliku JPK_VAT.
        """
        
        if not self.z_deklaracja(): 
            return

        # Wykonanie obliczeń
        Deklaracja.przygotowanie(self)

        deklaracja= Deklaracja.objects.filter(jpk= self).order_by('numer') 
        
        context= {'jpk': self, 'deklaracja': deklaracja}
        xml_wariant= 'deklaracja' + self.wariant

        dek_xml= render_to_string('app/xml/vat/{}.xml'.format(xml_wariant), context)
        
        """
        dom= ET.parse(StringIO(re.sub(' encoding="UTF-8"', '', self.xml)))
        prefix_map = {"pf": "http://crd.gov.pl/wzor/2020/03/06/9196/"}
        ps_el = dom.find(".//{http://crd.gov.pl/wzor/2020/03/06/9196/}PozycjeSzczegolowe", prefix_map)
        ps_xml = ET.XML(dek_xml)
        ps_el.getparent().replace(ps_el, ps_xml)
        self.xml= '<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(dom).decode()
        """

        self.xml= re.sub('<pf:PozycjeSzczegolowe>.*</pf:PozycjeSzczegolowe>', dek_xml, self.xml)

        # Jeżeli to jest tylko korekta deklaracji to usuwamy ewidencję
        # Oryginalnie ewidencja musi być wygenerowana bo na jej podstawie tworzona jest deklaracja        
        if self.kod_systemowy and self.kod_systemowy[:6] == 'JPK_V7' and self.cel_zlozenia == '2':
            if self.korekta == 'E':
                self.xml= re.sub('<pf:Deklaracja>.*</pf:Deklaracja>', '', self.xml, flags=re.S|re.DOTALL)                
            if self.korekta == 'D':
                self.xml= re.sub('<pf:Ewidencja>.*</pf:Ewidencja>', '', self.xml, flags=re.S|re.DOTALL)

        self.save()
        
        # Aktualizacja podsumowania deklaracji

        sprzedaz= self.sprzedaz_ctrl()
        zakup= self.zakup_ctrl()
        ctrl= self.deklaracja_ctrl()

        p_51= Deklaracja.ustal(self, 51)
        
        if p_51.kwota > 0:
            ctrl.suma1= p_51.kwota
        else:
            p_53= Deklaracja.ustal(self, 53)
            if p_53.kwota > 0:
                ctrl.suma1= p_53.kwota
        
        ctrl.wiersze= sprzedaz.wiersze + zakup.wiersze        
        ctrl.save()

    def z_deklaracja(self):
        # Dla JPK_V7K deklaracja tylko w ostatnim miesiacu kwartału
        if self.kod_systemowy.startswith('JPK_V7K') and not self.od_msc2() in (3, 6, 9, 12):
            return False
        # Tylko korekta ewidencji (bez deklaracji)
        if self.korekta == 'E':
            return False
        return True

    def z_ewidencja(self):
        # Tylko korekta deklaracji (bez ewidencji)
        if self.korekta == 'D':
            return False
        return True

    def v7_okres(self):
        if self.kod == 'JPK_VAT' and self.wariant >= '4' and self.kod_systemowy:
            return self.kod_systemowy[6:7]
        return ''

    def v7_kwartalny(self):
        return self.kod_systemowy and self.kod_systemowy[:7] == 'JPK_V7K'
    
    def v7_miesieczny(self):
        return not self.v7_kwartalny()
    
    def pf(self):
        return '9394' if self.v7_kwartalny() else '9393'



class Ctrl(models.Model):
    """
    Podsumowanie dla grupy elementów powtarzalnych (tabeli).
    """
    plik= models.ForeignKey('Plik', on_delete= models.CASCADE, related_name= 'podsumowania')
    tabela= models.CharField('Tabela', max_length= 20)
    wiersze= models.IntegerField('Wiersze', default= 0)
    suma1= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)
    suma2= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)
    xls= model_fields.CompressedTextField('Arkusz kontrolny XLS', null= True)
        
    class Meta:
        unique_together= ['plik', 'tabela']

    def save_xls(self, xls):
        self.xls= xls
        self.save()
        
        
    
class Wyciag(models.Model):
    
    nr_rachunku= models.CharField('Nr rachunku', max_length= 28)
    nr_wyciagu= models.IntegerField('Nr wyciagu')
    waluta= models.CharField('Waluta', max_length= 3)
    kod= models.CharField('Kod operacji', max_length= 4)
    
    data= models.DateField('Data operacji')
    kwota= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)
    opis= models.CharField('Opis operacji', max_length= 255)
    podmiot= models.CharField('Nazwa podmiotu', max_length= 255)
    
    saldo= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)

    def __str__(self):
        return '[nr_rachunku: {}, nr_wyciagu: {}, waluta: {}, kod: {}, data: {}, kwota: {}, opis: {}, podmiot: {}, saldo: {}'.format(
            self.nr_rachunku,
            self.nr_wyciagu,
            self.waluta,
            self.kod,
            self.data,
            self.kwota,
            self.opis,
            self.podmiot,
            self.saldo)
        
    @staticmethod
    def rachunek_pp(rachunek):
        return ' '.join(re.findall('.{4}', rachunek))
        
    @staticmethod
    def rachunki():
        rachunki= Wyciag.objects.values_list('nr_rachunku', flat=True).order_by('nr_rachunku').distinct()
        return [Wyciag.rachunek_pp(x) for x in rachunki]
    
    @staticmethod
    def testowe(*args, **kwargs):
        pola= {}
        pola.update(dict(zip(('nr_rachunku', 'nr_wyciagu', 'data', 'kwota', 'saldo', 'podmiot', 'opis'), args)))
        pola.update(kwargs)
        
        return Wyciag.objects.create(**pola)
    
    
    
class Storage(models.Model):
    """
    Przechowywanie informacji o procesie wysyłania pliku JPK.
    """
    jpk= models.ForeignKey('Plik', on_delete= models.CASCADE)
    
    sign_time= models.DateTimeField(default= datetime.datetime.now)
    sign_xml= model_fields.CompressedTextField('Plik do podpisania')
    sign_user= models.CharField(max_length= 10)
    
    aes_key= models.CharField(max_length= 44)
    enc_key= models.TextField()
    aes_iv= models.CharField(max_length= 24)
    jpk_aes= model_fields.CompressedTextField('Plik do wysłania')
    
    xml_name= models.CharField(max_length= 20)
    xml_len= models.IntegerField()
    xml_hash= models.CharField(max_length= 44)
    
    zip_name= models.CharField(max_length= 20)
    zip_len= models.IntegerField()
    zip_hash= models.CharField(max_length= 24)
    
    bramka= models.CharField(max_length= 1, default= 'P')
    
    xades_time= models.DateTimeField(null= True)
    xades_xml= model_fields.CompressedTextField('Plik podpisany', null= True)
    xades_user= models.CharField(max_length= 10, null= True)    
    
    init_time= models.DateTimeField(null= True)
    init_code= models.IntegerField(null= True)
    init_text= model_fields.CompressedTextField('Odpowiedź na InitUploadSigned', null= True)
    init_user= models.CharField(max_length= 10, null= True)   
        
    put_time= models.DateTimeField(null= True)
    put_code= models.IntegerField(null= True)
    put_text= model_fields.CompressedTextField('Odpowiedź na Upload', null= True)
    put_user= models.CharField(max_length= 10, null= True)   
        
    finish_time= models.DateTimeField(null= True)
    finish_code= models.IntegerField(null= True)
    finish_text= model_fields.CompressedTextField('Odpowiedź na FinishUpload', null= True)
    finish_user= models.CharField(max_length= 10, null= True)   
    
    reference= models.CharField(max_length= 32, null= True)

    class Meta:
        ordering= ['-id']
        
    
    def status(self):
        statusy= self.status_set.all()
        return statusy[0] if statusy else {}
    
    def init(self):
        return json.loads(self.init_text)
    
    def put(self):
        return utils.dictify(ET.fromstring(self.put_text.encode('utf-8'))) if self.put_text else {}
    
    def finish(self):
        return json.loads(self.finish_text)

    def check_upload_status(self):
        """
        Ustalenie czy powinno być wykonane następne sprawdzenie statusu.
        """
        
        # Jak wyłożył się wcześnij to nie ma co sprawdzać
        if self.init_code and self.init_code != 200: return False
        if self.put_code and self.put_code != 201: return False
        if self.finish_code and self.finish_code != 200: return False
        
        # Jak wysyłka OK to sprawdzamy status
        status= self.status()
        if not status:
            return True
        
        code= status.json().get('Code')
        if not code:
            return False
        
        rc= code in (100, 101, 102, 120, 301, 302, 303)
        return rc 
        
    def reset_upload(self, save= False):
        """
        Czyszczenie poprzednich danych o przesyłaniu
        Nie są potrzebne skoro robimy nowe przesłanie
        Może jednak te dane by się przydały?
        Można w tym miejscu (jeżeli było już wysyłanie), utworzyć nowy storage 
        """
        
        self.status_set.all().delete()
        
        self.init_code= None
        self.init_time= None
        self.init_text= None
        
        self.put_code= None
        self.put_time= None
        self.put_text= None
        
        self.finish_code= None
        self.finish_time= None
        self.finish_text= None        
        
        if save:
            self.save()
            
        if self.jpk.upo:
            self.jpk.upo= None
            self.jpk.save()
    
    def interfejs_produkcyjny(self):
        return self.bramka == 'P'
    
    def interfejs_testowy(self):
        return self.bramka == 'T'
    
        
    
class Status(models.Model):
    """
    Informacja o sprawdzeniu statusu.
    """
    storage= models.ForeignKey(Storage, on_delete= models.CASCADE)
    
    time= models.DateTimeField(default= datetime.datetime.now)
    code= models.IntegerField()
    text= model_fields.CompressedTextField('Odpowiedź na Status', null= True)
    user= models.CharField(max_length= 10)

    class Meta:
        ordering= ['-id']
           
    def json(self):
        return json.loads(self.text)
    
    def upo_xml(self):
        stat= json.loads(self.text)
        if not stat: return ''
        return stat['Upo']


    
class Blad(models.Model):
    jpk= models.ForeignKey('Plik', on_delete= models.CASCADE)

    zrodlo= models.CharField(max_length= 10)
    dokument= models.CharField(max_length= 20)
    blad= models.TextField()
    level= models.CharField(max_length= 10, default= 'error')

    class Meta:
        ordering= ['id']
        
    def klasa_css(self):
        return 'danger' if self.level == 'error' else '' 



class UserProfile(models.Model):
    """
    Dodatkowe dane użytkowników.
    """

    user= models.OneToOneField(User, related_name='profile')
    """Użytkownik, którego dane zawiera pozycja"""
    job_id= models.IntegerField(null= True)
    
    @staticmethod
    def nowy(user):
        profile= UserProfile(user= user)
        profile.save()     
        
    @staticmethod
    def get(request):   
        user= request.user    
        try:
            profil= user.profile
        except UserProfile.DoesNotExist:
            profil= UserProfile.nowy(user)
        return profil
        
        
# from users import email_new_user, email_group_changed
    
@receiver(models.signals.post_save, sender= User, dispatch_uid="post_save_user")    
def post_save_user(sender, instance, created, **kwargs):
    
    user= instance
    if created:
        profile= UserProfile.nowy(user)
    else:
        try:
            profile= user.profile
        except UserProfile.DoesNotExist:
            profile= UserProfile.nowy(user)



class Deklaracja(models.Model):
    """
    Pozycje deklaracji VAT-7.
    Informacja o wersji deklaracji zapisana jest w pliku jpk.
    """
    jpk= models.ForeignKey('Plik', on_delete= models.CASCADE)
    
    # C - podatek należny, D - podatek naliczony, E - zobowiązanie/zwrot, F - informacje dodatkowe
    grupa= models.CharField('Grupa', max_length= 1)
    # Lp pozycji lub pierwszej kwoty (jeżeli są dwie to mają lp, lp+1)
    numer= models.SmallIntegerField()
    # Nazwa/opis pozycji deklaracji
    nazwa= models.CharField('Nazwa', max_length= 255)
    # kk, k0, 0k, w, t
    rodzaj= models.CharField('Rodzaj', max_length= 1)
    # W przypadku gdy element nie jest postaci P_lp
    element= models.CharField('Element', max_length= 30, null= True, blank= True)
    
    # Podstawa lub podatek
    kwota= models.DecimalField('Kwota1', max_digits= 16, decimal_places= 2, default= 0.0)
    # Flaga/wybór
    wybor= models.BooleanField('Wybor', default= False)
    # Pole tekstowe
    tekst= model_fields.CompressedTextField('Opis zasad', null= True)

    def podstawa_nie_zero(self):
        """
        Sprawdzenie czy podstawa danego elementu jest niezerowa.
        """
        if self.rodzaj == '2':
            poprzednia= Deklaracja.objects.filter(jpk=self.jpk, numer= self.numer-1, rodzaj= '1')
            if not poprzednia:
                return False
            
            return poprzednia[0].kwota
        
        return False
        
    def p_element(self):
        return self.element or "P_{}".format(self.numer)

    @staticmethod
    def przygotowanie(jpk):
        """
        Przygotowanie deklaracji po utworzeniu pliku jpk.
        W tym momencie w deklaracji są tylko pozycje pochodzące z ewidencji.
        Trzeba je zaokrąglić do pełnych zł.
        I utworzyć podsumowania. 
        """

        # Utworzenie wszystkich brakujących pozycji deklaracji
        
        for poz in DeklaracjaPoz.objects.filter(wariant= jpk.wariant_dek):
            dek= Deklaracja.objects.filter(jpk=jpk, numer= poz.numer)
            if not dek:
                dek= DeklaracjaPoz.pozycja_deklaracji(jpk, poz.numer)
                dek.save()
        
        # Wyznaczenie podsumowania sekcji C i D
                 
        c_podstawa= decimal.Decimal(0.00)
        c_podatek= decimal.Decimal(0.00)

        d_podatek= decimal.Decimal(0.00)
        
        for dek in Deklaracja.objects.filter(jpk= jpk, rodzaj__in= ('1', '2'), grupa__in=('C', 'D')):
            
            if dek.numer in (37, 38, 48): # to są podsumowania
                continue
            
            poz= DeklaracjaPoz.objects.get(wariant= jpk.wariant_dek, numer= dek.numer)
            
            dek.kwota= utils.zlote(dek.kwota)

            if poz.grupa == 'C' and poz.rodzaj == '1' and poz.sumowanie:
                c_podstawa += dek.kwota if poz.sumowanie == '+' else -dek.kwota
            if poz.grupa == 'C' and poz.rodzaj == '2' and poz.sumowanie:
                c_podatek += dek.kwota if poz.sumowanie == '+' else -dek.kwota
            if poz.grupa == 'D' and poz.rodzaj == '2' and poz.sumowanie:
                d_podatek += dek.kwota if poz.sumowanie == '+' else -dek.kwota
                
            dek.save()
    
        # Zapisanie podsumowania sekcji C i D
        
        for dek in Deklaracja.objects.filter(jpk= jpk, numer__in=(37, 38, 48)):
            if dek.numer == 37:
                dek.kwota= c_podstawa
            if dek.numer == 38:
                dek.kwota= c_podatek
            if dek.numer == 48:
                dek.kwota= d_podatek
            dek.save() 

        Deklaracja.przelicz_deklaracje(jpk)


    @staticmethod
    def przelicz_deklaracje(jpk):
        
        # Obliczenie wysokości zobowiązania
        
        p38= Deklaracja.ustal(jpk, 38).kwota
        p48= Deklaracja.ustal(jpk, 48).kwota

        p49= Deklaracja.ustal(jpk, 49).kwota
        p50= Deklaracja.ustal(jpk, 50).kwota

        p52= Deklaracja.ustal(jpk, 52).kwota
        p54= Deklaracja.ustal(jpk, 54).kwota
        p60= Deklaracja.ustal(jpk, 60).kwota
                        
        if p38 > p48:
            p51= p38 - p48 - p49 -p50
        else:
            p51= 0
            
        if p48 > p38:
            p53= p48 - p38 + p52
        else:
            p53= 0 
        
        p62= p53 - p54 - p60
         
        Deklaracja.zapisz(jpk, 51, p51)
        Deklaracja.zapisz(jpk, 53, p53)
        Deklaracja.zapisz(jpk, 62, p62)
        
        
    @staticmethod
    def ustal(jpk, numer):
        """
        Wczytanie podanej pozycji deklaracji.
        Jeżeli pozycja nie istnieje to jest tworzona.
        """
        dek= Deklaracja.objects.filter(jpk=jpk, numer= numer)
        if not dek:
            dek= DeklaracjaPoz.pozycja_deklaracji(jpk, numer)
            dek.save()
        else:
            dek= dek[0]
            
        return dek

    @staticmethod
    def zapisz(jpk, numer, wartosc):
        """
        Zapisanie podanej kwoty w podanej pozycji deklaracji.
        """
        dek= Deklaracja.ustal(jpk, numer)

        if dek.rodzaj == 'W':
            dek.wybor= wartosc
        elif dek.rodzaj == 'T':
            dek.tekst= wartosc
        else:            
            dek.kwota= wartosc or 0
            
        dek.save()
        
        

class DeklaracjaPoz(models.Model):
    wariant= models.SmallIntegerField(default= 21)

    # C - podatek należny, D - podatek naliczony, E - zobowiązanie/zwrot, F - informacje dodatkowe
    grupa= models.CharField('Grupa', max_length= 1)
    # Lp pozycji lub pierwszej kwoty (jeżeli są dwie to mają lp, lp+1)
    numer= models.SmallIntegerField()
    # kk, k0, 0k, w, t
    rodzaj= models.CharField('Rodzaj', max_length= 1)
    # Nazwa/opis pozycji deklaracji
    nazwa= models.CharField('Nazwa', max_length= 255)
    # W przypadku gdy element nie jest postaci P_lp
    element= models.CharField('Element', max_length= 30, null= True, blank= True)
    # Sposób sumowania dla elementów grup C, D
    sumowanie= models.CharField('Sumowanie', max_length= 1, null= True, blank= True)

    strona= models.SmallIntegerField('Strona deklaracji', null= True, blank= True)

    x= models.SmallIntegerField(null= True)
    y= models.SmallIntegerField(null= True)
    
    typ= models.CharField('Typ', max_length= 1, default= 'D')

    @staticmethod
    def pozycja_deklaracji(jpk, numer):
        """
        Inicjalizacja opisu pozycji deklaracji odpowiedniego wariantu, 
        na podstawie numeru lp.
        """
        poz= DeklaracjaPoz.objects.get(wariant=jpk.wariant_dek, numer=numer)
        
        dek= Deklaracja(jpk= jpk, grupa= poz.grupa, numer= poz.numer, rodzaj= poz.rodzaj, nazwa= poz.nazwa, element= poz.element)
        dek.kwota= 0
        dek.wybor= False
        
        return dek
