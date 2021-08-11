# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime

from django.db import models

import logging
logger= logging.getLogger(__name__)


class Tworzenie(models.Model):
    """
    Informacja o zadaniu generowania faktur PDF.
    """
    
    uzytkownik= models.CharField(max_length= 10)
    zlecono= models.DateTimeField(default= datetime.datetime.now)
    
    od_daty= models.DateField()
    do_daty= models.DateField()
    zaklady= models.CharField(max_length= 50, null= True)
    tematy= models.CharField(max_length=100, null=True)
    pkwiu= models.CharField(max_length= 100, null= True)
    podpis= models.CharField(max_length= 10)
    grupowanie= models.CharField(max_length= 10, default= 'tematy')
    
    ile_faktur= models.IntegerField(default= 0)
    tmp_dir= models.CharField(max_length= 30, null= True)
    zakonczono= models.DateTimeField(null= True)
    ile_plikow= models.IntegerField(default= 0)
    rozmiar_zip= models.IntegerField(null= True, default= 0)
    pobrano= models.DateTimeField(null= True)
    usunieto= models.DateTimeField(null= True)
    
    ktora= models.IntegerField(default=0)
    stan= models.CharField(max_length= 100, null= True)

    class Meta:
        verbose_name= u'Generowanie faktur do PDF'
        verbose_name_plural= u'Informacja o generowaniu faktur do PDF'
        
        
class Faktura(models.Model):

    tworzenie= models.ForeignKey(Tworzenie)
    kiedy= models.DateTimeField(default= datetime.datetime.now)
    
    zaklad= models.CharField(max_length= 3)
    temat= models.CharField(max_length= 10)
    
    fak_id= models.IntegerField()
    nr_faktury= models.CharField(max_length= 15)
    data_wyst= models.DateField()
    data_sprz= models.DateField()
    zamowienie= models.CharField(max_length= 20, null= True)
    brutto= models.DecimalField(max_digits= 16, decimal_places= 2, default= 0.0)
    
    kon_id= models.IntegerField()
    kon_nazwa= models.CharField(max_length= 160, null= True)
    kon_miejsc= models.CharField(max_length= 30, null= True)
    
    data_rozp= models.DateField(null= True)
    zlc_nazwa= models.CharField(max_length= 300, null= True)
    zlc_sww= models.CharField(max_length= 20, null= True)
    
    opis= models.CharField(max_length= 1000, null= True)
    
    class Meta:
        unique_together = [
            ('tworzenie', 'id'),
        ]