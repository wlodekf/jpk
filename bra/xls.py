# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import xlsxwriter
from contextlib import closing
from io import BytesIO
from .models import Faktura
from xlsxwriter.utility import xl_rowcol_to_cell

def raport_kontrolny(imp):

    # Utworzenie pliku XLS
    output= BytesIO()
    
    with closing(xlsxwriter.Workbook(output)) as workbook:
        # Dodanie arkusza
        faktury_xls(imp, workbook)
    
    return output.getvalue()


def faktury_xls(imp, workbook):
    
    worksheet= workbook.add_worksheet('Faktury')
    kolumny_puste= [True]*27 # kolumny bez wartości / do schowania 
    row= 0
        
    def text(k, v, f= None):
        if type(v) == bool:
            v= 'T' if v else 'N'
        v= v.strip() if v else ''
        if v: kolumny_puste[k]= False
        worksheet.write(row, k, v, f)
        
    def data(k, v):
        v= v.strftime('%Y-%m-%d') if v else ''
        if v: kolumny_puste[k]= False
        worksheet.write(row, k, v)            

    def kwota(k, v):
        if v: kolumny_puste[k]= False
        worksheet.write_number(row, k, v)

                            
    formath= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#E6E6FF'})
    formathw= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'align': 'right', 'bg_color': '#E6E6FF'})

    headers= [
        ('Ident', ),
        ('Nr faktury', ),
        
        ('Data wystawienia', ),
        ('Data sprzedaży', ),
        ('Termin płatności', ),
                
        ('Nabywca', ),
        ('Adres', ),
        ('NIP', ),
        
        ('Należność', formathw),
        
        ('Netto 23%', formathw),
        ('Vat 23%', formathw),
        ('Netto 8%', formathw),
        ('Vat 8%', formathw),
        ('Netto 5%', formathw),
        ('Vat 5%', formathw),
        ('Netto 0%', formathw),
        ('Netto ZW', formathw),
                                                                        
        ('Korekta', ),
        ('Przyczyna korekty', ),
        ('Nr korygowanej', ),
        ('Data korygowanej', ),
        
        ('Zaliczkowa', ),
        ('Odwrotne', ), 
        ('Turystyka', ),
        
        ('Uwagi', ),
        ('Konto kon', ),
        ('Konto spr', ),                                              
    ]
    
    worksheet.set_row(1, 26, formath)
    for i, h in enumerate(headers):
        worksheet.write(1, i, h[0], h[1] if len(h)>1 else formath)

    # Data columns format
    
    formatw= workbook.add_format({'text_wrap': True, 'valign': 'top'})
    formatk= workbook.add_format({'num_format': '#,##0.00', 'valign': 'top'})
    formate= workbook.add_format({'bg_color': '#FFAAAA'})
                
    kolumny= [(10,),
              (15,),
              
              (10,),
              (10,),
              (10,),
                            
              (30, formatw), 
              (30, formatw),
              (11,),
              
              (12, formatk),
              
              (12, formatk),
              (12, formatk),                            
              (12, formatk),
              (12, formatk),
              (12, formatk),
              (12, formatk),
              (12, formatk),
              (12, formatk),
                   
              (3,),
              (20,),
              (15,),
              (10,),
               
              (3,),
              (3,),
              (3,),
                             
              (30, formatw),
              (10,),
              (10,)              
              ]
        
    for i, k in enumerate(kolumny):
        worksheet.set_column(i, i, k[0], k[1] if len(k)>1 else formatw)
            
    row= 1
    for f in Faktura.objects.filter(import_sprzedazy= imp).order_by('id'):
        row += 1
    
        text(0, f.ident)
        text(1, f.nr_faktury)

        data(2, f.data_wystawienia)
        data(3, f.data_sprzedazy)
        data(4, f.termin_platnosci)
                        
        text(5, f.nazwa_nabywcy)
        text(6, f.adres_nabywcy)
        if f.nip_poprawny():
            text(7, f.nip_nabywcy)
        else:
            text(7, f.nip_nabywcy, formate)
                
        kwota(8, f.naleznosc)

        kwota(9, f.netto_23)
        kwota(10, f.vat_23)
        
        kwota(11, f.netto_8) 
        kwota(12, f.vat_8)
        kwota(13, f.netto_5)
        kwota(14, f.vat_5)
        kwota(15, f.netto_0)
        kwota(16, f.netto_zw)
        
        text(17, f.korygujaca)
        text(18, f.przyczyna_korekty)
        text(19, f.nr_korygowanej)               
        data(20, f.data_korygowanej)
        
        text(21, f.zaliczkowa)               
        text(22, f.odwrotne)
        text(23, f.turystyka)
        
        text(24, f.uwagi)               
        text(25, f.konto_kon)
        text(26, f.konto_spr)
        
    # Podsumowanie kolumn kwotowych        
    for i in (8, 9, 10, 11, 12, 13, 14, 15, 16):
        worksheet.write_formula(0, i, '=SUBTOTAL(9,{}:{})'.format(xl_rowcol_to_cell(2, i), xl_rowcol_to_cell(row, i)))
                
    worksheet.autofilter('A2:AA{}'.format(row))  
    
    worksheet.freeze_panes(2, 3) 
    worksheet.set_selection(2, 5, 2, 5)
    
    worksheet.set_zoom(75)     

    worksheet.set_landscape()
    worksheet.set_margins(left=0.5, right=0.3, top=0.6, bottom=0.45)    
    
    format0= workbook.add_format({'color': '#FFFFFF'})            
    worksheet.conditional_format('I3:Q{}'.format(row+1), {'type':     'cell',
                                        'criteria': '=',
                                        'value':    0,
                                        'format':   format0})

    # Schowanie kolumn, które nie mają podanej żadnej wartości
    for i, pusta in enumerate(kolumny_puste):
        if pusta:
            worksheet.set_column(i, i, None, None, {'hidden': True})
                    
    worksheet_header(worksheet, 'Raport kontrolny importu sprzedaży', imp)
    
    worksheet.repeat_rows(1)
    worksheet.print_area(0,0,row,26)
    

def worksheet_header(worksheet, nazwa, imp):
    worksheet.set_header('&L&10{}, {}&C&16&"Calibri,Bold"{} &12&"Arial,Regular" &R&10&D &T'.format(
                        imp.firma.nazwa, 
                        imp.firma.miejscowosc,
                        nazwa
                        ))
    
    worksheet.set_footer('&R&12 &P/&N')
    worksheet.fit_to_pages(1,0)        
    worksheet.set_paper(9)
    worksheet.hide_gridlines(0)
