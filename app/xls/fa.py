# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from xlsxwriter.utility import xl_rowcol_to_cell
from .utils import *


def faktura(jpk, workbook, dom):
    """
    Utworzenie arkusza Excela z
    """
    
    worksheet= workbook.add_worksheet('Faktura')
    
    # Header
    formath= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#E6E6FF'})
    formathr= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'align': 'right', 'bg_color': '#E6E6FF'})
    
    headers= [
        ('P_1 data wystawienia',),
        ('P_2A nr faktury',),
        ('P_3A nazwa nabywcy',),
        ('P_3B adres nabywcy',),
        
        ('P_5A prefiks nabywcy',),
        ('P_5B nip nabywcy',),
        ('P_6 data sprzedaży',),

        ('P_13_1 netto 23%',),
        ('P_14_1 vat 23%',),
        ('P_13_2 netto 8%',),
        ('P_14_2 vat 8%',),
        ('P_13_3 netto 5%',),
        ('P_14_3 vat 5%',),
        ('P_13_4 netto OO',),
        ('P_14_4 vat OO',),
        ('P_13_5 netto NP',),
        ('P_14_5 vat NP',),        
        ('P_13_6 netto 0%',),
        ('P_13_7 netto ZW',),
        
        ('P_15 należność',),
        
        ('P_16 kasowa',),
        ('P_17 samo',),
        ('P_18 odwrot',),
        ('P_19 zwoln',),
        ('P_19A podstawa prawna',),
        ('P_20 egzek',),
        ('P_21 w imie',),
        ('P_23 3str',),
        ('P_106E_2 turyst',),
        
        ('RodzajFaktury',),
        ('PrzyczynaKorekty',),
        ('NrFaKorygowanej',),
        ('OkresFaKorygowanej',),
        
        ('ZAL Zapłata',),
        ('ZAL Podatek',),
        
        ('P_3C nazwa sprzedawcy',),
        ('P_3D adres sprzedawcy',),
        ('P_4A prefiks sprzedawcy',),
        ('P_4B nip sprzedawcy',),        
    ]
    
    worksheet.set_row(1, 34, formath)
    for i, h in enumerate(headers):
        worksheet.write(1, i, h[0], h[1] if len(h)>1 else formath)

    # Data columns format
    formatr= workbook.add_format({'align': 'center'})
    formatk= workbook.add_format({'num_format': '#,##0.00', 'font_size': 14})
    formats= workbook.add_format({'num_format': '#,##0.00', 'bg_color': '#E6E6E6'})    
    formato= workbook.add_format({'text_wrap': True})
        
    kolumny= [(10,),
              (15,),
              (30, formato),
              (30, formato),
              
              (3,),
              (12,),
              (10,),
              
              (15, formatk),  
              (15, formatk),  
              (15, formatk),  
              (15, formatk),  
              (15, formatk),  
              (15, formatk),  
              (15, formatk),  
              (15, formatk),                                                                                                    
              (15, formatk),  
              (15, formatk),  
              (15, formatk),  
              (15, formatk), 
                                          
              (15, formatk), 
              
              (5,),
              (5,),
              (5,),
              (5,), 
              (20,),
              (5,),
              (5,), 
              (5,),
              (5,),
              
              (8,),
              (30, formato),
              (15,),
              (10,),
              
              (12, formatk),  
              (10, formatk), 
                            
              (25, formato),
              (30, formato),              
              (3,),
              (12,),              
              ]
            
    for i, k in enumerate(kolumny):
        if len(k)>1:
            worksheet.set_column(i, i, k[0], k[1])
        else:
            worksheet.set_column(i, i, k[0])
                   
    # Writing data
    row= 1
    for element in dom.iter("{*}Faktura"):
        row += 1
        
        worksheet.write(row, 0, element.find('{*}P_1').text)
        worksheet.write_string(row, 1, element.find('{*}P_2A').text)
        worksheet.write_string(row, 2, element.find('{*}P_3A').text)
        worksheet.write_string(row, 3, element.find('{*}P_3B').text)
        
        worksheet.write(row, 4, t(element.find('{*}P_5A')))
        worksheet.write(row, 5, t(element.find('{*}P_5B')))
        worksheet.write(row, 6, t(element.find('{*}P_6')))
        
        worksheet.write_number(row, 7, kwota(element.find('{*}P_13_1')))  
        worksheet.write_number(row, 8, kwota(element.find('{*}P_14_1')))  
        worksheet.write_number(row, 9, kwota(element.find('{*}P_13_2')))  
        worksheet.write_number(row, 10, kwota(element.find('{*}P_14_2')))                          
        worksheet.write_number(row, 11, kwota(element.find('{*}P_13_3')))  
        worksheet.write_number(row, 12, kwota(element.find('{*}P_14_3')))  
        worksheet.write_number(row, 13, kwota(element.find('{*}P_13_4')))  
        worksheet.write_number(row, 14, kwota(element.find('{*}P_14_4'))) 
        worksheet.write_number(row, 15, kwota(element.find('{*}P_13_5')))  
        worksheet.write_number(row, 16, kwota(element.find('{*}P_14_5')))        
        worksheet.write_number(row, 17, kwota(element.find('{*}P_13_6')))  
        worksheet.write_number(row, 18, kwota(element.find('{*}P_13_7')))          
                
        worksheet.write_number(row, 19, kwota(element.find('{*}P_15')))
        
        worksheet.write(row, 20, element.find('{*}P_16').text)     
        worksheet.write(row, 21, element.find('{*}P_17').text)    
        worksheet.write(row, 22, element.find('{*}P_18').text)    
        worksheet.write(row, 23, element.find('{*}P_19').text)
        worksheet.write(row, 24, t(element.find('{*}P_19A')))
        worksheet.write(row, 25, element.find('{*}P_20').text)    
        worksheet.write(row, 26, element.find('{*}P_21').text)    
        worksheet.write(row, 27, element.find('{*}P_23').text)    
        worksheet.write(row, 28, element.find('{*}P_106E_2').text)

        worksheet.write(row, 29, element.find('{*}RodzajFaktury').text)
        worksheet.write(row, 30, t(element.find('{*}PrzyczynaKorekty')))
        worksheet.write(row, 31, t(element.find('{*}NrFaKorygowanej')))
        worksheet.write(row, 32, t(element.find('{*}OkresFaKorygowanej')))
        
        worksheet.write_number(row, 33, kwota(element.find('{*}ZALZaplata')))  
        worksheet.write_number(row, 34, kwota(element.find('{*}ZALPodatek')))  
                        
        worksheet.write_string(row, 35, element.find('{*}P_3C').text)
        worksheet.write_string(row, 36, element.find('{*}P_3D').text)
        worksheet.write_string(row, 37, element.find('{*}P_4A').text)
        worksheet.write_string(row, 38, element.find('{*}P_4B').text)        
                                
    # Podsumowanie kolumn kwotowych        
    for i in (7,8,9,10,11,12,13,14,15,16,17,18,19, 33,34): 
        worksheet.write_formula(0, i, '=SUBTOTAL(9,{}:{})'.format(xl_rowcol_to_cell(2, i), xl_rowcol_to_cell(row, i)))
    
    worksheet.autofilter('A2:AM{}'.format(row))   
            
    worksheet.freeze_panes(2, 3) 
    worksheet.set_selection(2, 3, 2, 3)
    if ZOOM:      
        worksheet.set_zoom(75)
    
        
    worksheet.set_landscape()
    worksheet.set_margins(left=0.5, right=0.3, top=0.5, bottom=0.3)    
    worksheet_header(worksheet, jpk, 'Faktura')
    worksheet.repeat_rows(1)
    worksheet.print_area(0,0,row,19)
    
    format0= workbook.add_format({'color': '#FFFFFF'})            
    worksheet.conditional_format('H3:T{}'.format(row), {'type':     'cell',
                                        'criteria': '=',
                                        'value':    0,
                                        'format':   format0})
    worksheet.conditional_format('AD3:AE{}'.format(row), {'type':     'cell',
                                        'criteria': '=',
                                        'value':    0,
                                        'format':   format0})    
    
        
    
def faktura_wiersz(jpk, workbook, dom):
    """
    Utworzenie arkusza Excela z
    """
    
    worksheet= workbook.add_worksheet('FakturaWiersz')
    
    # Header
    formath= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#E6E6FF'})
    formathr= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'align': 'right', 'bg_color': '#E6E6FF'})
    
    headers= [
        ('P_2B nr faktury', formath),
        ('P_7 nazwa', formath),
        ('P_8A jm', formath),
        ('P_8B ilość', formath),
        
        ('P_9A cena netto', formath),
        ('P_9B cena brutto', formath), 
        ('P_10 upusty', formath),
        ('P_11 netto', formath),
        ('P_11A brutto', formath),
        
        ('P_12 stawka vat', formath),                                               
    ]
    
    worksheet.set_row(1, 30, formath)
    for i, h in enumerate(headers):
        worksheet.write(1, i, h[0], h[1])

    # Data columns format
    formatr= workbook.add_format({'align': 'center'})
    formatk= workbook.add_format({'num_format': '#,##0.00', 'font_size': 14})
    formati= workbook.add_format({'num_format': '#,##0.000'})    
    formats= workbook.add_format({'num_format': '#,##0.00', 'bg_color': '#E6E6E6'})    
    formato= workbook.add_format({'text_wrap': True})
        
    kolumny= [(15,),
              (50, formato),
              (6,),
              (10, formati),
              (15, formatk),              
              (15, formatk),
              (6, formatk),
              (15, formatk),
              (15, formatk),
              (5,),
              ]
            
    for i, k in enumerate(kolumny):
        if len(k)>1:
            worksheet.set_column(i, i, k[0], k[1])
        else:
            worksheet.set_column(i, i, k[0])
                        
    # Writing data
    row= 1
    for element in dom.iter("{*}FakturaWiersz"):
        row += 1
        
        worksheet.write(row, 0, element.find('{*}P_2B').text)
        worksheet.write_string(row, 1, element.find('{*}P_7').text)
        worksheet.write_string(row, 2, element.find('{*}P_8A').text)
        worksheet.write_number(row, 3, kwota(element.find('{*}P_8B')))
        
        worksheet.write_number(row, 4, kwota(element.find('{*}P_9A')))
        worksheet.write_number(row, 5, kwota(element.find('{*}P_9B')))
        worksheet.write_number(row, 6, kwota(element.find('{*}P_10')))
        worksheet.write_number(row, 7, kwota(element.find('{*}P_11')))
        worksheet.write_number(row, 8, kwota(element.find('{*}P_11A')))
        
        worksheet.write(row, 9, t(element.find('{*}P_12')))
        
    # Podsumowanie kolumn kwotowych        
    for i in (4, 5, 6, 7, 8,): 
        worksheet.write_formula(0, i, '=SUBTOTAL(9,{}:{})'.format(xl_rowcol_to_cell(2, i), xl_rowcol_to_cell(row, i)))
    
    worksheet.autofilter('A2:J{}'.format(row))   
            
    worksheet.freeze_panes(2, 1) 
    worksheet.set_selection(2, 1, 2, 1)
    if ZOOM:      
        worksheet.set_zoom(75)

    worksheet.set_portrait()
    worksheet.set_margins(left=0.5, right=0.3, top=0.5, bottom=0.5)    
    worksheet_header(worksheet, jpk, 'FakturaWiersz')    
    worksheet.repeat_rows(1)
    worksheet.print_area(0,0,row,9)
    
    format0= workbook.add_format({'color': '#FFFFFF'})            
    worksheet.conditional_format('E3:I{}'.format(row), {'type':     'cell',
                                        'criteria': '=',
                                        'value':    0,
                                        'format':   format0})    
    
    