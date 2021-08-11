# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
import datetime


class KonVat(models.Model):
    
    id= models.AutoField(primary_key= True)
    nip= models.CharField(max_length= 20)
    vat= models.CharField(max_length= 1)
    od_kiedy= models.DateTimeField(default= datetime.datetime.now) 
    ostatnio= models.DateTimeField(default= datetime.datetime.now) 
    aktualny= models.CharField(max_length= 1, default= "T") 
    sprawdzany= models.SmallIntegerField(default= 1)
    zmienil= models.CharField(max_length= 10, default= 'system')
        
    class Meta:
        managed= False        
        db_table= 'kon_vat'
        

class KonKrs(models.Model):
    
    id= models.AutoField(primary_key= True)
    nip= models.CharField(max_length= 20)
    
    nazwa= models.CharField(max_length= 160)
    skrot= models.CharField(max_length= 40)
    
    ulica= models.CharField(max_length= 40)
    kod= models.CharField(max_length= 20)
    miejscowosc= models.CharField(max_length= 30)
    
    wojewodztwo= models.CharField(max_length= 3)
    kraj= models.CharField(max_length= 3)
    email= models.CharField(max_length= 40)

    class Meta:
        managed= False
        db_table= 'kon_krs'
