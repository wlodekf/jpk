# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import locale, re, xlsxwriter
import lxml.etree as ET

from contextlib import closing
from io import StringIO, BytesIO

from app.models import Plik

from . import fa, fa3, kr, vat, vat2, vat4, wb, mag

def arkusz(jpk, dom, workbook, ctrl):
    """
    Utworzenie podanego (przez ctrl) arkusza XLS. 
    """
    
    _fa= {'3': fa3}.get(jpk.wariant, fa)
    if ctrl == 'faktura': _fa.faktura(jpk, workbook, dom)
    if ctrl == 'faktura_wiersz': _fa.faktura_wiersz(jpk, workbook, dom)    

    if ctrl == 'zois': kr.zois(jpk, workbook, dom)
    if ctrl == 'dziennik': kr.dziennik(jpk, workbook, dom) 
    if ctrl == 'konto_zapis': kr.konto_zapis(jpk, workbook, dom)
    
    # W 'vat' jest zawsze wersja bieżąca (domyślna) 
    # Pozostałe (stare) są w plikach vat z numerem wariantu (wersji)
    _vat= {'2': vat2, '3': vat2, '4': vat4}.get(jpk.wariant, vat)
    if ctrl == 'sprzedaz': _vat.sprzedaz(jpk, workbook, dom)
    if ctrl == 'zakup': _vat.zakup(jpk, workbook, dom)
    
    if ctrl == 'wyciag': wb.wyciag(jpk, workbook, dom)  
    
    if ctrl == 'PZ': mag.pz(jpk, workbook, dom)  
    if ctrl == 'WZ': mag.wz(jpk, workbook, dom)          
    if ctrl == 'RW': mag.rw(jpk, workbook, dom) 
    if ctrl == 'MM': mag.mm(jpk, workbook, dom)



def jpk_arkusz(jpk, ark):

    # Parsowanie w celu pobrania danych
    dom= ET.parse(StringIO(re.sub(' encoding="UTF-8"', '', jpk.xml)))
    # Utworzenie pliku XLS
    output= BytesIO()
    
    with closing(xlsxwriter.Workbook(output)) as workbook:
        # Dodanie arkusza
        arkusz(jpk, dom, workbook, ark)
    
    return output.getvalue()
    
        
def jpk_workbook(jpk):
    
    # Parsowanie w celu pobrania danych
    dom= ET.parse(StringIO(re.sub(' encoding="UTF-8"', '', jpk.xml)))
    # Utworzenie pliku XLS
    output= BytesIO() 
       
    with closing(xlsxwriter.Workbook(output)) as workbook:

        if jpk.kod == 'JPK_KR':
            arkusz(jpk, dom, workbook, 'zois')
            arkusz(jpk, dom, workbook, 'dziennik')   
            arkusz(jpk, dom, workbook, 'konto_zapis')   
            
        if jpk.kod == 'JPK_VAT':
            arkusz(jpk, dom, workbook, 'sprzedaz')
            arkusz(jpk, dom, workbook, 'zakup') 
    
        if jpk.kod == 'JPK_FA':
            arkusz(jpk, dom, workbook, 'faktura')
            arkusz(jpk, dom, workbook, 'faktura_wiersz')         
    
        if jpk.kod == 'JPK_WB':
            arkusz(jpk, dom, workbook, 'wyciag')
            """
            Z zapisywaniem wszystkich rachunków do jednego XLS są różne problemy
            1. Które pliki uwzględnić?
            2. Po regeneracji dowolnego pliku trzeba aktualizować xls we wszystkich plikach występujących w workbooku   

            for jpk_wb in Plik.objects.filter(kod='JPK_WB', dataod= jpk.dataod, datado= jpk.datado, utworzony__date= jpk.utworzony.date()).order_by('rachunek'):
                if jpk_wb.jest_utworzony():
                    dom= ET.parse(StringIO(re.sub(' encoding="UTF-8"', '', jpk_wb.xml))) 
                    arkusz(jpk_wb, dom, workbook, 'wyciag')
            """

        if jpk.kod == 'JPK_MAG':
            if jpk.pz_ctrl().wiersze>0: arkusz(jpk, dom, workbook, 'PZ')
            if jpk.wz_ctrl().wiersze>0: arkusz(jpk, dom, workbook, 'WZ') 
            if jpk.rw_ctrl().wiersze>0: arkusz(jpk, dom, workbook, 'RW')
            if jpk.mm_ctrl().wiersze>0: arkusz(jpk, dom, workbook, 'MM')         
                                            
    return output.getvalue()
