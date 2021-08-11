# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from . import gig, ichp, bra
from . import vat
from fk.models import SysPar


def sprzedaz(jpk):
    
    if SysPar._gig():
        return gig.SprzedazGIG(jpk)
    if SysPar._ichp():
        return ichp.SprzedazICHP(jpk)
    if SysPar._bra():
        return bra.SprzedazBRA(jpk)



def zakup(jpk):
    
    if SysPar._gig():
        return gig.ZakupGIG(jpk)
    if SysPar._ichp():
        return ichp.ZakupICHP(jpk)
    if SysPar._bra():
        return bra.ZakupBRA(jpk)


    
def deklaracja(jpk):
    return vat.DeklaracjaVAT(jpk)
