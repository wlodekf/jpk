# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import locale

ZOOM= True

def kwota(e):
    if e is None or not e.text or e.text is None:
        return 0.0
    else:
        return locale.atof(e.text)

def t(e):
    return e.text if e is not None and e.text else ''


def worksheet_header(worksheet, jpk, nazwa):
    worksheet.set_header('&L&10{}, {}&C&16&"Calibri,Bold"{} / {} &12 {} - {}&R&10&D &T'.format(
                        jpk.podmiot()['nazwa'].split(',')[0], 
                        jpk.podmiot()['miejscowosc'],
                        jpk.kod, 
                        nazwa, 
                        jpk.dataod, 
                        jpk.datado))
    
    worksheet.set_footer('&R&12 &P/&N')
    worksheet.fit_to_pages(1,0)        
    worksheet.set_paper(9)
    worksheet.hide_gridlines(0)

__all__= ['ZOOM', 'kwota', 't', 'worksheet_header']