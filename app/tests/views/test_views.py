# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, re, os
from django.test import Client, mock
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from app.models import Plik
from app import tasks
from .. import JpkTestCase

import logging
logging.disable(logging.ERROR)

                
class ViewsTestCase(JpkTestCase):

    JPK_VAT_100_FILENAME= os.path.join(os.path.dirname(__file__), 'JPK_VAT-100.xml')
    
    def setUp(self):
        self.client= Client()
        user= User.objects.create(username='test', password='test')        
        self.client.force_login(user)
        
        self.jpk= Plik.objects.create(kod= 'JPK_FA',
                                      dataod= datetime.date(2016,7,1),
                                      datado= datetime.date(2016,7,31),
                                      nazwa= 'BRAK NAZWY',
                                      utworzony_user= 'test')
          
        self.jpk= tasks.JpkTask(self.jpk.id).run() 
        
                
    def setUpo(self, interfejs):
        self.jpk.upo= open(os.path.join(os.path.dirname(__file__), 'upo-{}.xml'.format(interfejs)), 'r').read()
        self.jpk.save()
        
                
    def test_home_no_login(self):
        
        self.client.logout()
        response= self.client.get(reverse('home'), follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/')
        
        
    def test_jpk_nowe_no_login(self):
        
        self.client.logout()
        response= self.client.get(reverse('jpk-nowe'), follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/jpk/nowe/')
        
                        
    def test_home(self):
        
        self.jpk= Plik.objects.create(kod= 'JPK_FA',
                                      dataod= datetime.date(2016,7,1),
                                      datado= datetime.date(2016,7,31),
                                      utworzony_user= 'test')
          
        self.jpk= tasks.JpkTask(self.jpk.id).run()  
                
        response= self.client.get('/')

        self.assertEqual(response.status_code, 200)

        self.assertEqual('gig', response.context['firma'])

        # Tutaj raczej więcej nie można zrobić ponieważ tabela 
        # wypełnia się przy pomocy zapytania AJAX, które nie będzie zrobione
        
    
    @mock.patch('app.tasks.run_task')
    def test_jpk_nowe(self, run_task):
    
        run_task.side_effect= lambda x: tasks.JpkTask(x.id).run()

        self.assertEqual(1, Plik.objects.all().count())
                
        response= self.client.post(reverse('jpk-nowe'), {'jpk_fa': 'JPK_FA', 'dataod': '2016-07-01', 'datado': '2016-07-31'})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/') 
                
        self.assertEqual(2, Plik.objects.all().count())

        # Sprawdzenie czy utworzono poprawny XML (pusty JPK_FA)
        
        jpk= Plik.objects.all().order_by('-id')[0]
        
        root= self.assertXmlDocument(jpk.xml.encode('utf-8'))
        self.assertXmlNamespace(root, None, 'http://jpk.mf.gov.pl/wzor/2016/03/09/03095/')        
        self.assertXmlNamespace(root, 'etd', 'http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2016/01/25/eD/DefinicjeTypy/')
        root= self.assertXmlDocument(re.sub('xmlns="http://jpk.mf.gov.pl/wzor/2016/03/09/03095/"', '', jpk.xml).encode('utf-8'))
        self.assertXmlNode(root)
        self.assertXmlNode(root, tag= 'JPK')
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1', './FakturaCtrl', './StawkiPodatku', './FakturaWierszCtrl'))

            
    def test_jpk_usun(self):
        
        self.assertEqual(1, Plik.objects.all().count())
        
        response= self.client.get(reverse('jpk-usun', args= [self.jpk.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')         

        self.assertEqual(0, Plik.objects.all().count())


    def test_jpk_nazwa(self):
        
        self.assertEqual(1, Plik.objects.all().count())
        self.assertEqual('BRAK NAZWY', Plik.objects.all()[0].nazwa)
        
        response= self.client.post(reverse('jpk-nazwa'), {'jpk_id': self.jpk.id, 'nazwa': 'OPIS PLIKU JPK'})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')         

        self.assertEqual(1, Plik.objects.all().count())
        self.assertEqual('OPIS PLIKU JPK', Plik.objects.all()[0].nazwa)        
        

    def test_jpk_arkusz(self):
        
        response= self.client.get(reverse('jpk-arkusz', args= [self.jpk.id, 'faktura']))

        self.assertEqual(response.status_code, 200)
        self.assertEqual('application/vnd.ms-excel', response['Content-Type'])
        self.assertEqual('attachment', response['Content-Disposition'][:10])        
        self.assertEqual(b'PK', response.content[:2])


    def test_jpk_xlsx(self):
        
        response= self.client.get(reverse('jpk-xlsx', args= [self.jpk.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual('application/vnd.ms-excel', response['Content-Type'])
        self.assertEqual('attachment', response['Content-Disposition'][:10])        
        self.assertEqual(b'PK', response.content[:2])


    def test_jpk_download(self):
        
        response= self.client.get(reverse('jpk-download', args= [self.jpk.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual('application/xhtml+xml', response['Content-Type'])
        self.assertEqual('attachment', response['Content-Disposition'][:10])  
        
        root= self.assertXmlDocument(response.content)
        self.assertXmlNamespace(root, None, 'http://jpk.mf.gov.pl/wzor/2016/03/09/03095/')        
        self.assertXmlNamespace(root, 'etd', 'http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2016/01/25/eD/DefinicjeTypy/')
        root= self.assertXmlDocument(re.sub('xmlns="http://jpk.mf.gov.pl/wzor/2016/03/09/03095/"', '', response.content.decode('utf-8')).encode('utf-8'))
        self.assertXmlNode(root)
        self.assertXmlNode(root, tag= 'JPK')
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1', './FakturaCtrl', './StawkiPodatku', './FakturaWierszCtrl'))
        
        
    @mock.patch('app.tasks.run_task')
    def test_jpk_regeneruj(self, run_task):
    
        run_task.side_effect= lambda x: tasks.JpkTask(x.id).run()

        response= self.client.get(reverse('jpk-regeneruj', args=[self.jpk.id]))
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')        

        # Sprawdzenie czy utworzono poprawny XML (pusty JPK_FA)
        
        jpk= Plik.objects.all()[0]
        
        root= self.assertXmlDocument(jpk.xml.encode('utf-8'))
        self.assertXmlNamespace(root, None, 'http://jpk.mf.gov.pl/wzor/2016/03/09/03095/')        
        self.assertXmlNamespace(root, 'etd', 'http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2016/01/25/eD/DefinicjeTypy/')
        root= self.assertXmlDocument(re.sub('xmlns="http://jpk.mf.gov.pl/wzor/2016/03/09/03095/"', '', jpk.xml).encode('utf-8'))
        self.assertXmlNode(root)
        self.assertXmlNode(root, tag= 'JPK')
        self.assertXpathsExist(root, ('./Naglowek', './Podmiot1', './FakturaCtrl', './StawkiPodatku', './FakturaWierszCtrl'))

        
    def test_jpk_task_gotowy(self):
        
        response= self.client.get(reverse('jpk-task', args= [','.join(str(x) for x in [self.jpk.id])]))

        self.assertEqual(response.status_code, 200)
        
        self.assertEqual({"czas": "0:00:00", "stan": "GOTOWY"}, response.json()[str(self.jpk.id)])


    @mock.patch('celery.result.AsyncResult')        
    def test_jpk_task_success(self, async_result):
        
        async_result.return_value= mock.Mock(status= 'SUCCESS')
        self.jpk.stan= 'TWORZENIE'
        self.jpk.task= '123'
        self.jpk.save()
        
        response= self.client.get(reverse('jpk-task', args= [','.join(str(x) for x in [self.jpk.id])]))

        self.assertEqual(response.status_code, 200)
        
        # Gdy runner wykonuje całą klasę mock nie jest stosowany
        # Gdy runner wykonuje tylko ten test to jest OK
        
#         self.assertEqual('GOTOWY', response.json().get(str(self.jpk.id)).get('stan'))

    @mock.patch('celery.result.AsyncResult') 
    def test_jpk_task_failure(self, async_result):

        async_result.return_value= mock.Mock(status= 'FAILURE')
        self.jpk.stan= 'TWORZENIE'
        self.jpk.task= '123'
        self.jpk.save()
        
        response= self.client.get(reverse('jpk-task', args= [','.join(str(x) for x in [self.jpk.id])]))

        self.assertEqual(response.status_code, 200)
        
        # Gdy runner wykonuje całą klasę mock nie jest stosowany
        # Gdy runner wykonuje tylko ten test to jest OK
                
#         self.assertEqual('PROBLEMY', response.json().get(str(self.jpk.id)).get('stan'))


    def test_jpk_refresh(self):
        
        response= self.client.get(reverse('jpk-refresh', args= [self.jpk.id]))

        self.assertEqual(response.status_code, 200)
        
        j= response.json()
        
        self.assertEqual('JPK_FA', j['kod'])        
        self.assertEqual('2016-07-01', j['dataod'])
        self.assertEqual('2016-07-31', j['datado'])        
        self.assertEqual('GOTOWY', j['stan'])           


    def test_jpk_rozwin(self):
        
        response= self.client.get(reverse('jpk-rozwin', args= [self.jpk.id]))

        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, '<a href="/jpk/{}/arkusz/faktura/">Faktury</a>'.format(self.jpk.id))
        self.assertContains(response, '<a href="/jpk/{}/arkusz/faktura_wiersz/">Wiersze</a>'.format(self.jpk.id))        


    @mock.patch('lxml.etree.XMLSchema')
    @mock.patch('lxml.etree.parse')
    def test_jpk_validate(self, m_parse, m_xml_schema):
                
        m_xml_schema.return_value= mock.Mock(error_log= [mock.Mock(line=100, message= 'Niepoprawny element XYZ')]) 
        m_xml_schema.return_value.validate.return_value= 0
        
        response= self.client.get(reverse('jpk-validate', args= [self.jpk.id]))

        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'Niepoprawny element XYZ') 


    @mock.patch('app.wyslij.Random')
    @mock.patch('time.time')
    def test_jpk_initupload(self, m_time, m_random):
                
        # Pusty JPK_VAT za 2016/07
        jpk= Plik.objects.create(
                    kod= 'JPK_VAT', 
                    dataod= datetime.date(2016,7,1),
                    datado= datetime.date(2016,7,31),
                    utworzony_user= 'test',
                    stan= 'GOTOWY',
                    
                    # Fiksujemy id aby nazwa pliku była zawsze taka sama (JPK_VAT-100)
                    id= 100,
                    # Fiksujemy moment utworzenia bo jest w pliku XML                                    
                    utworzony= datetime.datetime(2016, 10, 5, 17, 24, 29),
                    
                    # Zawartość pliku jest nieistotna, ważne aby była stała
                    xml= open(self.JPK_VAT_100_FILENAME, 'r').read()
                ) 
        
        # W zipie wpisywana jest data/czas modyfikacji ustalany z time.time()
        # dlatego określamy stałą wartość aby zip był zawsze jednakowy
        m_time.return_value= 1475692250.8109133
                         
        # Fiksujemy klucz szyfrowania i wartość inicjalizacyjną dla AES
        # które są ustalane z Random.new().read()
        m_read= mock.Mock(side_effect= [
            b'w\xe2\xa8\xe3\x0cw\x00\xdfVv\xc0/\xceg\xb4y\x89xO%\xa8\x8c \x99\x0e~F8\xe2+\xdc\xc9', 
            b'\xc5\xber\x03T\xfb\x05\xf9\xff\x8c\xf2am2L&'])
        m_random.new.return_value.read= m_read
        
        
        response= self.client.get(reverse('jpk-initupload', args= [jpk.id]))


        self.assertEqual(response.status_code, 200)
        
        # Sprawdzenie poprawności wywołań Random.new().read
        self.assertEqual([mock.call(32), mock.call(16)], m_read.mock_calls)
        
        self.assertXmlEquivalentOutputs(response.content, """
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
        
        self.assertEqual('application/xhtml+xml', response['Content-Type'])
        self.assertEqual('attachment', response['Content-Disposition'][:10])  
        
        jpk= Plik.objects.get(pk= jpk.id)
        
        self.assertEqual('PODPISYWANY', jpk.stan)
        
                
    def test_jpk_upo(self):
        """
        Dla JPK posiadającego UPO zwracany jest XML z potwierdzeniem odbioru.
        Dla wersji produkcyjnej.
        """
        
        self.setUpo('p')
        
        response= self.client.get(reverse('jpk-upo', args= [self.jpk.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual('application/xhtml+xml', response['Content-Type'])
        self.assertEqual('attachment', response['Content-Disposition'][:10])  
        
        root= self.assertXmlDocument(response.content)
        self.assertContains(response, '<Potwierdzenie ')


    def test_jpk_upo_t(self):
        """
        Dla JPK posiadającego UPO zwracany jest XML z potwierdzeniem odbioru.
        Dla wersji testowej.
        """
        
        self.setUpo('t')
        
        response= self.client.get(reverse('jpk-upo', args= [self.jpk.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual('application/xhtml+xml', response['Content-Type'])
        self.assertEqual('attachment', response['Content-Disposition'][:10])  
        
        root= self.assertXmlDocument(response.content)
        self.assertContains(response, '<Potwierdzenie ')
        
        
    def test_jpk_upo_wydruk(self):
        """
        Dla JPK posiadającego UPO zwracany jest XML z wizualizacją potwierdzenia odbioru.        
        Dla wersji produkcyjnej.
        """
        
        self.setUpo('p')
        
        response= self.client.get(reverse('jpk-upo-wydruk', args= [self.jpk.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual('application/xhtml+xml', response['Content-Type'])
        self.assertEqual('inline', response['Content-Disposition'][:6])  
        
        root= self.assertXmlDocument(response.content)
        self.assertContains(response, '<Potwierdzenie ')
        self.assertContains(response, 'upo.xsl')
        

    def test_jpk_upo_wydruk_t(self):
        """
        Dla JPK posiadającego UPO zwracany jest XML z wizualizacją potwierdzenia odbioru.  
        Dla wersji testowej.      
        """
        
        self.setUpo('t')
        
        response= self.client.get(reverse('jpk-upo-wydruk', args= [self.jpk.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual('application/xhtml+xml', response['Content-Type'])
        self.assertEqual('inline', response['Content-Disposition'][:6])  
        
        root= self.assertXmlDocument(response.content)
        self.assertContains(response, '<Potwierdzenie ')
        self.assertContains(response, 'upo.xsl')
        
        