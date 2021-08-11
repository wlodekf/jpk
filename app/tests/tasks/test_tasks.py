# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime

from app import tasks
from app.models import Plik
from .. import JpkTestCase

import logging
logging.disable(logging.CRITICAL)



class TasksTestCase(JpkTestCase):

    def test_niepoprawny_kres_blad_podczas_inicjalizacji(self):
        """
        Błąd podczas inicjalizacji generowania powoduje wyjątek oraz pusty xml.
        """
        
        self.jpk= Plik.objects.create(kod= 'JPK_VAT',
                                      dataod= datetime.date(2000,7,1),
                                      datado= datetime.date(2000,7,31),
                                      utworzony_user= 'test')
        
        with self.assertRaises(Exception) as e:
            self.jpk= tasks.JpkTask(self.jpk.id).run()
        
        self.assertIsNone(self.jpk.xml)


    def test_niepoprawny_kres_blad_podczas_generowania(self):
        """
        Błąd podczas generowania xml powoduje wyjątek oraz pusty xml.
        """
        
        self.jpk= Plik.objects.create(kod= 'JPK_FA',
                                      dataod= datetime.date(2000,7,1),
                                      datado= datetime.date(2000,7,31),
                                      utworzony_user= 'test')
        
        with self.assertRaises(Exception) as e:
            self.jpk= tasks.JpkTask(self.jpk.id).run()
        
        self.assertIsNone(self.jpk.xml)
