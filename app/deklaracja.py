# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import os
import re

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import StringIO, BytesIO

import lxml.etree as ET
 
from django.conf import settings

from app.models import Deklaracja, DeklaracjaPoz

import logging
logger= logging.getLogger(__name__)

    
            
class DeklaracjaVAT(object):
    """
    Obsługa deklaracji VAT.
    """

    def __init__(self, jpk):
        self.jpk= jpk


    def wizualizacja_pdf(self):
        """
        Dodanie do podanego obrazu e-faktury "pieczątki" oznaczającej e-Fakturę.
        Stosowane dla faktur sprzedaży wybranych kontrahentów.
        """
        pdfmetrics.registerFont(TTFont('Arial', '/home/wlodek/projects/django/jpk/app/static/font/Arial.ttf'))
                
        # Wczytanie szablonu deklaracji

        szablon_path= os.path.normpath(os.path.join(settings.STATIC_ROOT, 'files/vat-7-{}.pdf'.format(self.jpk.wariant_dek)))
        szablon= open(szablon_path, 'rb').read()
        szablon= PdfFileReader(BytesIO(szablon))

        # Utworzenie nowego pliku pdf z połączenia szablonu (tło) i zawartości deklaracji

        nowy= PdfFileWriter()

        # Ustalenie wartości pozycji deklaracji z pliku XML
        # tak aby nie były czytane z bazy, 
        # bo to XML jest wysyłany więc on musi być wizualizowany
                 
        self.pozycje_z_xml()
        
        # Dodanie do każdej strony szablonu wizualizacji zawartości deklaracji

        for i in range (0, szablon.getNumPages() ):
            page= szablon.getPage(i)
            tresc= self.strona_deklaracji_pdf(i+1)
            page.mergePage(tresc.getPage(0))
            nowy.addPage(page)

                
        # Zapisanie nowego pdf do pliku (tymczasowe)
        
        output= BytesIO()
        nowy.write(output)
        return output.getvalue()

        
    def strona_deklaracji_pdf(self, strona):

        packet= BytesIO()
        can= canvas.Canvas(packet, pagesize= A4)
        can.setFontSize(10)
        
        # Utworzenie nowego PDF

        can.setFont('Arial', 10)
        self.set_char_spacing(can, 1)
        
        # Pozycje z deklaracji

        self.pozycje_ze_strony(strona, can)
                
        if strona == 1:
            self.naglowek_deklaracji(can)
        if strona == 3: 
            self.dane_kontaktowe(can)

        can.showPage()
        can.save()
        
        # move to the beginning of the StringIO buffer
        packet.seek(0)
        strona= PdfFileReader(packet)
        
        return strona

    
    def naglowek_deklaracji(self, can):

        # Nagłówek deklaracji

        self.set_char_spacing(can, 10)
        can.setFontSize(11)
 
        # NIP, miesiąc, rok

        # Te stałe stąd wywalić do bazy 

        can.drawString(93, 785, self.jpk.firma.nip)
        can.drawString(254, 691, self.jpk.od_msc2())
        can.drawString(330, 691, self.jpk.od_rok())
        
        # Cel złożenia

        if self.jpk.cel_zlozenia == '1':
            can.drawString(368, 598, 'x') # złożenie deklaracji
        else:
            can.drawString(479, 598, 'x') # korekta deklaracji

        # Rodzaj podmiotu
                        
        can.drawString(135, 552, 'x') # osoba niefizyczna

        self.set_char_spacing(can, 1)

        # Nazwa firmy
                
        can.setFont('Arial', 11)
        can.drawString(62, 510, self.jpk.firma.nazwa)


    def dane_kontaktowe(self, can):

        # Dane kontaktowe podatnika
                
        can.setFontSize(11)

        can.drawString(70, 596, self.jpk.firma.telefon)

        can.drawString(390, 610, self.jpk.firma.email)

        self.set_char_spacing(can, 10)
        can.drawString(255, 596, self.jpk.utworzony.strftime('%d%m%Y'))


    def pozycje_ze_strony(self, strona, can):
        """
        Wizualizacja wszystkich elementów z podanej strony.
        Uwzględniane są tylko te elementy, które występują w pliku XML
        i z niego powinny być pobrane a nie z bazy danych.
        """
        
        for poz in DeklaracjaPoz.objects.filter(wariant= self.jpk.wariant_dek, strona=strona):
#             dek= Deklaracja.ustal(self.jpk, poz.numer)

            wartosc= self.wartosci[poz.numer]
            
            # Kwota
            if poz.rodzaj in ('1', '2') and poz.x and poz.y and wartosc:
                can.drawRightString(poz.x, poz.y, "{:-11,.0f}".format(float(wartosc)).replace(',','.'))        

            # Wybór
            if poz.rodzaj == 'W' and poz.x and poz.y and wartosc:
                can.drawString(poz.x, poz.y, 'x')

            # Pole tekstowe (sztuk 2)
            if poz.rodzaj == 'T' and poz.x and poz.y and wartosc:
                can.drawString(poz.x, poz.y, wartosc)


    def pozycje_z_xml(self):
        """
        Ustalenie wartości pozycji deklaracji z pliku XML.
        """
        
        # Parsowanie w celu pobrania danych
        dom= ET.parse(StringIO(re.sub(' encoding="UTF-8"', '', self.jpk.xml)))

        self.wartosci= [None]*100

        deklaracja= None
        prefix_map = {"pf": "http://crd.gov.pl/wzor/2020/03/06/9196/"}
        for element in dom.iter(".//{http://crd.gov.pl/wzor/2020/03/06/9196/}PozycjeSzczegolowe"):
            deklaracja= element
            break
        
        for elem in deklaracja:
            tag= elem.tag
            if hasattr(tag, 'find'):
                i = tag.find('}')
                if i >= 0:
                    tag = tag[i+1:]
        
            print(tag, elem.text)
            
            if re.match(r'P_\d+', tag):
                numer= int(tag[2:])
            else:
                numer= 70
                
            self.wartosci[numer]= elem.text

        
    def set_char_spacing(self, can, spacing):
        textobject = can.beginText()
        textobject.setTextOrigin(0, 0)
        textobject.setCharSpace(spacing)
        textobject.textLine("")
        can.drawText(textobject)
