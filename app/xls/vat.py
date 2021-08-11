# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from xlsxwriter.utility import xl_rowcol_to_cell
from .utils import *


def sprzedaz(jpk, workbook, dom):
    """
    Utworzenie arkusza Excela z
    """
    
    worksheet= workbook.add_worksheet('Sprzedaz')
    
    # Header
    formath= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#E6E6FF'})
    formathr= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'align': 'right', 'bg_color': '#E6E6FF'})
    formatht= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#1C901C', 'font_color': '#FFFFFF'})
        
    headers= [
        ('Lp sprzedaży', formath),
        ('Data sprzedaży', formath),
        ('Data wystawienia', formath),
        ('Nr dokumentu', formath),
        ('Nazwa nabywcy', formath),
        ('Adres nabywcy', formath),
        ('Pod/rejestr', formatht),
        ('Podstawa', formatht),
        ('Podatek należny', formatht),
    ]
    for k in range(10, 39):
        headers.append(('K_{}'.format(k), formathr))
    
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
              (11,),
              (11,),
              (16,),
              (35, formato),
              (35, formato),
              (5, formatt), 
              (13, formats),
              (13, formats),
              ]
    for k in range(10, 39):
        kolumny.append((13, formatk))
        
    for i, k in enumerate(kolumny):
        if len(k)>1:
            worksheet.set_column(i, i, k[0], k[1])
        else:
            worksheet.set_column(i, i, k[0])
                        
    # Writing data
    row= 1
    for element in dom.iter("{*}SprzedazWiersz"):
        row += 1
        
        worksheet.write_number(row, 0, int(element.find('{*}LpSprzedazy').text))
        worksheet.write(row, 1, t(element.find('{*}DataSprzedazy')))
        worksheet.write(row, 2, element.find('{*}DataWystawienia').text)
        nr_dokumentu= element.find('{*}NrDokumentu')
        worksheet.write_string(row, 3, nr_dokumentu.text)
        worksheet.write_string(row, 4, t(element.find('{*}NazwaNabywcy')))
        worksheet.write_string(row, 5, t(element.find('{*}AdresNabywcy')))
        
        for podrejestr in nr_dokumentu.itertext():
            pass
        worksheet.write(row, 6, podrejestr) # t(element.find('{*}T_podrejestr')))
        
        # Liczenie podstawy i vat w wierszu 
        worksheet.write_formula(row, 7, ('={}'+('+{}'*14)).format(*([xl_rowcol_to_cell(row, k) for k in (
                                            9, 10, 12, 14, 16, 18, 20, 21, 22, 24, 26, 28, 30, 31, 33)]))) 
        worksheet.write_formula(row, 8, ('={}'+('+{}'*11)).format(*([xl_rowcol_to_cell(row, k) for k in (
                                            15, 17, 19, 23, 25, 27, 29, 32, 34, 35, 36, 37)])))
         
        # Kolumny z deklaracji
        for k in range(10, 39):        
            worksheet.write_number(row, k-1, kwota(element.find('{{*}}K_{}'.format(k))), formatk)
            
    # Podsumowanie kolumn kwotowych        
    for i in range(7, 38): 
        worksheet.write_formula(0, i, '=SUBTOTAL(9,{}:{})'.format(xl_rowcol_to_cell(2, i), xl_rowcol_to_cell(row, i)))
    
    worksheet.autofilter('B2:AL{}'.format(row))   
    
    worksheet.freeze_panes(2, 5) 
    worksheet.set_selection(2, 5, 2, 5)
    if ZOOM:       
        worksheet.set_zoom(75)     

    worksheet.set_landscape()
    worksheet.set_margins(left=0.5, right=0.3, top=0.5, bottom=0.3)    
    worksheet_header(worksheet, jpk, 'Sprzedaż')
    worksheet.repeat_rows(1)
    worksheet.print_area(0,0,row,18)
    
    format0= workbook.add_format({'color': '#FFFFFF'})            
    worksheet.conditional_format('J3:AL{}'.format(row+1), {'type':     'cell',
                                        'criteria': '=',
                                        'value':    0,
                                        'format':   format0})    
    

def zakup(jpk, workbook, dom):
    """
    Utworzenie arkusza Excela z
    """
    
    worksheet= workbook.add_worksheet('Zakup')
    
    # Header
    formath= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#E6E6FF'})
    formathr= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'align': 'right', 'bg_color': '#E6E6FF'})
    formatht= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#1C901C', 'font_color': '#FFFFFF'})
    
    headers= [
        ('Lp zakupu', formath),
        ('Nazwa wystawcy', formath),
        ('Adres wystawcy', formath),
        ('Nr Id', formath),        
        ('Nr faktury', formath),
        ('Data wpływu', formath),
    ]
    for k in range(42, 49):
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
              (35, formato),
              (35, formato),
              (12,),
              (20,),
              (11,),              
              ]
    
    for k in range(10, 39):
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
        worksheet.write_string(row, 1, element.find('{*}NazwaWystawcy').text)
        worksheet.write_string(row, 2, element.find('{*}AdresWystawcy').text)
        worksheet.write(row, 3, element.find('{*}NrIdWystawcy').text)
        nr_faktury= element.find('{*}NrFaktury')
        worksheet.write_string(row, 4, nr_faktury.text)
        worksheet.write(row, 5, element.find('{*}DataWplywuFaktury').text)
        
        # Kolumny z deklaracji
        for k in range(42, 49):        
            worksheet.write_number(row, k-36, kwota(element.find('{{*}}K_{}'.format(k))), formatk)
            
        # Liczenie podstawy i vat w wierszu 
        worksheet.write_formula(row, 13, ('={}'+('+{}'*1)).format(*([xl_rowcol_to_cell(row, k) for k in (6, 8)]))) 
        worksheet.write_formula(row, 14, ('={}'+('+{}'*4)).format(*([xl_rowcol_to_cell(row, k) for k in (7, 9, 10, 11, 12)])))
        
        for podrejestr in nr_faktury.itertext():
            pass
        worksheet.write(row, 15, podrejestr) # t(element.find('{*}T_podrejestr')))         
            
    # Podsumowanie kolumn kwotowych        
    for i in range(6, 15): 
        worksheet.write_formula(0, i, '=SUBTOTAL(9,{}:{})'.format(xl_rowcol_to_cell(2, i), xl_rowcol_to_cell(row, i)))
    
    worksheet.autofilter('B2:P{}'.format(row))   
            
    worksheet.freeze_panes(2, 6) 
    worksheet.set_selection(2, 6, 2, 6)
    if ZOOM:        
        worksheet.set_zoom(75)

    worksheet.set_landscape()
    worksheet.set_margins(left=0.5, right=0.3, top=0.5, bottom=0.3) 
    worksheet_header(worksheet, jpk, 'Zakup')       
    worksheet.repeat_rows(1)
    worksheet.print_area(0,0,row,12)
    
    format0= workbook.add_format({'color': '#FFFFFF'})            
    worksheet.conditional_format('G3:O{}'.format(row+1), {'type':     'cell',
                                        'criteria': '=',
                                        'value':    0,
                                        'format':   format0})
    
        
    