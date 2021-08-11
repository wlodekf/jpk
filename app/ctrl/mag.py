# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from app import ctrl


class PZ(ctrl.CtrlTabeliMag):
    
    def __init__(self, jpk):
        super(PZ, self).__init__(jpk, {'symbol': 'PZ'}, False)

    def uwzglednij(self, i, dok):            
        rc= super(PZ, self).uwzglednij(i, dok)
        dok.ustal_zak_pz()
        return rc


class WZ(ctrl.CtrlTabeliMag):
    
    def __init__(self, jpk):
        super(WZ, self).__init__(jpk, {'symbol2': 'WZ'}, True)

    
class RW(ctrl.CtrlTabeliMag):
    
    def __init__(self, jpk):
        super(RW, self).__init__(jpk, {'symbol__in': ('RW', 'IR', 'WR')}, True)


class MM(ctrl.CtrlTabeliMag):
    
    def __init__(self, jpk):
        super(MM, self).__init__(jpk, {'symbol': 'MM'}, True)
    