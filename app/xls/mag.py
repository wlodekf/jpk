# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from xlsxwriter.utility import xl_rowcol_to_cell
from .utils import *

def pz(jpk, workbook, dom):
    """
    Utworzenie arkusza Excela z JPK_MAG
    """
    
    pzwz_wartosc(jpk, workbook, dom, 'PZ',  'Otrzymania', 'Dostawca')
    mag_wiersz(jpk, workbook, dom, 'PZ', 'Przyjeta')
    

def wz(jpk, workbook, dom):
    """
    Utworzenie arkusza Excela z JPK_MAG
    """
    
    pzwz_wartosc(jpk, workbook, dom, 'WZ', 'Wydania', 'OdbiorcaWZ')
    mag_wiersz(jpk, workbook, dom, 'WZ', 'Wydana')
    
    
def rw(jpk, workbook, dom):
    """
    Utworzenie arkusza Excela z JPK_MAG
    """
    
    rwmm_wartosc(jpk, workbook, dom, 'RW')
    mag_wiersz(jpk, workbook, dom, 'RW', 'Wydana')
    
    
def mm(jpk, workbook, dom):
    """
    Utworzenie arkusza Excela z JPK_MAG
    """
    
    rwmm_wartosc(jpk, workbook, dom, 'MM')
    mag_wiersz(jpk, workbook, dom, 'MM', 'Wydana')
    
    
            
def pzwz_wartosc(jpk, workbook, dom, symbol, kierunek, kontrahent):
        
    worksheet= workbook.add_worksheet('{} {} Wartosc'.format(jpk.mag3(), symbol))
    
    # Header
    formath= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#E6E6FF'})
    formathr= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'align': 'right', 'bg_color': '#E6E6FF'})
    
    headers= [
        ('Numer'+symbol,),
        ('Data'+symbol,),
        ('Wartosc'+symbol, formathr),
        ('Data'+kierunek+symbol, formathr),
        (kontrahent,),
        ('NumerFa'+symbol,), 
        ('DataFa'+symbol,), 
    ]
    
    worksheet.set_row(1, 30, formath)
    for i, h in enumerate(headers):
        worksheet.write(1, i, h[0], h[1] if len(h)>1 else formath)

    # Data columns format
    formatr= workbook.add_format({'align': 'center'})
    formatk= workbook.add_format({'num_format': '#,##0.00', 'font_size': 14})
    formats= workbook.add_format({'num_format': '#,##0.00', 'bg_color': '#E6E6E6'})    
    formato= workbook.add_format({'text_wrap': True})
    formatnrr= workbook.add_format({'bold': True, 'font_size': 12})
            
    kolumny= [(15,),
              (12,),
              (17, formatk),  
              (12,),
              (40, formato),
              (20,),
              (12,),
              ]
            
    for i, k in enumerate(kolumny):
        if len(k)>1:
            worksheet.set_column(i, i, k[0], k[1])
        else:
            worksheet.set_column(i, i, k[0])
    
    worksheet.write(0, 4, dom.find('{*}Magazyn').text, formato)
            
    # Writing data
    row= 1
    for element in dom.iter('{*}'+symbol+'Wartosc'):
        row += 1
        
        worksheet.write_string(row, 0, element.find('{*}Numer'+symbol).text)
        worksheet.write(row, 1, element.find('{*}Data'+symbol).text)
        
        worksheet.write_number(row, 2, kwota(element.find('{*}Wartosc'+symbol)))  
        worksheet.write(row, 3, element.find('{*}Data'+kierunek+symbol).text)  
                
        worksheet.write_string(row, 4, element.find('{*}'+kontrahent).text)
        worksheet.write_string(row, 5, t(element.find('{*}NumerFa'+symbol)))
        worksheet.write_string(row, 6, t(element.find('{*}DataFa'+symbol)))
                                        
    # Podsumowanie kolumn kwotowych        
    for i in (2,): 
        worksheet.write_formula(0, i, '=SUBTOTAL(9,{}:{})'.format(xl_rowcol_to_cell(2, i), xl_rowcol_to_cell(row, i)))
    
    worksheet.autofilter('A2:G{}'.format(row))   
            
    worksheet.freeze_panes(2, 2) 
    worksheet.set_selection(2, 3, 2, 3)
    if ZOOM:      
        worksheet.set_zoom(75)
    
    worksheet.set_portrait()
    worksheet.set_margins(left=0.5, right=0.3, top=0.5, bottom=0.3)  
    worksheet_header(worksheet, jpk, '{} {} Wartosc'.format(jpk.mag3(), symbol))      
    worksheet.repeat_rows(1)
    worksheet.print_area(0,0,row,6)
    
    format0= workbook.add_format({'color': '#FFFFFF'})            
    worksheet.conditional_format('C4:C{}'.format(row), {'type':     'cell',
                                        'criteria': '=',
                                        'value':    0,
                                        'format':   format0})


            
def rwmm_wartosc(jpk, workbook, dom, symbol):
        
    worksheet= workbook.add_worksheet('{} {} Wartosc'.format(jpk.mag3(), symbol))
    
    # Header
    formath= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#E6E6FF'})
    formathr= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'align': 'right', 'bg_color': '#E6E6FF'})
    
    headers= [
        ('Numer'+symbol,),
        ('Data'+symbol,),
        ('Wartosc'+symbol, formathr),
        ('DataWydania'+symbol, formathr),
        ('Skad'+symbol,), 
        ('Dokad'+symbol,), 
    ]
    
    worksheet.set_row(1, 30, formath)
    for i, h in enumerate(headers):
        worksheet.write(1, i, h[0], h[1] if len(h)>1 else formath)

    # Data columns format
    formatr= workbook.add_format({'align': 'center'})
    formatk= workbook.add_format({'num_format': '#,##0.00', 'font_size': 14})
    formats= workbook.add_format({'num_format': '#,##0.00', 'bg_color': '#E6E6E6'})    
    formato= workbook.add_format({'text_wrap': True})
    formatnrr= workbook.add_format({'bold': True, 'font_size': 12})
            
    kolumny= [(15,),
              (12,),
              (17, formatk),  
              (12,),
              (30, formato),
              (30, formato),
              ]
            
    for i, k in enumerate(kolumny):
        if len(k)>1:
            worksheet.set_column(i, i, k[0], k[1])
        else:
            worksheet.set_column(i, i, k[0])
    
    worksheet.write(0, 4, dom.find('{*}Magazyn').text, formato)
            
    # Writing data
    row= 1
    for element in dom.iter('{*}'+symbol+'Wartosc'):
        row += 1
        
        worksheet.write_string(row, 0, element.find('{*}Numer'+symbol).text)
        worksheet.write(row, 1, element.find('{*}Data'+symbol).text)
        
        worksheet.write_number(row, 2, kwota(element.find('{*}Wartosc'+symbol)))  
        worksheet.write(row, 3, element.find('{*}DataWydania'+symbol).text)  
                
        worksheet.write_string(row, 4, t(element.find('{*}Skad'+symbol)))
        worksheet.write_string(row, 5, t(element.find('{*}Dokad'+symbol)))
                                        
    # Podsumowanie kolumn kwotowych        
    for i in (2,): 
        worksheet.write_formula(0, i, '=SUBTOTAL(9,{}:{})'.format(xl_rowcol_to_cell(2, i), xl_rowcol_to_cell(row, i)))
    
    worksheet.autofilter('A2:F{}'.format(row))   
            
    worksheet.freeze_panes(2, 2) 
    worksheet.set_selection(2, 3, 2, 3)
    if ZOOM:      
        worksheet.set_zoom(75)
    
    worksheet.set_portrait()
    worksheet.set_margins(left=0.5, right=0.3, top=0.5, bottom=0.3)  
    worksheet_header(worksheet, jpk, '{} {} Wartosc'.format(jpk.mag3(), symbol))      
    worksheet.repeat_rows(1)
    worksheet.print_area(0,0,row,5)
    
    format0= workbook.add_format({'color': '#FFFFFF'})            
    worksheet.conditional_format('C4:C{}'.format(row), {'type':     'cell',
                                        'criteria': '=',
                                        'value':    0,
                                        'format':   format0})



def mag_wiersz(jpk, workbook, dom, symbol, kierunek):

    worksheet= workbook.add_worksheet('{} {} Wiersz'.format(jpk.mag3(), symbol))
    
    # Header
    formath= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#E6E6FF'})
    formathr= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'align': 'right', 'bg_color': '#E6E6FF'})
    
    headers= [
        ('Numer2'+symbol,),
        ('KodTowaru'+symbol,),
        ('NazwaTowaru'+symbol,),
        ('Ilosc{}{}'.format(kierunek, symbol), formathr),
        ('JednostkaMiary'+symbol,), 
        ('CenaJedn'+symbol, formathr), 
        ('Wartosc'+symbol, formathr),
    ]
    
    worksheet.set_row(1, 30, formath)
    for i, h in enumerate(headers):
        worksheet.write(1, i, h[0], h[1] if len(h)>1 else formath)

    # Data columns format
    formatr= workbook.add_format({'align': 'center'})
    formatk= workbook.add_format({'num_format': '#,##0.00', 'font_size': 14})
    formats= workbook.add_format({'num_format': '#,##0.00', 'bg_color': '#E6E6E6'})    
    formato= workbook.add_format({'text_wrap': True})
    formatnrr= workbook.add_format({'bold': True, 'font_size': 12})
    formati= workbook.add_format({'num_format': '#,##0.000'})   
            
    kolumny= [(15,),
              (12,),
              (40, formato),
              (12, formati),
              (10,),
              (15, formatk),
              (17, formatk),  
              ]
            
    for i, k in enumerate(kolumny):
        if len(k)>1:
            worksheet.set_column(i, i, k[0], k[1])
        else:
            worksheet.set_column(i, i, k[0])
    
    worksheet.write(0, 2, dom.find('{*}Magazyn').text, formato)
           
    formati1= workbook.add_format({'num_format': '#,##0.000'}) 
    formatk1= workbook.add_format({'num_format': '#,##0.00', 'font_size': 14})
    formato1= workbook.add_format({'text_wrap': True})
    
    formati2= workbook.add_format({'num_format': '#,##0.000', 'bg_color': '#E0E0E0'}) 
    formatk2= workbook.add_format({'num_format': '#,##0.00', 'font_size': 14, 'bg_color': '#E0E0E0'})
    formato2= workbook.add_format({'text_wrap': True, 'bg_color': '#E0E0E0'})
                    
    # Writing data
    row= 1
    pop_nr_dok, xi= '!@#', 2
    for element in dom.iter("{*}"+symbol+"Wiersz"):
        row += 1
        
        nr_dok= element.find('{*}Numer2'+symbol).text
        if nr_dok != pop_nr_dok:
            pop_nr_dok= nr_dok
            xi= 3 - xi
            if xi == 1:
                formatxi, formatxk, formatx= formati1, formatk1, formato1
            else:
                formatxi, formatxk, formatx= formati2, formatk2, formato2
                        
        worksheet.write_string(row, 0, element.find('{*}Numer2'+symbol).text, formatx)
        worksheet.write(row, 1, element.find('{*}KodTowaru'+symbol).text, formatx)
        worksheet.write(row, 2, element.find('{*}NazwaTowaru'+symbol).text, formatx)  
        
        worksheet.write_number(row, 3, kwota(element.find('{{*}}Ilosc{}{}'.format(kierunek, symbol))), formatxi)  
                
        worksheet.write_string(row, 4, t(element.find('{*}JednostkaMiary'+symbol)), formatx)
        worksheet.write_number(row, 5, kwota(element.find('{*}CenaJedn'+symbol)), formatxk) 
        worksheet.write_number(row, 6, kwota(element.find('{*}WartoscPozycji'+symbol)), formatxk) 
                                                        
    # Podsumowanie kolumn kwotowych        
    for i in (6,): 
        worksheet.write_formula(0, i, '=SUBTOTAL(9,{}:{})'.format(xl_rowcol_to_cell(2, i), xl_rowcol_to_cell(row, i)))
    
    worksheet.autofilter('A2:G{}'.format(row))   
            
    worksheet.freeze_panes(2, 2)
    worksheet.set_selection(2, 3, 2, 3)
    if ZOOM:
        worksheet.set_zoom(75)
    
    worksheet.set_portrait()
    worksheet.set_margins(left=0.5, right=0.3, top=0.5, bottom=0.3)
    worksheet_header(worksheet, jpk, '{} {} Wiersz'.format(jpk.mag3(), symbol))      
    worksheet.repeat_rows(1)
    worksheet.print_area(0,0,row,6)
    
    format0= workbook.add_format({'color': '#FFFFFF'})
    worksheet.conditional_format('F4:G{}'.format(row), {'type':     'cell',
                                        'criteria': '=',
                                        'value':    0,
                                        'format':   format0})
