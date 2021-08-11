# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
        
from celery import shared_task
from django.template.loader import render_to_string
from django.db import connection
    
from .models import Plik
from app.models import Deklaracja, DeklaracjaPoz

from .ctrl import vat, fa, kr,wb, mag, sf
from . import xls, wyslij, utils

import traceback

import logging
logger= logging.getLogger(__name__)

COUNTDOWN= 3

from collections import OrderedDict

CTRLS= {
        'JPK_VAT': {'sprzedaz': vat.sprzedaz,
                    'zakup': vat.zakup,
                    'deklaracja': vat.deklaracja},
        'JPK_FA':  {'faktura': fa.Faktura,
                    'faktura_wiersz': fa.Wiersz},
        'JPK_KR':  {'zois': kr.ZOiS, 
                    'dziennik': kr.Dziennik, 
                    'konto_zapis': kr.KontoZapis},
        'JPK_WB':  {'salda': wb.Salda, 
                    'wyciag': wb.WyciagWiersz},
        'JPK_MAG': {'pz': mag.PZ, 
                    'wz': mag.WZ, 
                    'rw': mag.RW, 
                    'mm': mag.MM},
        'JPK_SF':  OrderedDict([
                    ('wprowadz', sf.Wprowadzenie), 
                    ('rzis', sf.RZiS),
                    ('aktywa', sf.Aktywa),
                    ('pasywa', sf.Pasywa),
                    ('kapital', sf.Kapital),
                    ('przeplywy', sf.Przeplywy),
                    ('podatek', sf.PodatekCtrl),
                    ('dodatkowe', sf.Dodatkowe)])
    }


def jpk_task_thread(jpk):
    """
    Tworzenie pliku JPK w osobnym wątku
    """
    try:
        if jpk.kod == 'JPK_KR':
            KrTask(jpk.id).run()
        else:
            JpkTask(jpk.id).run()
    except:
        traceback.print_exc()
    finally:
        connection.close()
    

def run_task(jpk, config= {}):

    result= None
    
    if jpk.kod == 'JPK_KR':
        result= jpk_task_kr.apply_async((jpk.id,), countdown= COUNTDOWN)
    else:
        result= jpk_task.apply_async((jpk.id, config), countdown= COUNTDOWN)        
                                      
    return result
    
    
@shared_task
def jpk_task_kr(jpk_id):
    KrTask(jpk_id).run()


@shared_task
def jpk_task(jpk_id, config):
    JpkTask(jpk_id, config).run()    
    

@shared_task 
def wyslij_jpk_task(jpk, user):
    wyslij.WysylkaMF(jpk).wyslij(user)

    
def wyslij_jpk(jpk, user):
    wyslij_jpk_task.apply_async((jpk, user), countdown= 1)
    
            
class JpkTask(object):
    """
    Utworzenie pliku JPK.
    Najpierw tworzone są wszystkie Ctrl(podsumowania) dla pliku.
    Każdy Ctrl odpowiada za jedną z części pliku.
    """
    def __init__(self, jpk_id, config= {}):
        self.jpk_id= jpk_id
        self.config= config
        
        self.jpk= Plik.objects.get(id= self.jpk_id)
        self.podmiot= self.jpk.podmiot() 
        
        # W przypadku odświeżenia usunięcie starych podsumowań
        self.jpk.podsumowania.all().delete()
        
        # Ustawienie stanu na - tworzenie
        self.jpk.set_stan('TWORZENIE')
        self.jpk.save(update_fields=['stan', 'odkad'])
    
        self.init_ok= True
        
        self.ctrls= {}
        for kod, ctrl in CTRLS[self.jpk.kod].items():
            
            try:
                if self.jpk.kod == 'JPK_SF':
                    # Raporty kapitałów i przepływów są opcjonalne 
                    if kod == 'kapital' and not config['kapital']:
                        continue
                    if kod == 'przeplywy' and not config['przeplywy']:
                        continue
                    self.ctrls[kod]= ctrl(self.jpk, self.config)
                else:                
                    self.ctrls[kod]= ctrl(self.jpk)
            except:
                self.init_ok= False
                self.xml= None
                raise

    def run(self):
        context= {'jpk': self.jpk, 'podmiot': self.podmiot}
        context.update(self.ctrls)
         
        try:
            if self.init_ok:
                if self.jpk.kod == 'JPK_SF':
                    # Inicjalizacja/utworzenie wszystkich części (tabel pomocniczych) danego JPK
                    # Zaczynamy od 'wprowadzenia' bo tam jest tworzony nagłówek sprawozdania
                    for _, ctrl in self.ctrls.items():
                        ctrl.utworz()
                else:
                    xml_wariant= self.jpk.kod.lower() + (self.jpk.wariant if self.jpk.wariant != '1' else '')
                    # {'JPK_VAT2': '2', 'JPK_VAT3': '3'}.get(self.jpk.kod+self.jpk.wariant, '')

                    # Poniżej podczas generowania XML przetwarzane są pozycje 
                    # tworzące wszystkie części JPK (główny XML składa się z pod części
                    # odpowiadających Ctrl)
                    self.jpk.xml= render_to_string('app/xml/{}.xml'.format(xml_wariant), context)
                        
        except Exception as e:
            self.jpk.set_stan('PROBLEMY')            
            self.jpk.xml= None
            self.jpk.save(update_fields= ['stan', 'xml'])

            raise
        
        self.save()
        
        return self.jpk
        
    def sprawdzenia(self):
        pass
    
    def save(self):
        """
        Zakończenie tworzenia pliku JPK.
        Zapamiętywane są podsumowania poszczególnych części JPK.
        Generowane są arkusze kontrolne.
        """

        # Zapisanie kontrolek
                
        for ctrl in self.ctrls.values():
            ctrl.save_ctrl()
            
        self.jpk.set_stan('GOTOWY')
        self.jpk.save(update_fields= ['stan', 'odkad', 'xml'])
        
        # Ewentualna aktualizacja pliku XML aktualnym stanem deklaracji

        if self.jpk.kod == 'JPK_VAT' and self.jpk.wariant >= '4':
            self.jpk.deklaracja_xml()  
        
        # Wygenerowanie arkuszy kontrolnych
        
        if utils.par_firmy('save_jpk_xls') and not self.jpk.kod in ('JPK_WB', 'JPK_SF'):
            self.jpk.xls= xls.jpk_workbook(self.jpk)
            self.jpk.save(update_fields=['xls'])
                    
        if utils.par_firmy('save_ctrl_xls') and not self.jpk.kod in ('JPK_SF',):
            for kod, ctrl in self.ctrls.items():
                ctrl.ctrl.save_xls(xls.jpk_arkusz(self.jpk, kod))
        
        # Informacje o błędach
                    
        self.sprawdzenia()

    def wizualizacja_pdf(self, jpk):
        """
        Dodanie do podanego obrazu e-faktury "pieczątki" oznaczającej e-Fakturę.
        Stosowane dla faktur sprzedaży wybranych kontrahentów.
        """
        
        # Wczytanie szablonu deklaracji

        szablon= open('/home/wlodek/Downloads/vat-7-20.pdf', 'rb').read()
        szablon= PdfFileReader(BytesIO(szablon))

        nowy= PdfFileWriter()
        
        for i in range (0, szablon.getNumPages() ):
            page= szablon.getPage(i)
            tresc= self.strona_deklaracji_pdf(i, jpk)
            page.mergePage(tresc.getPage(0))
            nowy.addPage(page)
        
        # Zapisz nowy pdf do pliku
        
        output= BytesIO()
        nowy.write(output)
        out= open('/home/wlodek/Downloads/vat-7.pdf', 'wb')
        out.write(output.getvalue())
        out.close()
        
    def strona_deklaracji_pdf(self, strona, jpk):

        packet= BytesIO()
        can= canvas.Canvas(packet, pagesize= A4)
        can.setFont('Courier-Bold', 10)
        can.setFontSize(10)
        
        # Utworzenie nowego PDF

        if strona == 0: self.strona1_pdf(can, jpk)
#         if strona == 1: self.strona1_pdf(can, jpk)
#         if strona == 2: self.strona1_pdf(can, jpk)

        can.showPage()
        can.save()
        
        # move to the beginning of the StringIO buffer
        packet.seek(0)
        strona= PdfFileReader(packet)
        
        return strona
    
    def strona1_pdf(self, can, jpk):
        for numer in range(10, 33):
            dek= Deklaracja.ustal(jpk, numer)
            poz= DeklaracjaPoz.objects.get(wariant= jpk.wariant_dek, numer=numer)

            if poz.x and poz.y and dek.kwota:
                can.drawString(poz.x, poz.y, "{:-11,.0f}".format(dek.kwota).replace(',',' '))
        
        
        
class KrTask(JpkTask):
    def __init__(self, jpk_id):
        super(KrTask, self).__init__(jpk_id)
        
    def sprawdzenia(self):
        if self.ctrls['zois'].suma1 != self.ctrls['zois'].suma2: 
            self.jpk.blad('ZOiS', '', 'Niezgodność obrotów WN i MA w okresie')
        if self.ctrls['zois'].suma1 != self.ctrls['dziennik'].suma1:
            self.jpk.blad('ZOiS', '', 'Obroty w miesiącu niezgodne z sumą dziennika')
        if self.ctrls['dziennik'].suma1 != self.ctrls['konto_zapis'].suma1 or self.ctrls['dziennik'].suma1 != self.ctrls['konto_zapis'].suma2:
            self.jpk.blad('ZOiS', '', 'Suma dziennika niezgodna z KontoZapis')   
    