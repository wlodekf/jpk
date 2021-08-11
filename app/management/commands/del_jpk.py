# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from app.models import Plik

class Command(BaseCommand):
    """
    Komenda manage.py do usuwania pliku JPK.
    """
    args = '<jpk_id jpk_id ...>'
    help = 'Usuwa podane pliki JPK'
    output_transaction= True

    def handle(self, *args, **options):
        
        force= False
        for jpk_id in args:
            
            if jpk_id == 'force':
                force= True
                continue
            
            try:
                jpk= Plik.objects.get(pk=int(jpk_id))
            except Plik.DoesNotExist:
                raise CommandError('Plik JPK "{}" nie istnieje'.format(jpk_id))

            if (jpk.upo or jpk.stan == 'DOSTARCZONY') and not force:
                raise CommandError('Plik JPK "{}" został dostarczony, nie może być usunięty'.format(jpk_id))                
            elif jpk.stan == 'SPRAWDZANY' and not force:
                raise CommandError('Plik JPK "{}" jest w trakcie przetwaraznia w MF, nie może być usunięty'.format(jpk_id))                 
            else:
                jpk.delete()
                self.stdout.write('Usunięto plik JPK "{}"'.format(jpk_id))
