# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import xlsxwriter
from contextlib import closing
from io import BytesIO


def raport_kontrolny(imp, dane):

    # Utworzenie pliku XLS
    output= BytesIO()
    
    with closing(xlsxwriter.Workbook(output)) as workbook:
        # Dodanie arkusza
        sprzedaz_xls(imp, dane, workbook)
    
    return output.getvalue()


def sprzedaz_xls(imp, dane, workbook):
    
    worksheet= workbook.add_worksheet('Raport')
    kolumny_puste= [True]*27 
    row= 0
        
    def text(k, v, f= None):
        if type(v) == bool:
            v= 'T' if v else 'N'
        v= v.strip() if v else ''
        if v: kolumny_puste[k]= False
        worksheet.write(row, k, v, f)
        
    def data(k, v, f= None):
        v= v.strftime('%Y-%m-%d') if v else ''
        if v: kolumny_puste[k]= False
        worksheet.write(row, k, v, f)

    def kwota(k, v, f= None):
        if v: 
            kolumny_puste[k]= False
            worksheet.write_number(row, k, v, f)

                            
    formath= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'bg_color': '#E6E6FF'})
    formathw= workbook.add_format({'bold': True, 'valign': 'top', 'text_wrap': True, 'align': 'right', 'bg_color': '#E6E6FF'})

    headers= [
        ('Ident', ),
        ('Poz', ),
        
        ('Faktura', ),
        ('Data', ),
      
        ('Kon', ),
        ('NIP', ),
        ('Nazwa', ),
        ('Miasto', ),
        
        ('Rodzaj', ),
        ('Płatność', ),        

        ('Netto', formathw),
        ('VAT', formathw),  
        ('Brutto', formathw),
                
        ('Analityka', ),
        ('Projekt', ),
        ('Nr dok', ),
        ('Opis', ),
        
        ('Status', ),
        
        ('Rodzaj', ),
        ('Lp', ),
        ('Konto', ),
        ('Projekt', )
    ]
    
    worksheet.set_row(1, 26, formath)
    for i, h in enumerate(headers):
        worksheet.write(1, i, h[0], h[1] if len(h)>1 else formath)

    # Data columns format
    
    formatlp= workbook.add_format({'text_wrap': True, 'valign': 'top', 'align': 'left', 'color': '#A0A0A0'})
    formatli= workbook.add_format({'text_wrap': True, 'valign': 'top', 'align': 'left', 'bg_color': '#ddf3dd'})
        
    formatw= workbook.add_format({'text_wrap': True, 'valign': 'top'})

    formatkp= workbook.add_format({'num_format': '#,##0.00', 'valign': 'top', 'color': '#A0A0A0'})
    formatki= workbook.add_format({'num_format': '#,##0.00', 'valign': 'top', 'bg_color': '#ddf3dd'})
        
    formate= workbook.add_format({'bg_color': '#FFAAAA'})
    
    formatp= workbook.add_format({'color': '#A0A0A0', 'text_wrap': True, 'valign': 'top'})
    formati= workbook.add_format({'bg_color': '#ddf3dd', 'text_wrap': True, 'valign': 'top'})

    formats= workbook.add_format({'bg_color': '#E6E6FF', 'color': '#000000', 'text_wrap': True, 'valign': 'top'})
    
    kolumny= [(6, ),
              (6, ),
              
              (15, ),
              (10, ),
              
              (6, ),
              (12, ),
              (30, ),
              (10, ),
              
              (7,),
              (13,),
              
              (11, ),
              (11, ),
              (11, ),
              
              (20, ),
              (20, ),
              (8,),
              (15,),
              
              (10, ),
              
              (3, ),
              (5, ),
              (15, ),
              (10, )
    ]
        
    for i, k in enumerate(kolumny):
        worksheet.set_column(i, i, k[0], k[1] if len(k)>1 else formatw) 
        
    row= 1
    for k, fak in dane:
        row += 1
        
        row_h= 15
        if len(k['kon'].get('nazwa1', '')) > 30 or len(k['kontoAnalityczne'])>20 or len(k['projekt'])>20:
            row_h= 30

        if k['status'] == 'import':
            worksheet.set_row(row, row_h, cell_format= formati)
            formatl= formatli
            formatk= formatki
        else:
            worksheet.set_row(row, row_h, cell_format= formatp)
            formatl= formatlp
            formatk= formatkp
            
        kwota(0, k['identyfikatorNaglowka'], formatl)
        kwota(1, k['identyfikatorPozycji'], formatl)
        
        text(2, k['numerDokumentu'])
        text(3, k['dataWystawienia'][:10])
                
        kwota(4, k['idKontrahenta'], formatl)
        text(5, k['kon'].get('nip', '') )
        text(6, k['kon'].get('nazwa1', ''))
        text(7, k['kon'].get('miasto', ''))

        text(8, k['rodzajDokumentu'])
        text(9, k['metodaPlatnosci'])

        kwota(10, k['dekretNetto'], formatk)
        kwota(11, k['dekretVat'], formatk)
        kwota(12, k['dekretBrutto'], formatk)
        
        text(13, k['kontoAnalityczne'])
        text(14, k['projekt'])
        text(15, k['uwagi'])
        text(16, k['dekretTresc'])
        
        text(17, k['status'], formats)
        
        text(18, fak.rodz_te if fak else '')
        kwota(19, fak.numer if fak else None, formatl)
        text(20, k.get('fk_konto', ''))
        text(21, k.get('fk_zlecenie', ''))
        

#     worksheet.autofilter('A2:AA{}'.format(row))  
    
#     worksheet.set_column(17, 17, 10, cell_format= formats)
#     worksheet.set_column('R:R', 10, formats)
        
    worksheet.freeze_panes(2, 4)
 
    worksheet.set_selection(2, 5, 2, 5)
     
    worksheet.set_zoom(75)     

    worksheet.set_landscape()
    worksheet.set_margins(left=0.5, right=0.3, top=0.6, bottom=0.45)    
    
    format0= workbook.add_format({'color': '#FFFFFF'})
            
#     worksheet.conditional_format('I3:Q{}'.format(row+1), {'type':     'cell',
#                                         'criteria': '=',
#                                         'value':    0,
#                                         'format':   format0})

    worksheet_header(worksheet, 'Raport kontrolny importu zakupów', imp)
    
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
