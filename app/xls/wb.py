# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from xlsxwriter.utility import xl_rowcol_to_cell
from .utils import *

from app.models import Wyciag

def wyciag(jpk, workbook, dom):
    """
    Utworzenie arkusza Excela z JPK_WB
    """
    
    worksheet= workbook.add_worksheet(jpk.rach())
    
    # Header
    formath= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#E6E6FF'})
    formathr= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'align': 'right', 'bg_color': '#E6E6FF'})
    
    headers= [
        ('Lp',),
        ('Data operacji',),
        ('Kwota', formathr),
        ('Saldo', formathr),
        ('Nazwa podmiotu',),
        ('Opis operacji',), 
    ]
    
    worksheet.set_row(2, 30, formath)
    for i, h in enumerate(headers):
        worksheet.write(2, i, h[0], h[1] if len(h)>1 else formath)

    # Data columns format
    formatr= workbook.add_format({'align': 'center'})
    formatk= workbook.add_format({'num_format': '#,##0.00', 'font_size': 14})
    formats= workbook.add_format({'num_format': '#,##0.00', 'bg_color': '#E6E6E6'})    
    formato= workbook.add_format({'text_wrap': True})
    formatnrr= workbook.add_format({'bold': True, 'font_size': 12})
            
    kolumny= [(5,),
              (12,),
              (17, formatk),  
              (17, formatk),  
              (40, formato),
              (50, formato),
              ]
            
    for i, k in enumerate(kolumny):
        if len(k)>1:
            worksheet.set_column(i, i, k[0], k[1])
        else:
            worksheet.set_column(i, i, k[0])
    
    worksheet.write(0, 0, Wyciag.rachunek_pp(dom.find('{*}NumerRachunku').text), formatnrr)
            
    for salda in dom.iter("{*}Salda"):
        worksheet.write_number(0, 3, kwota(salda.find('{*}SaldoPoczatkowe')))
        worksheet.write_string(0, 4, 'Saldo początkowe')
        
        worksheet.write_number(1, 3, kwota(salda.find('{*}SaldoKoncowe'))) 
        worksheet.write_string(1, 4, 'Saldo końcowe')        
                               
    # Writing data
    row= 2
    for element in dom.iter("{*}WyciagWiersz"):
        row += 1
        
        worksheet.write(row, 0, element.find('{*}NumerWiersza').text)
        worksheet.write(row, 1, element.find('{*}DataOperacji').text)
        
        worksheet.write_number(row, 2, kwota(element.find('{*}KwotaOperacji')))  
        worksheet.write_number(row, 3, kwota(element.find('{*}SaldoOperacji')))  
                
        worksheet.write_string(row, 4, element.find('{*}NazwaPodmiotu').text)
        worksheet.write_string(row, 5, element.find('{*}OpisOperacji').text)
                                
    # Podsumowanie kolumn kwotowych        
    for i in (2,): 
        worksheet.write_formula(1, i, '=SUBTOTAL(9,{}:{})'.format(xl_rowcol_to_cell(3, i), xl_rowcol_to_cell(row, i)))
    
    worksheet.autofilter('A3:F{}'.format(row))   
            
    worksheet.freeze_panes(3, 3) 
    worksheet.set_selection(2, 3, 2, 3)
    if ZOOM:      
        worksheet.set_zoom(75)
    
    worksheet.set_portrait()
    worksheet.set_margins(left=0.5, right=0.3, top=0.5, bottom=0.3)  
    worksheet_header(worksheet, jpk, 'Wyciąg')      
    worksheet.repeat_rows(2)
    worksheet.print_area(0,0,row,5)
    
    format0= workbook.add_format({'color': '#FFFFFF'})            
    worksheet.conditional_format('C4:D{}'.format(row), {'type':     'cell',
                                        'criteria': '=',
                                        'value':    0,
                                        'format':   format0})

