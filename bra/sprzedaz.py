# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import csv
import re
import datetime
import decimal

import asyncio
import websockets
import traceback

from django.conf import settings
from django.db.models import Max, Q

from fk.models import Kon, MagDok, MagWiersz, MagNumer

from .models import Faktura, Wiersz, ImportSprzedazy

su= lambda s: s.strip().upper() if s else s
ZERO= decimal.Decimal(0.0)

def cp1250_decoder(csv_data):
    """
    Dekodowanie danych z pliku CSV w standardzie Windows.
    Zastępowane są również podwójne apostrofy bo dekoder je przepuszcza.
    """
    for line in csv_data:
        line= line.decode('cp1250', errors= 'ignore')
        line= re.sub('\u201E', '"', line)
        line= re.sub('\u201D', '"', line)
        yield line
        
def ustal_delimiter(plik, przynajmniej):
    """
    Ustalenie czy delimiterem w pliku CSV jest średnik czy przecinek.
    csv.Snifer jakoś nie chce działać.
    """
    delim= ';'
    for p in cp1250_decoder(plik):
        if p.count(';') >= przynajmniej and p.count(',') < przynajmniej: 
            delim= ';'
            break
        if p.count(',') >= przynajmniej and p.count(';') < przynajmniej: 
            delim= ','
            break
    plik.seek(0)
    return delim



class Postep():
    """
    Obsługa wysyłania do przeglądarki 
    """
    
    def __init__(self):
        self.pop= 0
        self.connected= False
        self.stopped= False

    def loop_stop(self, loop):
        loop.stop()
    
#     def check_server(self, loop, ws_server):
#         print('Checking server: ', self.connected)
#         if not self.connected:
#             self.stopped= True
#             print(type(ws_server), dir(ws_server))
#             ws_server.close()
            
    def wykonaj(self, zadanie):
        
        print('starting event loop')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server= websockets.serve(zadanie, '0.0.0.0', 5678)
        print('trzy', type(start_server))
        
        
        loop= asyncio.get_event_loop()
        print('starting server')
        ws_server= loop.run_until_complete(start_server)
        print('ws_server', ws_server)
#         loop.call_later(1.0, self.check_server, loop, a)
        print('server started')
        loop.run_forever()
                
        print('loop.closing')
        loop.close()
 
    async def show_progress(self, websocket, i, ile):
#         if not self.stopped:
#             self.connected= True
#         else:
#             return
        
        ten= int(i/ile*100)
        if ten != self.pop:
            await websocket.send(str(ten))
            self.pop= ten
                        
    def stop_progress(self, websocket):
        websocket.ws_server.close()
        websocket.loop.call_later(0.1, self.loop_stop, websocket.loop) 
        
        
                                                                
class SprzedazImporter():
    """
    Importer sprzedaży do JPK_FA.
    
    Sprzedaż importowana jest z plików CSV w ustalonym formacie.
    Nagłówki faktur i wiersze zapisane powinny być w osobnych plikach.
    Po wczytaniu faktury i wiersze (opcjonalne) zapisywane są w tabelach 
    w bazie JPK.
    Mogą być również przeniesione do rejestru sprzedaży VAT w systemie FK.
    
    Importowana sprzedaż może być również wykorzystana do wgrywania do 
    rejestru sprzedaży VAT.
    """
    
    def __init__(self, firma= None, imp= None):
        super().__init__()
        
        if imp:
            self.firma= imp.firma.oznaczenie
            self.imp= imp
        else:
            self.firma= firma
            self.f_pominiete= 0
            self.w_pominiete= 0
    
    def sprzedaz_importuj(self, form, request):
        """
        Wczytanie faktur i wierszy z plików CSV i zapisanie w tabelach 
        Faktura i Wiersz.
        Przy okazji liczone są statystyki - liczby pozycji i sumy kwot
        na stawki VAT. 
        """
        
        # Utworzenie rekordu z podsumowaniem importu
        # Na razie tylko informacja o plikach i kto/kiedy
        self.imp= ImportSprzedazy.objects.create(
            firma= self.firma,
            faktury= form.cleaned_data['faktury'],
            wiersze= form.cleaned_data['wiersze'],
            kto= request.user.username
        )
        
        self.imp.nadpisane= 0
        
        # Import faktur i wierszy z wgranych plików z zapisem do bazy
        self.importuj_faktury(self.imp.faktury)
        self.importuj_wiersze(self.imp.wiersze)
            
        # Zapisanie liczby zaimportowanych faktur i wierszy
        self.imp.ile_faktur= self.ile_faktur()
        self.imp.ile_wierszy= self.ile_wierszy()
        self.imp.save()
        
                    
    def importuj_faktury(self, plik):
        """
        Zaimportowanie faktur sprzedaży z pliku CSV zapisanie ich w 
        bazie danych jpk w tablicach tymczasowych.
        """
        self.plik= plik
        
#         self.postep= Postep()
#         self.postep.wykonaj(self._importuj_faktury)
#                 
#     async def _importuj_faktury(self, websocket, path):
        
        self.faktury= []
        fak_reader= csv.reader(cp1250_decoder(self.plik), delimiter= ustal_delimiter(self.plik, 24))
        header= None
        
        self.imp.od_daty= None
        self.imp.do_daty= None
        
        ile= sum(1 for row in fak_reader)
        
        self.plik.seek(0)
        fak_reader= csv.reader(cp1250_decoder(self.plik), delimiter= ustal_delimiter(self.plik, 24))
                    
        for i, row in enumerate(fak_reader):
            
            # Pominięcie nagłówka
            if not header:
                header= '|'.join(row)
                continue
            
#             print('|'.join(row))
            
            # Pominięcie pustego wiersza
            if not row[0] or not row[1]:
                self.f_pominiete += 1
                continue
            
            fak= Faktura.from_csv(row, header)
            fak.import_sprzedazy= self.imp
        
            if not self.imp.od_daty or fak.data_wystawienia < self.imp.od_daty:
                self.imp.od_daty= fak.data_wystawienia
            if not self.imp.do_daty or fak.data_wystawienia > self.imp.do_daty:
                self.imp.do_daty= fak.data_wystawienia                
                    
            self.podsumuj(fak)
                        
            if Faktura.objects.filter(import_sprzedazy__firma= self.imp.firma, ident= fak.ident).exists():
                self.imp.nadpisane += 1
            
            self.przetworz_fak(fak)
            
            fak.save()
            
            self.faktury.append(fak)
            
#             await self.postep.show_progress(websocket, i, ile)            
            
#         self.postep.stop_progress(websocket)
                    
            
    def przetworz_fak(self, fak):
        """
        Dodatkowe przetworzenie faktury.
        """
        if self.firma.oznaczenie == 'printf':
            # Ustalenie konta sprzedaży na podstawie numeru projektu/zlecenia
            # zawartego w numerze faktury
            try:
                projekt= fak.nr_faktury.split('/')[2]
                fak.konto_spr= '7011'+projekt+'01'
            except:
                pass

                       
    def importuj_wiersze(self, plik):
        """
        Zaimportowanie wierszy faktur.
        """
        
        def fak_pozycji(poz_ident, faktury):
            for fak in faktury:
                if fak.ident == poz.ident:
                    return fak
            return None
                
        self.wiersze= []
        if not plik: return 
        
        poz_reader= csv.reader(cp1250_decoder(plik), delimiter= ustal_delimiter(plik, 9))
        header= None
        
        for row in poz_reader:
            
            # Pominięcie nagłówka
            if not header:
                header= '|'.join(row)
                continue
            
            # Pominięcie pustego wiersza
            if not row[0] or not row[1]:
                self.w_pominiete += 1
                continue
            
            poz= Wiersz.from_csv(row, header)
            poz.firma= self.firma
            poz.faktura= fak_pozycji(poz.ident, self.faktury)
            poz.save()
            self.wiersze.append(poz)
            
            
    def sprzedaz_akceptuj(self):
        """
        Akceptacja faktur.
        """
#         self.postep= Postep()
#         self.postep.wykonaj(self._sprzedaz_akceptuj)
#         
#     
#     async def _sprzedaz_akceptuj(self, websocket, path):
        """
        Faktury zostały już wczytane, teraz usuwane są duplikaty, tzn. jeżeli
        w danym imporcie są faktury, które już były w bazie to te stare są usuwane.
        """
        faktury= Faktura.objects.filter(import_sprzedazy= self.imp)
        ile= len(faktury)
        pop= 0
        
        self.imp.nadpisane= 0
        for i, fak in enumerate(faktury):
            # Sprawdzenie czy faktura o podanym ident już istnieje
            # Jeżeli tak to jest usuwana (a w jej miejsce będzie wstawiona nowa) 
            f= Faktura.objects.filter(Q(import_sprzedazy__firma= self.imp.firma, ident= fak.ident) & ~Q(pk= fak.pk))
            if f:
                f.delete()
                self.imp.nadpisane += 1
                
#             await self.postep.show_progress(websocket, i, ile)
                    
        self.imp.save()
                
#         self.postep.stop_progress(websocket)
        
                    
    def ile_faktur(self):
        return len(self.faktury)
    
    def ile_wierszy(self):
        return len(self.wiersze)

    def podsumuj(self, fak):
        """
        Ustalenie liczby faktur z poszczególnymi stawkami oraz
        sum netto i vat w poszczególnych stawkach. 
        """
        i= self.imp
        
        if fak.netto_23 or fak.vat_23: i.ile_23 += 1
        i.netto_23 += fak.netto_23
        i.vat_23 += fak.vat_23

        if fak.netto_8 or fak.vat_8: i.ile_8 += 1        
        i.netto_8 += fak.netto_8
        i.vat_8 += fak.vat_8
        
        if fak.netto_5 or fak.vat_5: i.ile_5 += 1        
        i.netto_5 += fak.netto_5
        i.vat_5 += fak.vat_5
        
        if fak.netto_0: i.ile_0 += 1      
        i.netto_0 += fak.netto_0

        if fak.netto_zw: i.ile_zw += 1        
        i.netto_zw += fak.netto_zw
        
        i.naleznosc += fak.naleznosc

        
        
class SprzedazRejestrVAT():
    """
    Przenoszenie zaimportowanej sprzedaży do rejestru sprzedaży VAT w systemie FK.
    """
    
    def __init__(self, imp= None):
        super().__init__()
        
        self.imp= imp
        self.firma= imp.firma.oznaczenie
    
    def do_rejestru(self, form):
        self.form= form
        
#         self.postep= Postep()
#         self.postep.wykonaj(self._do_rejestru)
#             
#             
#     async def _do_rejestru(self, websocket, path):
        """
        Zapisanie zaimportowanych faktur sprzedaży do rejestru sprzedaży.
        
        Być może powinno być tak, że import dotyczy tylko jednego podrejestru VAT
        i powinien być podawany przy upload (albo przy zapisie do rejestru).
        """
    
        # Zapamiętanie fakturu zapisu do rejestru sprzedaży
        self.imp.do_rejestru= True
        self.imp.rejestr= self.form.cleaned_data['rejestr']
        self.imp.konto_kon= re.sub('[- ]', '', self.form.cleaned_data['konto_kon'])
        self.imp.konto_spr= re.sub('[- ]', '', self.form.cleaned_data['konto_spr'])
        self.imp.save()
        
        miesiac= None
        numer= None
        
        faktury= self.imp.faktura_set.all().order_by('data_wystawienia', 'nr_faktury')
        ile= len(faktury)
        
        for i, f in enumerate(faktury):
            
            kon= self.ustal_kon(f)
            
            fak= MagDok()
            
            fak.nr_dysp= f.id # powiązanie z importem (dane do JPK_FA)
            
            fak.stat= 'D'
            fak.korekta= 'K' if f.korygujaca else 'D'
            fak.dzial= 'USL' 
            fak.symbol= 'FV'
            
            fak.rodz_te= self.imp.rejestr
             
            # Ewentualna zmiana rodz_te w rejestrze sprzedaży? 
            # łącznie z przenumerowaniem, ale jak uniknąć dziur?
            # Ewentualnie w rejestrze importu
            
            if not numer:
                miesiac= (f.data_wystawienia.year % 100)*100 + f.data_wystawienia.month
                numer= MagNumer.nastepny(dbs= self.imp.firma.oznaczenie, dzial= self.imp.rejestr, symbol= 'FR', korekta= 'D', rok= miesiac)
                self.imp.od_numeru= numer
                self.imp.od_daty= f.data_wystawienia
            else:
                numer += 1
                
            fak.numer= numer
            
            self.imp.do_numeru= numer
            self.imp.do_daty= f.data_wystawienia
             
            fak.kod_wydz= '000'
            fak.nr_dok= f.nr_faktury
            fak.data= f.data_wystawienia
            fak.data_sp= f.data_sprzedazy
            fak.id_kli= kon # ustalić na podstawie NIP, ewentualnie utworzyć nowego
            fak.nip= f.nip_nabywcy
            fak.upust_sp= 0 
            fak.upust_gt= 0
            fak.sp_zapl= 'P'
            fak.term_zapl= f.termin_platnosci or f.data_wystawienia
            fak.uwagi= f.uwagi
            
            if not fak.uwagi:
                for w in f.wiersz_set.all().order_by('id'):
                    fak.uwagi= w.nazwa.upper()
                    break
            
            fak.wart_det= 0
            fak.wart_bru= f.naleznosc
            fak.zaplata= 0
            fak.data_pod= f.data_sprzedazy
            fak.dni_na_zapl= (fak.term_zapl- fak.data).days
            fak.zaplacone= 0
            
            # Korekta
            fak.nr_dow2= f.nr_korygowanej
            fak.data2= f.data_korygowanej 
            
            # Zapisanie konta kontrahenta w polu zamów
            # Automat dekretujący odpowiednio to obsłuży dekretując na to konto
            # zamiast domyślne
            fak.zamow= self.imp.konto_kon or f.konto_kon
            fak.zamow= fak.zamow.strip() if fak.zamow else None
            
            fak.save(using= settings.DBS(self.firma))
            
            naleznosc= decimal.Decimal(0)

            if True:            
                naleznosc += self.wiersz_nag(fak, f, '23', f.netto_23, f.vat_23)
                naleznosc += self.wiersz_nag(fak, f, ' 8', f.netto_8, f.vat_8)
                naleznosc += self.wiersz_nag(fak, f, ' 5', f.netto_5, f.vat_5)
                naleznosc += self.wiersz_nag(fak, f, ' 0', f.netto_0, ZERO)
                naleznosc += self.wiersz_nag(fak, f, 'ZW', f.netto_zw, ZERO)
            else:
                for w in f.wiersz_set.all():
                    naleznosc += self.wiersz(fak, w)
                         
            if naleznosc != fak.wart_bru:
                fak.uwagi= 'NIEZGODNOŚĆ WARTOŚCI POZYCJI I NALEŻNOŚCI {} vs. {}'.format(naleznosc, fak.wart_bru) 
                fak.save()
                
            f.fak_id= fak.id
            f.save(update_fields=['fak_id'])
            
#             await self.postep.show_progress(websocket, i, ile)            
            
        if numer and miesiac:
            MagNumer.ostatni(dbs= self.imp.firma.oznaczenie, dzial= self.imp.rejestr, symbol= 'FR', korekta= 'D', rok= miesiac, numer= numer+1)            
            
        self.imp.save()
        
#         self.postep.stop_progress(websocket)        
        
        return numer


    def wiersz_nag(self, fak, f, stawka, netto, vat):
        if netto != ZERO or vat != ZERO:
            wie= MagWiersz()
            
            wie.id_dok= fak
            wie.il_dysp= -1
            wie.il_real= -1
            wie.cena_real= netto
            wie.cena_ewid= vat
            wie.vat= stawka
            wie.wartosc= netto + vat
            wie.rodzaj= '01'
            wie.konto= self.imp.konto_spr or f.konto_spr
            if self.firma == 'printf':
                try:
                    wie.konto += (stawka if re.match('[A-Z]+', stawka) else '{:02d}'.format(int(stawka.strip())))
                except:
                    traceback.print_exc()
            wie.konto= wie.konto.strip() if wie.konto else None          
                        
            wie.save(using= settings.DBS(self.firma))
            
            return wie.wartosc
        else:
            return ZERO

        
    def wiersz(self, fak, w):
        """
        Zapisanie do podanej faktury kolejnego wiersza.
        """
        wie= MagWiersz()
        
        wie.id_dok= fak
        wie.il_dysp= -w.ilosc
        wie.il_real= -w.ilosc
        wie.jm= w.jm
        wie.cena_real= w.netto
        wie.cena_ewid= w.brutto - w.netto
        wie.vat= w.stawka
        wie.wartosc= w.brutto
        wie.rodzaj= '01'
        wie.upust= w.upust
        wie.konto= '732170090123'
        
        wie.save(using= settings.DBS(self.firma))
        
        return wie.wartosc

    def adres_kon(self, adres):
        m= re.match('(.*)(\d\d\-\d\d\d)(.*)', adres)
        if m:
            return m.group(1), m.group(2), m.group(3)
        return adres[:40], '', adres[40:70]

        
    def ustal_kon(self, f):
        """
        Ustalenie kontrahenta na podstawie numeru NIP.
        """
        kon= Kon.objects.using(settings.DBS(self.firma)).filter(id= f.nip_nabywcy)
        if kon:
            return kon[0]
        
        kon= Kon()
        
        # Numer dla zagranicznego
        nr_kon= Kon.objects.using(settings.DBS(self.firma)).exclude(nr_kon__startswith= 'Z').aggregate(Max('nr_kon'))
        kon.nr_kon= '{:05d}'.format(int(nr_kon['nr_kon__max'].strip())+1)

        if '/' in f.nazwa_nabywcy:
            kon.skrot, kon.nazwa= f.nazwa_nabywcy.split('/')
        else:
            kon.nazwa= f.nazwa_nabywcy
        
        kon.id= f.nip_nabywcy
        kon.idtyp= 'NIPUE' if re.match('[A-Z][A-Z]', f.nip_nabywcy) else 'NIP'
        kon.ulica, kon.kod, kon.miejsc= self.adres_kon(f.adres_nabywcy)
         
        kon.kraj= f.nip_nabywcy[:2] if re.match('[A-Z][A-Z]', f.nip_nabywcy) else 'PL'
        
        kon.id_obcy= f.id # zapamiętanie skąd się zwiął (faktura)
        
        kon.skrot= su(kon.skrot)
        kon.nazwa= su(kon.nazwa)
        kon.miejsc= su(kon.miejsc)
        kon.ulica= su(kon.ulica)
        
        kon.kiedy= datetime.date.today() # data utworzenia
        kon.data_us= kon.kiedy
        if f.termin_platnosci and f.data_wystawienia:
            kon.term_zap= (f.termin_platnosci - f.data_wystawienia).days
        
        kon.save(using= settings.DBS(self.firma))
        
        return kon
    
