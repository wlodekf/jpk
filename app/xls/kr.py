# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from xlsxwriter.utility import xl_rowcol_to_cell
from .utils import *

def datastr_msc(data):
    if not data: return ''
    return data[:4]+'/'+data[5:7]


def zois(jpk, workbook, dom):
    """
    Utworzenie arkusza Excela z Zestawieniem Obrotów i Sald
    """
    
    worksheet= workbook.add_worksheet('ZOiS')
    
    headers= [
        'Kod Konta',
        'Opis Konta',
        'Bilans Otwarcia Winien',
        'Bilans Otwarcia Ma',
        'Obroty Winien',
        'Obroty Ma',
        'Obroty Winien Narast',
        'Obroty Ma Narast',
        'Saldo Winien',
        'Saldo Ma',
        'Typ Konta',
        'Kod Zespolu',
        'Opis Zespolu',
        'Kod Kategorii',
        'Opis Kategorii',
    ]

    # Header
    formath= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#E6E6FF'})
    formathk= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'align': 'right', 'bg_color': '#E6E6FF'})
    formats= workbook.add_format({'bold': True, 'align': 'right', 'text_wrap': True})

    worksheet.set_row(2, 30, formath)    
    worksheet.write_row(2, 0, headers[:2], formath)
    worksheet.write_row(2, 2, headers[2:10], formathk)
    worksheet.write_row(2, 10, headers[10:], formath)   
    worksheet.write('B1', 'SUMA', formats)
    worksheet.write('B2', 'SALDO', formats)
    
    # Data columns format
    formatc= workbook.add_format({'font_name': 'Courier New', 'font_size': 10})
    formatk= workbook.add_format({'num_format': '#,##0.00'})
    formatr= workbook.add_format({'font_size': 10})
            
    worksheet.set_column('A:A', 18)
    worksheet.set_column('B:B', 47, formatc)
    worksheet.set_column('C:J', 15, formatk)
    
    worksheet.set_column('K:K', 15, formatr)
    worksheet.set_column('L:L',  5, formatr)
    worksheet.set_column('M:M', 30, formatr)
    worksheet.set_column('N:N',  5, formatr)
    worksheet.set_column('O:O', 40, formatr)
    
    # Writing data
    row= 2
    for element in dom.iter("{*}ZOiS"):
        row += 1
        
        worksheet.write_string(row, 0, element.find('{*}KodKonta').text)
        worksheet.write_string(row, 1, element.find('{*}OpisKonta').text or '')

        worksheet.write_number(row, 2, kwota(element.find('{*}BilansOtwarciaWinien')))
        worksheet.write_number(row, 3, kwota(element.find('{*}BilansOtwarciaMa')))
        worksheet.write(row, 4, kwota(element.find('{*}ObrotyWinien')))
        worksheet.write(row, 5, kwota(element.find('{*}ObrotyMa')))
        worksheet.write(row, 6, kwota(element.find('{*}ObrotyWinienNarast')))
        worksheet.write(row, 7, kwota(element.find('{*}ObrotyMaNarast')))
        worksheet.write(row, 8, kwota(element.find('{*}SaldoWinien')))
        worksheet.write(row, 9, kwota(element.find('{*}SaldoMa')))
        
        worksheet.write_string(row, 10, element.find('{*}TypKonta').text)
        worksheet.write_string(row, 11, element.find('{*}KodZespolu').text)
        worksheet.write_string(row, 12, element.find('{*}OpisZespolu').text)
        worksheet.write_string(row, 13, element.find('{*}KodKategorii').text)
        worksheet.write_string(row, 14, element.find('{*}OpisKategorii').text)
        
    
    worksheet.freeze_panes(3, 2) 
    worksheet.set_selection(3, 2, 3, 2)
     
    # Podsumowania kolumn kwotowych sumy i salda obrotów
    for col in range(2, 10):
        worksheet.write_formula(0, col, '=SUBTOTAL(9,{}:{})'.format(xl_rowcol_to_cell(3, col), xl_rowcol_to_cell(row, col)))
      
    for col in (2,4,6,8):  
        wn, ma= xl_rowcol_to_cell(0, col), xl_rowcol_to_cell(0, col+1)
        worksheet.write_formula(1, col,   '=IF({}>{},{}-{},"")'.format(wn, ma, wn, ma))
        worksheet.write_formula(1, col+1, '=IF({}>{},{}-{},"")'.format(ma, wn, ma, wn))
                    
    worksheet.autofilter('K3:O{}'.format(row))
    if ZOOM:
        worksheet.set_zoom(75)
    
    worksheet.set_landscape()
    worksheet.set_margins(left=0.5, right=0.3, top=0.5, bottom=0.4)  
    worksheet_header(worksheet, jpk, 'ZOiS')  
    worksheet.repeat_rows(2)
    worksheet.print_area(0,0,row,9)
    
    format0= workbook.add_format({'color': '#FFFFFF'})            
    worksheet.conditional_format('C4:J{}'.format(row), {'type':     'cell',
                                        'criteria': '=',
                                        'value':    0,
                                        'format':   format0})  
    
            

def dziennik(jpk, workbook, dom):
    """
    Utworzenie arkusza Excela z Dziennika Księgowań
    """
    
    worksheet= workbook.add_worksheet('Dziennik')
    
    headers= [
        'Opis dziennika',
        'Lp zapisu',
        'Nr zapisu',
        'Nr dowodu',
        'Rodzaj dowodu',
        'Data operacji',
        'Data dowodu',
        'Data księgowania',
        'Kod operatora',
        'Opis operacji',
        'Kwota operacji',
        'Miesiąc operacji',
        'Miesiąc dowodu',
        'Miesiąc księgowania',
        'Miesiąc obrotów'
    ]

    # Header
    formath= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#E6E6FF'})
    formathr= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'align': 'right', 'bg_color': '#E6E6FF'})
    formatht= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#1C901C', 'font_color': '#FFFFFF'})
    
    worksheet.set_row(1, 30, formath)    
    worksheet.write_row(1, 0, headers[:2], formathr)
    worksheet.write_row(1, 2, headers[2:10], formath)
    worksheet.write_row(1, 10, headers[10:11], formathr)
    worksheet.write_row(1, 11, headers[11:], formatht)          
    
    # Data columns format
    formatl= workbook.add_format({'align': 'right'})
    formatk= workbook.add_format({'num_format': '#,##0.00'})
    formato= workbook.add_format({'text_wrap': True})    
            
    worksheet.set_column('A:A', 10)
    worksheet.set_column('B:C', 8, formatl)
    worksheet.set_column('D:D', 15)
    worksheet.set_column('E:E', 20, formato)
         
    worksheet.set_column('F:H', 12)
    worksheet.set_column('I:I', 10)
    worksheet.set_column('J:J', 40, formato)
    worksheet.set_column('K:K', 15, formatk)
    worksheet.set_column('L:O', 10)    
    
    # Writing data
    row= 1
    for element in dom.iter("{*}Dziennik"):
        row += 1
        
        worksheet.write_string(row, 0, element.find('{*}OpisDziennika').text)
        worksheet.write_number(row, 1, int(element.find('{*}LpZapisuDziennika').text))
        worksheet.write_number(row, 2, int(element.find('{*}NrZapisuDziennika').text))
        
        worksheet.write_string(row, 3, element.find('{*}NrDowoduKsiegowego').text)
        worksheet.write_string(row, 4, t(element.find('{*}RodzajDowodu')))
        
        d_operacji= element.find('{*}DataOperacji')
        d_dowodu= element.find('{*}DataDowodu')
        d_ksiegowania= element.find('{*}DataKsiegowania')
        
        worksheet.write_string(row, 5, d_operacji.text)
        worksheet.write_string(row, 6, d_dowodu.text)
        worksheet.write_string(row, 7, d_ksiegowania.text)
        
        worksheet.write_string(row, 8, element.find('{*}KodOperatora').text)
        worksheet.write_string(row, 9, element.find('{*}OpisOperacji').text or '')
        worksheet.write_number(row, 10, kwota(element.find('{*}DziennikKwotaOperacji')))
        
        worksheet.write_string(row, 11, datastr_msc(d_operacji.text)) # element.find('{*}T_msc_operacji').text)
        worksheet.write_string(row, 12, datastr_msc(d_dowodu.text)) # _element.find('{*}T_msc_dowodu').text)                
        worksheet.write_string(row, 13, datastr_msc(d_ksiegowania.text)) # element.find('{*}T_msc_ksiegowania').text)
        
        for msc_ksiegowania in d_ksiegowania.itertext():
            pass
        worksheet.write_string(row, 14, msc_ksiegowania) # element.find('{*}T_miesiac').text)                
        
    # Podsumowanie kolumn kwotowych        
    for i in (10,): 
        worksheet.write_formula(0, i, '=SUBTOTAL(9,{}:{})'.format(xl_rowcol_to_cell(2, i), xl_rowcol_to_cell(row, i)))
    
    worksheet.autofilter('A2:O{}'.format(row))  
        
    worksheet.freeze_panes(2, 0)
    if ZOOM:     
        worksheet.set_zoom(75)
    
    worksheet.set_portrait()
    worksheet.set_margins(left=0.5, right=0.3, top=0.6, bottom=0.5)    
    worksheet_header(worksheet, jpk, 'Dziennik')    
    worksheet.repeat_rows(1)
    worksheet.print_area(0,2,row,10)
    
        

def konto_zapis(jpk, workbook, dom):
    """
    Utworzenie arkusza Excela z Konto Zapis
    """
        
    worksheet= workbook.add_worksheet('KontoZapis')
    
    headers= [
        'Lp zapisu',
        'Nr zapisu',
        
        'Konto Wn',
        'Kwota Wn',
        'W walucie Wn',
        'Waluta Wn',
        'Opis Wn',
        
        'Konto Ma',
        'Kwota Ma',
        'W walucie Ma',
        'Waluta Ma',
        'Opis Ma'
    ]

    # Header
    formath= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#E6E6FF'})
    formathr= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'align': 'right', 'bg_color': '#E6E6FF'})
    
    worksheet.set_row(1, 30, formath)
    worksheet.write_row(1, 0, headers, formath)
    
    # Data columns format
    formata= workbook.add_format({'font_size': 14})    
    formatl= workbook.add_format({'align': 'left'})
    formatk= workbook.add_format({'num_format': '#,##0.00', 'font_size': 14})
    formato= workbook.add_format({'text_wrap': True})
             
    worksheet.set_column('A:A', 8, formatl)
    worksheet.set_column('B:B', 8, formatl)
        
    worksheet.set_column('C:C', 22, formata)
    worksheet.set_column('D:D', 17, formatk)
    worksheet.set_column('E:E', 12, formatk)    
    worksheet.set_column('F:F', 4)
    worksheet.set_column('G:G', 40, formato)
    
    worksheet.set_column('H:H', 22, formata)
    worksheet.set_column('I:I', 17, formatk)
    worksheet.set_column('J:J', 12, formatk)      
    worksheet.set_column('K:K', 4)
    worksheet.set_column('L:L', 40, formato)
        
    formatbb= workbook.add_format({'valign': 'top', 'font_size': 14, 'bg_color': '#E0E0E0', 'align': 'left'})
    formatbc= workbook.add_format({'valign': 'top', 'font_size': 14, 'align': 'left'})
    
    formatob= workbook.add_format({'valign': 'top', 'text_wrap': True, 'bg_color': '#E0E0E0'})
    formatoc= workbook.add_format({'valign': 'top', 'text_wrap': True})
    
    formatkb= workbook.add_format({'valign': 'top', 'font_size': 14, 'num_format': '#,##0.00', 'bg_color': '#E0E0E0'})
    formatkc= workbook.add_format({'valign': 'top', 'font_size': 14, 'num_format': '#,##0.00'})
        
    empty= [''] * 12
    
    # Writing data
    row= 1
    for element in dom.iter("{*}KontoZapis"):
        row += 1
    
        nr_zapisu= t(element.find('{*}NrZapisu'))
        if not nr_zapisu or nr_zapisu == 'None':
            nr_zapisu= 0
            
        if int(nr_zapisu) % 2 == 1:
            formatr= formatbb
            formatop= formatob
            formatkw= formatkb
        else: 
            formatr= formatbc
            formatop= formatoc
            formatkw= formatkc
            
        worksheet.write_row(row, 0, empty, formatr)    
                
        worksheet.write_number(row, 0, int(element.find('{*}LpZapisu').text), formatr)
        worksheet.write_number(row, 1, int(nr_zapisu), formatr)
        
        konto_wn= element.find('{*}KodKontaWinien')
        if konto_wn is not None and konto_wn.text != 'null':
            worksheet.write_string(row, 2, konto_wn.text, formatr)
            worksheet.write_number(row, 3, kwota(element.find('{*}KwotaWinien')), formatkw)
            
            kwota_wn_waluta= element.find('{*}KwotaWinienWaluta')
            if kwota_wn_waluta is not None: worksheet.write_number(row, 4, kwota(kwota_wn_waluta), formatkw)
            kod_waluty_wn= element.find('{*}KodWalutyWinien')
            if kod_waluty_wn is not None: worksheet.write_string(row, 5, kod_waluty_wn.text, formatr)
            opis_wn= element.find('{*}OpisZapisuWinien')
            if opis_wn is not None: worksheet.write_string(row, 6, opis_wn.text, formatop)

        konto_ma= element.find('{*}KodKontaMa')
        if konto_ma is not None and konto_ma.text != 'null': 
            worksheet.write_string(row, 7, konto_ma.text, formatr)
            worksheet.write_number(row, 8, kwota(element.find('{*}KwotaMa')),formatkw)
            
            kwota_ma_waluta= element.find('{*}KwotaMaWaluta')
            if kwota_ma_waluta is not None: worksheet.write_number(row, 9, kwota(kwota_ma_waluta), formatkw)
            kod_waluty_ma= element.find('{*}KodWalutyMa')
            if kod_waluty_ma is not None: worksheet.write_string(row, 10, kod_waluty_ma.text, formatr)
            opis_ma= element.find('{*}OpisZapisuMa')
            if opis_ma is not None: worksheet.write_string(row, 11, opis_ma.text, formatop)
    
    # Podsumowanie kolumn kwotowych        
    for i in (3,8): 
        worksheet.write_formula(0, i, '=SUBTOTAL(9,{}:{})'.format(xl_rowcol_to_cell(2, i), xl_rowcol_to_cell(row, i)))
    
    worksheet.autofilter('A2:L{}'.format(row))   
        
    worksheet.freeze_panes(2, 0)
    if ZOOM:     
        worksheet.set_zoom(75)   
        
    worksheet.set_portrait()
    worksheet.set_margins(left=0.5, right=0.3, top=0.6, bottom=0.4)
    
    worksheet_header(worksheet, jpk, 'KontoZapis')
    
    worksheet.print_area(0,1,row,11)
    worksheet.repeat_rows(1)

