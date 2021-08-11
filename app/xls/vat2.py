# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from xlsxwriter.utility import xl_rowcol_to_cell
from .utils import *

"""
Wariant 2 (2017-01) JPK_VAT obowiązujący od 2017.02.01. 
Dla wszystkich plików JPK_VAT również zawierających korekty z 2016.
"""

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

        ('Nr kontrahenta', formath),        
        ('Nazwa kontrahenta', formath),
        ('Adres kontrahenta', formath),
        ('Dowód sprzedaży', formath),
        ('Data wystawienia', formath),
        ('Data sprzedaży', formath),
    ]
    
    for k in range(10, 39):
        headers.append(('K_{}'.format(k), formathr))
    headers.extend([
        ('Podstawa', formatht),
        ('Podatek należny', formatht),
        ('Pod/rejestr', formatht),
    ])
    
    worksheet.set_row(1, 30, formath)
    for i, h in enumerate(headers):
        worksheet.write(1, i, h[0], h[1])

    # Data columns format
    formatr= workbook.add_format({'align': 'center'})
    formatk= workbook.add_format({'num_format': '#,##0.00'})
    formats= workbook.add_format({'num_format': '#,##0.00',})    
    formato= workbook.add_format({'text_wrap': True})
    formatt= workbook.add_format({'bg_color': '#EAEAEA'}) 
            
    kolumny= [(6, formatr),
              (12,),              
              (35, formato),
              (35, formato),
              (16,),
              (11,),
              (11,),
              ]
    for k in range(10, 39):
        kolumny.append((13, formatk))
    kolumny.extend([
              (13, formats),
              (13, formats),
              (5, formatt), 
              ])              
            
    for i, k in enumerate(kolumny):
        if len(k)>1:
            worksheet.set_column(i, i, k[0], k[1])
        else:
            worksheet.set_column(i, i, k[0])
                        
    # Writing data
    kolumny_zerowe= [True]*(39-10) # kolumny z kwotami nie mające wartości / do schowania 
    row= 1
    for element in dom.iter("{*}SprzedazWiersz"):
        row += 1
        
        worksheet.write_number(row, 0, int(element.find('{*}LpSprzedazy').text))
        worksheet.write_string(row, 1, t(element.find('{*}NrKontrahenta')))        
        worksheet.write_string(row, 2, t(element.find('{*}NazwaKontrahenta')))
        worksheet.write_string(row, 3, t(element.find('{*}AdresKontrahenta')))
        nr_dokumentu= element.find('{*}DowodSprzedazy')
        worksheet.write_string(row, 4, nr_dokumentu.text)
        worksheet.write(row, 5, element.find('{*}DataWystawienia').text)
        worksheet.write(row, 6, t(element.find('{*}DataSprzedazy')))
         
        # Kolumny z deklaracji
        for k in range(10, 39):     
            wartosc= kwota(element.find('{{*}}K_{}'.format(k)))
            worksheet.write_number(row, k-3, wartosc, formatk)
            if not wartosc == 0.0:
                kolumny_zerowe[k-10]= False

        # Podsumowanie            
        
        # Liczenie podstawy i vat w wierszu 
        worksheet.write_formula(row, 36, ('={}'+('+{}'*14)).format(*([xl_rowcol_to_cell(row, k-3) for k in (
                                            10, 11, 13, 15, 17, 19, 21, 22, 23, 25, 27, 29, 31, 32, 34)]))) 
        worksheet.write_formula(row, 37, ('={}'+('+{}'*11)).format(*([xl_rowcol_to_cell(row, k-3) for k in (
                                            16, 18, 20, 24, 26, 28, 30, 33, 35, 36, 37, 38)])))
        # Podrejestr w komentarzu do pole z dowodem sprzedaży
        for podrejestr in nr_dokumentu.itertext():
            pass
        worksheet.write(row, 38, podrejestr) # t(element.find('{*}T_podrejestr')))
        
        
    # Podsumowanie kolumn kwotowych        
    for i in range(7, 38):
        worksheet.write_formula(0, i, '=SUBTOTAL(9,{}:{})'.format(xl_rowcol_to_cell(2, i), xl_rowcol_to_cell(row, i)))
    
    worksheet.autofilter('B2:AM{}'.format(row))   
    
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
            worksheet.set_column(i+7, i+7, None, None, {'hidden': True})
        else:
            niezerowe += 1
            
    if niezerowe>6:
        worksheet.set_column(6, 6, kolumny[6][0], None, {'hidden': True}) # data sprzedaży
    if niezerowe>10:
        worksheet.set_column(3, 3, kolumny[3][0], kolumny[3][1], {'hidden': True}) # adres
                                    
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
        ('Nr dostawcy', formath),        
        ('Nazwa dostawcy', formath),
        ('Adres dostawcy', formath),
        ('Nr faktury', formath),
        ('Data zakupu', formath),
        ('Data wpływu', formath),
    ]
    for k in range(43, 50):
        headers.append(('K_{}'.format(k), formathr))
        
    headers.append(('Podstawa', formatht))
    headers.append(('Podatek naliczony', formatht))
    headers.append(('Rejestr', formatht))
    
    worksheet.set_row(1, 30, formath)
    for i, h in enumerate(headers):
        worksheet.write(1, i, h[0], h[1])

    # Data columns format
    formatr= workbook.add_format({'align': 'center'})
    formatk= workbook.add_format({'num_format': '#,##0.00', 'font_size': 13})
    formats= workbook.add_format({'num_format': '#,##0.00', 'bg_color': '#E6E6E6'})    
    formato= workbook.add_format({'text_wrap': True})
        
    kolumny= [(6, formatr),
              (12,),
              (35, formato),
              (35, formato),
              (20,),
              (11,),              
              (11,),
              ]
    
    for k in range(43, 50):
        kolumny.append((13, formatk))
        
    kolumny.append((13, formats))
    kolumny.append((13, formats)) 
    kolumny.append((5,)) 
                
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
        worksheet.write(row, 1, element.find('{*}NrDostawcy').text)
        worksheet.write_string(row, 2, element.find('{*}NazwaDostawcy').text)
        worksheet.write_string(row, 3, element.find('{*}NazwaDostawcy').text)
        nr_faktury= element.find('{*}DowodZakupu')
        worksheet.write_string(row, 4, nr_faktury.text)
        worksheet.write(row, 5, element.find('{*}DataZakupu').text)
        worksheet.write(row, 6, element.find('{*}DataWplywu').text)        
        
        # Kolumny z deklaracji
        for k in range(43, 50):        
            worksheet.write_number(row, k-36, kwota(element.find('{{*}}K_{}'.format(k))), formatk)
            
        # Liczenie podstawy i vat w wierszu 
        worksheet.write_formula(row, 14, ('={}'+('+{}'*1)).format(*([xl_rowcol_to_cell(row, k) for k in (7, 9)]))) 
        worksheet.write_formula(row, 15, ('={}'+('+{}'*4)).format(*([xl_rowcol_to_cell(row, k) for k in (8, 10, 11, 12, 13)])))
        
        # Podrejestr z komentarza w numerze faktury
        for podrejestr in nr_faktury.itertext():
            pass
        worksheet.write(row, 16, podrejestr) # t(element.find('{*}T_podrejestr')))         
            
    # Podsumowanie kolumn kwotowych        
    for i in range(7, 16): 
        worksheet.write_formula(0, i, '=SUBTOTAL(9,{}:{})'.format(xl_rowcol_to_cell(2, i), xl_rowcol_to_cell(row, i)))
    
    worksheet.autofilter('B2:P{}'.format(row))   
            
    worksheet.freeze_panes(2, 7) 
    worksheet.set_selection(2, 7, 2, 7)
    if ZOOM:        
        worksheet.set_zoom(75)

    worksheet.set_landscape()
    worksheet.set_margins(left=0.5, right=0.3, top=0.6, bottom=0.45) 
    worksheet_header(worksheet, jpk, 'Zakup')       
    worksheet.repeat_rows(1)
    worksheet.print_area(0,0,row,13)
    
    format0= workbook.add_format({'color': '#FFFFFF'})            
    worksheet.conditional_format('G3:O{}'.format(row+1), {'type':     'cell',
                                        'criteria': '=',
                                        'value':    0,
                                        'format':   format0})
    
        
    