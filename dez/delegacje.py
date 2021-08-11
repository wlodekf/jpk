# -*- coding: utf-8 -*-

"""
Wysyłanie powiadomień o konieczności rozliczenia zaliczki pobranej
na właśnie zakończoną delegację.
"""

from __future__ import unicode_literals

import datetime
import logging
import smtplib
import re

from email.mime.text import MIMEText

from django.shortcuts import render_to_response 
from django.template import RequestContext
from django.template import loader
from django.conf import settings

from fk.models import KasDow, Spo

logger= logging.getLogger(__name__)

ENV= 'prod' # dev, test, prod
EMAIL_SEND= True

AUTO_DOMAIN= {'dev': 'localhost', 'test': 'krezus3.gig.local', 'prod': 'krezus3.gig.local'}[ENV]
EMAIL_DOMAIN= {'dev': 'localhost', 'test': 'gw.local', 'prod': 'gw.local'}[ENV]

CC_NAMES= ['jwilaszek',
           'mgrabowska',
           'mborek',
           'stargos',
           'krezusfk'
          ]
PROD_CC= ['{}@{}'.format(name, EMAIL_DOMAIN) if not '@' in name else name for name in CC_NAMES]

# serwer pocztowy
EMAIL_SERVER= 'localhost' if ENV=='dev' else 'gw.gig.local'
EMAIL_FROM= 'automat@'+AUTO_DOMAIN
EMAIL_BCC= {'dev': ['krezusfk@'+EMAIL_DOMAIN], 'test': ['wlodekf@gmail.com'], 'prod': PROD_CC}[ENV]
EMAIL_REPLY= PROD_CC

SLO_KASY= 'KASY' # słownik walut w kasach
SLO_PRACO= 'PRACO'
OPE_DELEGACJI= '12' # operacja delegacji
KONIEC_SHIFT= 1 # przesunięcie od końca delegacji do powiadomienia
TERMIN_ROZLICZENIA= 14 # liczba dni na rozliczenie delegacji

S= lambda x: x.strip() if x else x


class Delegacje():
    
    def __init__(self):

        self.server= smtplib.SMTP(EMAIL_SERVER)
        if ENV != 'dev':
            self.server.login('faktury', '7H2wr123')
        self.server.set_debuglevel(1)
        
        self.KASA_WALUTA= Spo.objects.using(settings.LAST_DBS).filter(nr_slo= SLO_KASY)
        self.KASA_WALUTA= {S(x.spokod): S(x.pnazwa) for x in self.KASA_WALUTA if S(x.pnazwa) != 'PLN'}
        self.kasy_walutowe= self.KASA_WALUTA.keys()
        
        self.PRACO= {S(x.spokod): S(x.pnazwa) for x in Spo.objects.using(settings.LAST_DBS).filter(nr_slo= SLO_PRACO)}     
        

    def wyslij_przypomnienia(self):                
        """
        Wysyłka powiadomień do wszystkich pracowników,
        których delegacja skończyła się wczoraj.
        """
        
        for dowod in KasDow.objects.using(settings.LAST_DBS).filter(kasa__in= self.kasy_walutowe, 
                                                                    rodzaj= 'KW', 
                                                                    ksi__isnull= True).order_by('kpw_id'):
            
            pozycje= dowod.kaspoz_set.all()
            is_del= True
            
            for pozycja in pozycje:
                if pozycja.operacja != OPE_DELEGACJI:
                    is_del= False
                    break
                
            if not pozycje or not is_del: 
                continue
            
            try:
                if self.powiadom(dowod, pozycje[0]):
                    if ENV == 'prod' or ENV == 'dev': 
                        # Zaznaczenie, że powiadomienie zostało wysłane
                        dowod.ksi= 'E'
                        dowod.save()
            except Exception as exc:
                print(exc)

            if ENV == 'dev':
                break

        self.server.quit()
    
    
    def powiadom(self, dowod, pozycja):
        """
        Wysyłka powiadomienia do pracownika, który pobrał zaliczkę na delegację
        danym dowodem kasowym.
        """
        
        koniec= self.data_konca_delegacji(pozycja.opis)

        dowod.termin= koniec + datetime.timedelta(TERMIN_ROZLICZENIA)
        pozycja.waluta= self.waluta_w_kasie(dowod.kasa)
        pozycja.opis= re.sub('\s+', ' ', pozycja.opis)
        
        if koniec and dowod.data > koniec:
            # Rozliczenia po zakończeniu delegacji 
            # więc to nie jest pobranie zaliczki na delegację 
            print('To nie jest zaliczka na delegację', dowod.numer, dowod.data, pozycja.kwota, pozycja.waluta, koniec, pozycja.opis)
            return True
                            
        if not koniec or datetime.date.today() < koniec + datetime.timedelta(KONIEC_SHIFT):
            if koniec:
                print('Delegacja niezakończona', dowod.numer, dowod.data, pozycja.kwota, pozycja.waluta, koniec, pozycja.opis)
            return False # pomijamy
        
        
        template= loader.get_template('dez/email.txt')    
        tekst= template.render({'dow': dowod, 'poz': pozycja})
        
        msg= MIMEText(tekst, 'plain', 'utf-8')
        
        _from= EMAIL_FROM
        _to= self.email_to(dowod)
        _bcc= EMAIL_BCC 

        if not _to:
            return False
            
        msg['Subject']= 'Przypomnienie o rozliczeniu delegacji {}'.format(S(pozycja.rach))
        msg['From']= _from
        msg['To']= _to
        
        msg.add_header('Reply-To', ', '.join(EMAIL_REPLY))

        print('Powiadomienie', dowod.numer, dowod.data, pozycja.kwota, pozycja.waluta, koniec, pozycja.opis)
        
        if EMAIL_SEND:
            self.server.sendmail(_from, [_to]+_bcc, msg.as_string())
            return True
        else:     
            print(msg.as_string())
        
        return False

        
    def as_view(self, request):
        """
        Nie wykorzystywane.
        """
        return render_to_response('dez/email.txt', 
                            { 
                            }, 
                            context_instance= RequestContext(request))

    
    def waluta_w_kasie(self, kasa):
        """
        Ustalenie na podstawie odpowiedniego słownika jaka waluta jest
        w kasie o podanym kodzie.
        """
        return self.KASA_WALUTA.get(S(kasa))
    
    
    def data_konca_delegacji(self, opis):
        """
        Ustalenie daty końca delegacji.
        
        Data początkowa i końcowa delegacji zawarta jest w opisie pozycji
        dowodu kasowego (pole "opis").
        """
        
        m= re.search('\d?\d[\.\-]\d\d[\.\-]20\d\d', opis)
        if not m:
            return None
        
        koniec= m.group(0)
        if not koniec:
            return None 
        
        koniec= re.sub('-', '.', koniec)
        koniec= datetime.datetime.strptime(koniec, '%d.%m.%Y').date()
        
        return koniec

    def email_to(self, dowod):
        """
        Ustalenie adresu pracownika, do którego wysyłane jest zawiadomienie.
        
        Na podstawie numeru pracownika zapisanego w dowodzie kasowym
        ze słownika pracowników ustalane jest imię i nazwisko pracownika.
        Adres tworzony jest z pierwszej litery imienia i nazwiska (bez polskich znaków).
        """
        
        praco= self.PRACO.get(S(dowod.nr_pra))
        if not praco:
            return None
        
        praco= re.sub('\s+', ' ', praco) # kompresja spacji
        praco= praco.split(' ')
        
        nazwisko= praco[0]
        imie= praco[1]
        
        nazwisko= nazwisko.split('-')[0].translate(str.maketrans('ĄĆĘŁŃÓŚŹŻ', 'ACELNOSZZ'))
        
        pnazwa= imie[0]+nazwisko
        pnazwa= pnazwa.lower()

        return '{}@{}'.format({'dev': 'wlodek', 'test': 'faktury', 'prod': pnazwa}[ENV], EMAIL_DOMAIN)

