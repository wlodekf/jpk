# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import xlsxwriter
from contextlib import closing
from io import BytesIO
from .models import Faktura
from xlsxwriter.utility import xl_rowcol_to_cell

def raport_kontrolny(job, xls_path):

    print(xls_path)
    
    # Utworzenie pliku XLS
    output= BytesIO()
    
    with closing(xlsxwriter.Workbook(output)) as workbook:
        # Dodanie arkusza
        faktury_xls(job, workbook)
    
    with open(xls_path, 'wb') as f:
        f.write(output.getvalue())


def text(t):
    return t.strip() if t else ''
def data(d):
    return d.strftime('%Y-%m-%d') if d else ''    
    
    
def faktury_xls(job, workbook):
    
    worksheet= workbook.add_worksheet('Faktury')
    
    formath= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#E6E6FF'})
    formathw= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'align': 'right', 'bg_color': '#E6E6FF'})
        
    headers= [
        ('Zak', ),
        ('Temat', ),
        ('Nr faktury', ),
        ('Data wyst', ),
        ('Brutto', formathw),
        ('Opis pozycji', ),
        ('Odbiorca', ),
        ('Miejscowość', ),
        ('Data rozpocz', ),
        ('Data sprzedaży', ),
        ('Nazwa', ),
        ('PKWiU', ),
        ('Zamówienie', ),  
    ]
    
    worksheet.set_row(1, 15, formath)
    for i, h in enumerate(headers):
        worksheet.write(1, i, h[0], h[1] if len(h)>1 else formath)

    # Data columns format
    
    formatw= workbook.add_format({'text_wrap': True, 'valign': 'top'})
    formatk= workbook.add_format({'num_format': '#,##0.00', 'valign': 'top'})
            
    kolumny= [(4,),
              (10,),
              (14,),
              (10,),
              (12, formatk),
              
              (40, formatw), 
              (30, formatw),
              (15, formatw),
              
              (10,),
              (10,), 
              (40, formatw),
              (7,),
              (13, formatw)              
              ]
        
    for i, k in enumerate(kolumny):
        worksheet.set_column(i, i, k[0], k[1] if len(k)>1 else formatw)
                
    row= 1
    for f in Faktura.objects.filter(tworzenie= job).order_by('id'):
        row += 1
    
        print(f.zaklad, f.temat)
            
        worksheet.write(row, 0, text(f.zaklad))
        worksheet.write(row, 1, text(f.temat))
        worksheet.write(row, 2, text(f.nr_faktury)) 
        worksheet.write(row, 3, data(f.data_wyst))
        worksheet.write_number(row, 4, f.brutto)
        worksheet.write(row, 5, text(f.opis))
        
        worksheet.write(row, 6, text(f.kon_nazwa))
        worksheet.write(row, 7, text(f.kon_miejsc))
        
        worksheet.write(row, 8, data(f.data_rozp))                
        worksheet.write(row, 9, data(f.data_sprz))
        worksheet.write(row, 10, text(f.zlc_nazwa))
        worksheet.write(row, 11, text(f.zlc_sww))               
        worksheet.write(row, 12, text(f.zamowienie))
        
    # Podsumowanie kolumn kwotowych        
    for i in (4,):
        worksheet.write_formula(0, i, '=SUBTOTAL(9,{}:{})'.format(xl_rowcol_to_cell(2, i), xl_rowcol_to_cell(row, i)))
                
    worksheet.autofilter('A2:M{}'.format(row))  
    
    worksheet.freeze_panes(2, 3) 
    worksheet.set_selection(2, 5, 2, 5)
    
    worksheet.set_zoom(75)     

    worksheet.set_landscape()
    worksheet.set_margins(left=0.5, right=0.3, top=0.6, bottom=0.45)    
    
    worksheet_header(worksheet, 'Raport kontrolny faktur sprzedaży', job)
    
    worksheet.repeat_rows(1)
    worksheet.print_area(0,0,row,12)
    

def worksheet_header(worksheet, nazwa, job):
    warunki= '{}, {}, {}, {} - {}'.format(job.zaklady, job.tematy, job.pkwiu, job.od_daty, job.do_daty)
    worksheet.set_header('&L&10{}, {}&C&16&"Calibri,Bold"{} &12&"Arial,Regular" {} &R&10&D &T'.format(
                        'Główny Instytut Górnictwa', 
                        'Katowice',
                        nazwa,
                        warunki
                        ))
    
    worksheet.set_footer('&R&12 &P/&N')
    worksheet.fit_to_pages(1,0)        
    worksheet.set_paper(9)
    worksheet.hide_gridlines(0)
    