# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from xlsxwriter.utility import xl_rowcol_to_cell
from .utils import *
from fk.models import PROCEDURY, PROCEDURY_MAP

"""
Wariant 4 (2020-04) JPK_VAT obowiązujący od 2020.04.01. 
Dla plików JPK_VAT za okresy po 2020/04.
Korekty za poprzednie okresy w starym formacie.
"""


def ustal_gtu(element):
    """
    Ustalenie tabeli znaczników GTU występujących w podanym wierszu sprzedaży
    ['GTU_01', '', '', '', 'GTU_05', ...]
    """
    gtu= ['']*13
    for i in range(0, 13):
        val= t(element.find('{*}GTU_'+'{:02d}'.format(i+1)))
        if len(val) > 0:
            gtu[i]= 'GTU_{:02d}'.format(i+1)
    return gtu


def ustal_proc(element):
    """
    Ustalenie tabeli znaczników procedur występujących w podanym wierszu sprzedaży
    ['SW', '', '', 'TT_WNT', ...]
    """
    proc= ['']*14
    for i, p in enumerate(PROCEDURY):
        el= PROCEDURY_MAP.get(p, p)
        val= t(element.find('{*}'+el))
        if len(val) > 0:
            proc[i]= p
    return proc


def ustal_zak_proc(element):
    """
    Ustalenie tabeli znaczników procedur występujących w podanym wierszu zakupu
    ['MPP', '', '', 'IMP', ...]
    """
    proc= ['']*2
    for i, p in enumerate(['MPP', 'IMP']):
        val= t(element.find('{*}'+p))
        if len(val) > 0:
            proc[i]= p
    return proc


    
def sprzedaz(jpk, workbook, dom):
    """
    Utworzenie arkusza Excela z rozliczeniem podatku należnego (SprzedazWiersz).
    """
    
    worksheet= workbook.add_worksheet('Sprzedaz')
    
    # Header
    formath= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#E6E6FF'})
    formathr= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'align': 'right', 'bg_color': '#E6E6FF'})
    formatht= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#1C901C', 'font_color': '#FFFFFF'})
        
    headers= [
        ('Lp sprzedaży', formath),
        ('Kraj TIN', formath),
        ('Nr kontrahenta', formath),   
        ('Nazwa kontrahenta', formath),
        
        ('Dowód sprzedaży', formath),
        ('Data wystawienia', formath),
        ('Data sprzedaży', formath),
        ('Typ', formath),
    ]
    
    for k in range(10, 37):
        headers.append(('K_{}'.format(k), formathr))

    headers.extend([
        ('Marza', formathr),
        
        ('Podstawa', formatht),
        ('Podatek należny', formatht),
        ('Pod/rejestr', formatht),
    ])
    
    headers.append(('GTU', formath))
    for i in range(0, 13):
        headers.append(('GTU_{:02d}'.format(i+1), formath))
    
    headers.append(('Proc', formath))
    for p in PROCEDURY:
        headers.append((p, formath))
            
    worksheet.set_row(1, 30, formath)
    for i, h in enumerate(headers):
        worksheet.write(1, i, h[0], h[1])

    # Data columns format
    formatr= workbook.add_format({'align': 'center'})
    formatk= workbook.add_format({'num_format': '#,##0.00'})
    formats= workbook.add_format({'num_format': '#,##0.00',})    
    formato= workbook.add_format({'text_wrap': True})
    formatt= workbook.add_format({'bg_color': '#EAEAEA'}) 

    # Definicja szerokości i formatu kolumn

    kolumny= [
        (6, formatr),
        (3,),
        (12,),              
        (35, formato),
        (16,),
        (11,),
        (11,),
        (3,),
    ]
    
    for k in range(10, 37):
        kolumny.append((13, formatk))
        
    kolumny.extend([
        (13, formats),

        (13, formats),
        (13, formats),
        (5, formatt), 
    ])              
           
    kolumny.append((10, formato))
    for i in range(0, 13):
        kolumny.append((5, formats))
    
    kolumny.append((10, formato))
    for p in PROCEDURY:
        kolumny.append((5, formats))

    # Ustawienie szerokości i formatu kolumn
         
    for i, k in enumerate(kolumny):
        if len(k)>1:
            worksheet.set_column(i, i, k[0], k[1])
        else:
            worksheet.set_column(i, i, k[0])
                        
    # Writing data
    kolumny_zerowe= [True]*(38-10) # kolumny z kwotami nie mające wartości / do schowania 
    row= 1

    for element in dom.iter("{*}SprzedazWiersz"):
        row += 1
        
        worksheet.write_number(row, 0, int(element.find('{*}LpSprzedazy').text))
        worksheet.write_string(row, 1, t(element.find('{*}KodKrajuNadaniaTIN')))  
        worksheet.write_string(row, 2, t(element.find('{*}NrKontrahenta')))        
        worksheet.write_string(row, 3, t(element.find('{*}NazwaKontrahenta')))
        nr_dokumentu= element.find('{*}DowodSprzedazy')
        worksheet.write_string(row, 4, nr_dokumentu.text)
        worksheet.write(row, 5, element.find('{*}DataWystawienia').text)
        worksheet.write(row, 6, t(element.find('{*}DataSprzedazy')))
        worksheet.write(row, 7, t(element.find('{*}TypDokumentu')))
                 
        # Kolumny z deklaracji

        for k in range(10, 38):
            el= 'K_{}'.format(k) if k < 37 else 'SprzedazVAT_Marza' 
            wartosc= kwota(element.find('{*}'+el))
            worksheet.write_number(row, k-2, wartosc, formatk)
            if not wartosc == 0.0:
                kolumny_zerowe[k-10]= False

        # Podsumowanie            
        
        # Liczenie podstawy i vat w wierszu 
        
        worksheet.write_formula(row, 36, ('={}'+('+{}'*12)).format(*([xl_rowcol_to_cell(row, k-2) for k in (
                                            10, 11, 13, 15, 17, 19, 21, 22, 23, 25, 27, 29, 31)]))) 
        worksheet.write_formula(row, 37, ('={}'+('+{}'*11)).format(*([xl_rowcol_to_cell(row, k-2) for k in (
                                            16, 18, 20, 24, 26, 28, 30, 32, 33, 34, 35, 36)])))

        # Podrejestr w komentarzu do pola z dowodem sprzedaży

        for podrejestr in nr_dokumentu.itertext():
            pass
        worksheet.write(row, 38, podrejestr) # t(element.find('{*}T_podrejestr')))

        # Ustalenie GTU
        
        gtu= ustal_gtu(element)
        
        # Wszystkie GTU w jednej kolumnie
        
        worksheet.write_string(row, 39, ' '.join([g for g in gtu if g]).strip())  
        
        # Kolumny z poszczególnymi GTU
        
        for i in range(0, 13):
            worksheet.write_string(row, 40+i, gtu[i])  
    
        # Wszystkie procedury w jednej kolumnie
        
        proc= ustal_proc(element)
        
        worksheet.write_string(row, 53, ' '.join([p for p in proc if p]).strip())
        
        # Poszczególne procedury
        
        for i, p in enumerate(PROCEDURY):
            worksheet.write_string(row, 54+i, proc[i])
        
        
    # Podsumowanie kolumn kwotowych  
          
    for i in range(8, 38):
        worksheet.write_formula(0, i, '=SUBTOTAL(9,{}:{})'.format(xl_rowcol_to_cell(2, i), xl_rowcol_to_cell(row, i)))
    
    worksheet.autofilter('B2:BP{}'.format(row))   
    
    worksheet.freeze_panes(2, 6) 
    worksheet.set_selection(2, 6, 2, 6)
    if ZOOM:       
        worksheet.set_zoom(75)

    worksheet.set_margins(left=0.5, right=0.3, top=0.6, bottom=0.45)    
    worksheet_header(worksheet, jpk, 'Sprzedaż')
    worksheet.repeat_rows(1)
    
    format0= workbook.add_format({'color': '#FFFFFF'})            
    worksheet.conditional_format('H3:AL{}'.format(row+1), {'type':     'cell',
                                        'criteria': '=',
                                        'value':    0,
                                        'format':   format0})
       
    niezerowe= 0
    for i, zero in enumerate(kolumny_zerowe):
        if zero:
            worksheet.set_column(8+i, 8+i, None, None, {'hidden': True})
        else:
            niezerowe += 1
            
    if niezerowe>6:
        worksheet.set_column(6, 6, kolumny[6][0], None, {'hidden': True}) # data sprzedaży

    # Schowanie pojedynczych kolumn GTU

    worksheet.set_column(40, 52, None, None, {'hidden': True}) # pojedyncze GTU
    worksheet.set_column(54, 67, None, None, {'hidden': True}) # pojedyncze procedury
                                     
    if niezerowe > 2:
        worksheet.set_landscape()
    else:
        worksheet.set_portrait()   
        
    worksheet.print_area(0,0,row,37 if niezerowe < 7 else 34)
                     
             
    

def zakup(jpk, workbook, dom):
    """
    Utworzenie arkusza Excela z rozliczeniem podatku naliczonego (ZakupWiersz).
    """
    
    worksheet= workbook.add_worksheet('Zakup')
    
    # Header
    formath= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#E6E6FF'})
    formathr= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'align': 'right', 'bg_color': '#E6E6FF'})
    formatht= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#1C901C', 'font_color': '#FFFFFF'})
    
    headers= [
        ('Lp zakupu', formath),
        ('Kraj TIN', formath),
        ('Nr dostawcy', formath),        
        ('Nazwa dostawcy', formath),
        ('Nr faktury', formath),
        ('Data zakupu', formath),
        ('Data wpływu', formath),
    ]
    for k in range(40, 48):
        headers.append(('K_{}'.format(k), formathr))
        
    headers.extend([
        ('Podstawa', formatht),
        ('Podatek naliczony', formatht),
        ('Rejestr', formatht),

        ('Dokument zakupu', formath),
        ('MPP', formath),
        ('IMP', formath),
    ])
    
    worksheet.set_row(1, 30, formath)
    for i, h in enumerate(headers):
        worksheet.write(1, i, h[0], h[1])

    # Data columns format
    formatr= workbook.add_format({'align': 'center'})
    formatk= workbook.add_format({'num_format': '#,##0.00', 'font_size': 13})
    formats= workbook.add_format({'num_format': '#,##0.00', 'bg_color': '#E6E6E6'})    
    formato= workbook.add_format({'text_wrap': True})
        
    kolumny= [(6, formatr),
              (3,),
              (12,),
              (35, formato),
              (20,),
              (11,),              
              (11,),
              ]
    
    for k in range(40, 48):
        kolumny.append((13, formatk))
        
    kolumny.append((13, formats))
    kolumny.append((13, formats)) 
    kolumny.append((5,)) 
      
    kolumny.append((10, formato))
    kolumny.append((5, formato)) 
    kolumny.append((5, formato)) 


    for i, k in enumerate(kolumny):
        if len(k)>1:
            worksheet.set_column(i, i, k[0], k[1])
        else:
            worksheet.set_column(i, i, k[0])
                        
    # Writing data
    row= 1

    for element in dom.iter("{*}ZakupWiersz"):
        row += 1
        
        worksheet.write_number(row, 0, int(element.find('{*}LpZakupu').text))
        worksheet.write_string(row, 1, t(element.find('{*}KodKrajuNadaniaTIN')))  
        worksheet.write(row, 2, element.find('{*}NrDostawcy').text)
        worksheet.write_string(row, 3, element.find('{*}NazwaDostawcy').text)
        nr_faktury= element.find('{*}DowodZakupu')
        worksheet.write_string(row, 4, nr_faktury.text)
        worksheet.write(row, 5, element.find('{*}DataZakupu').text)
        worksheet.write(row, 6, element.find('{*}DataWplywu').text)        
        
        # Kolumny z deklaracji
        for k in range(40, 48):        
            worksheet.write_number(row, k-33, kwota(element.find('{{*}}K_{}'.format(k))), formatk)
            
        # Liczenie podstawy i vat w wierszu 
        worksheet.write_formula(row, 15, ('={}'+('+{}'*1)).format(*([xl_rowcol_to_cell(row, k) for k in (7, 9)]))) 
        worksheet.write_formula(row, 16, ('={}'+('+{}'*4)).format(*([xl_rowcol_to_cell(row, k) for k in (8, 10, 11, 12, 13)])))
        
        # Podrejestr z komentarza w numerze faktury
        for podrejestr in nr_faktury.itertext():
            pass
        worksheet.write(row, 17, podrejestr) # t(element.find('{*}T_podrejestr')))         
            
        worksheet.write_string(row, 18, t(element.find('{*}DokumentZakupu')))
  
        # Ustalenie znaczników

        proc= ustal_zak_proc(element)
        
        # Kolumny z poszczególnymi GTU

        for i in range(0, 2):
            worksheet.write_string(row, 19+i, proc[i])  
            
            
                
    # Podsumowanie kolumn kwotowych        
    for i in range(7, 17): 
        worksheet.write_formula(0, i, '=SUBTOTAL(9,{}:{})'.format(xl_rowcol_to_cell(2, i), xl_rowcol_to_cell(row, i)))
    
    worksheet.autofilter('B2:U{}'.format(row))   
            
    worksheet.freeze_panes(2, 5) 
    worksheet.set_selection(2, 7, 2, 7)
    if ZOOM:        
        worksheet.set_zoom(75)

    worksheet.set_landscape()
    worksheet.set_margins(left=0.5, right=0.3, top=0.6, bottom=0.45) 
    worksheet_header(worksheet, jpk, 'Zakup')       
    worksheet.repeat_rows(1)
    worksheet.print_area(0,0,row,14)
    
    format0= workbook.add_format({'color': '#FFFFFF'})            
    worksheet.conditional_format('H3:O{}'.format(row+1), {'type':     'cell',
                                        'criteria': '=',
                                        'value':    0,
                                        'format':   format0})
    
        
    