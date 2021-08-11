# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import decimal
import re

from app import ctrl, utils

from app.models import Deklaracja, DeklaracjaPoz
from fk.models import DefZrv, SysPar
from vat.models import KonVat

from vat.views import kon_nip_status, msg_statusu_nip

from .. import Pozycje


class SprzedazVAT(ctrl.CtrlTabeli):
    """
    Ewidencja sprzedaży VAT.
    """
    
    def __init__(self, *args, **kwargs):
        super(SprzedazVAT, self).__init__(*args, **kwargs)
        self.tabela= 'sprzedaz'        
        
    def sumuj(self, pozycje, element):
        super(SprzedazVAT, self).sumuj(pozycje, element)
        self.suma1 += element.podatek_nalezny
                    
    def uwzglednij(self, pozycje, fak):
        """
        Źródłem najpierw jest rejestr sprzedaży a później zakupów.
        """
        super(SprzedazVAT, self).uwzglednij(pozycje, fak)
        
        fak.podatek_nalezny= decimal.Decimal(0.00)
        
        for k in range(10, 40):
            setattr(fak, 'k_{}'.format(k), decimal.Decimal(0.0))

        uwz= pozycje.uwzglednij(fak)
        if uwz and self.jpk.wariant_dek:
            self.do_deklaracji(fak, 10, 39)
            
        return uwz


class SprzedazVATPozycjeFak(Pozycje):
    
    def przygotuj(self, fak):
        """
        Przygotowanie informacji pochodnych, kontrola poprawności oraz
        utworzenie podsumowania faktury stawkami VAT.
        
        Sposób postępowania wspólny dla wszystkich firm.
        """
        
        # Ustalenie i kontrola numeru dokumentu / faktury sprzedaży
        
        fak.nr_dokumentu= fak.nr_fak()
        if not fak.nr_dokumentu: # pragma: no cover
            fak.jpk.blad('SPR', fak.id, 'Nieokreślony numer dokumentu/faktury')
        
        # Ustalenie i kontrola daty wystawienia dokumentu / faktury sprzedaży
        
        fak.data_wystawienia= fak.data
        if not fak.data_wystawienia: # pragma: no cover
            fak.jpk.blad('SPR', fak.nr_dokumentu, 'Nieokreślona data wystawienia faktury sprzedaży')
            
        fak.data_sprzedazy= fak.data_sp if fak.data_sp and fak.data_sp != fak.data else None

        # Utworzenie podsumowania faktury wg stawek VAT
        # tak samo jak na wydruku faktury
        
        fak.podsum= {}
        for w in fak.wiersze.all():
            w.wartosc_wiersza(fak)
            
            if w.p_netto is None or w.p_vat is None or w.p_brutto is None: # pragma: no cover
                fak.jpk.blad('SPR', fak.nr_dokumentu, 'Nieokreślona wartość w pozycji faktury netto/vat/brutto {}/{}/{}'.format(w.p_netto, w.p_vat, w.p_brutto))
                                 
            st= fak.podsum.get(w.vat)
            if not st:
                fak.podsum[w.vat]= [w.p_netto, w.p_vat, w.p_brutto]
            else:
                st[0] += w.p_netto or decimal.Decimal(0)
                st[1] += w.p_vat or decimal.Decimal(0)
                st[2] += w.p_brutto or decimal.Decimal(0)


    def sprawdzenie_nip_sprzedazy(self, fak):
        """
        Sprawdzenie czy odbiorca/nabywca sprzedaży ma poprawny NIP.  
        """
        
        # Kontrahent zagraniczny - nie sprawdzamy
        if fak.id_kli and fak.id_kli.idtyp == 'IDENT':
            return
        
        nip= fak.nip_kon()
        nip= nip.replace('-', '')
        
        # Brak nip nie ma co sprawdzać
        if not nip or len(nip) == 0:
            return
        
        # NIP europejski - nie sprawdzamy
        if not nip or re.match('[A-Z][A-Z].*', nip):
            return

        # Ustalenie aktualnego statusu NIP z bazy lub webserwisu
        status= '?'
        kon_vat= KonVat.objects.filter(nip= nip, aktualny='T')
        if kon_vat:
            kon_vat= kon_vat[0]
            old = int(SysPar.get_wartosc('KON-NIP-SPRAWDZ-WIELE', fak.jpk))
            if kon_vat.ostatnio.date() >= datetime.date.today() - datetime.timedelta(days= old):
                status= kon_vat.vat

        if status == '?':
            try:
                status= kon_nip_status(nip)
            except Exception as e:
                print('Błąd w sprawdzanie_platnika_vat {}'.format(e))
                status= '?'

        msg, level= None, 'warn'
                
        if status in ('N', 'I'):
            msg, level= msg_statusu_nip(status)
                
        if msg:
            msg= msg.format(nip)
            fak.jpk.blad('FAK', fak.nr_dokumentu, msg, level= level)

        return
    

class ZakupVAT(ctrl.CtrlTabeli):
    """
    Kontrola zakupu VAT.
    """
    
    def __init__(self, jpk):
        super(ZakupVAT, self).__init__(jpk)
        self.tabela= 'zakup'
        
        if SysPar._bra(): return
            
        self.pre_wsp= DefZrv.pre_wsp(jpk.fkdbs('Zakup.pre_wsp {}'.format(jpk.dataod.year)), jpk.dataod.year)
        if self.pre_wsp[0] is None:
            jpk.blad('ZAK', 'WSP', 'Nie znaleziono prewspółczynnika dla {} w bazie {}'.format(jpk.dataod.year, jpk.fkdbs("pre_wsp")))
            self.pre_wsp= [100.00, 100.00]

        if jpk.dataod.month == 1 and jpk.dataod.day == 1:            
            self.pop_wsp= DefZrv.pre_wsp(jpk.fkdbs('Zakup.pre_wsp {}'.format(jpk.dataod.year-1)), jpk.dataod.year-1)
            if self.pop_wsp[0] is None:
                jpk.blad('ZAK', 'PRE', 'Nie znaleziono prewspółczynnika dla {} w bazie {}'.format(jpk.dataod.year-1, jpk.fkdbs('pop_wsp')))
                self.pop_wsp= [100.00, 100.00]


    def sumuj(self, pozycje, element):
        self.suma1 += element.podatek_naliczony


    def uwzglednij(self, pozycje, element):
                
        element.podatek_naliczony= decimal.Decimal(0.00)
        
        for k in range(43, 51):
            setattr(element, 'k_{}'.format(k), decimal.Decimal(0.00))
            
        uwz= pozycje.uwzglednij(element)
        if uwz and self.jpk.wariant_dek:
            self.do_deklaracji(element, 43, 48, -3)
            
        return uwz


    def vat_rozliczony(self, zak):

        zero= decimal.Decimal(0)
        if (zak.sop_i_net != zero or zak.sop_i_vat != zero or
            zak.sop_p_net != zero or zak.sop_p_vat != zero or
            zak.kos_i_net != zero or zak.kos_i_vat != zero or
            zak.kos_w_net != zero or zak.kos_w_vat != zero or
            zak.soz_i_net != zero or zak.soz_i_vat != zero or
            zak.soz_p_net != zero or zak.soz_p_vat != zero or
            zak.bez_i_net != zero or zak.bez_i_vat != zero or
            zak.bez_p_net != zero or zak.bez_p_vat != zero):
            pass # pragma: no cover
        else:
            if zak.netto != zero or zak.vat != zero:
                zak.jpk.blad('ZAK', zak.faktura, 'W tej fakturze VAT nie jest rozliczony')          
            return
        
        netto= (zak.sop_i_net + zak.sop_p_net +
                zak.soz_i_net + zak.soz_p_net +
                zak.kos_i_net + zak.kos_w_net +
                zak.bez_i_net + zak.bez_p_net)
    
        if SysPar.get_wartosc('ZAK-BEZ-BRUTTO', zak.jpk.fkdbs('ZAK-BEZ-BRUTTO')) == 'tak': # pragma: no cover
            # Na razie nie ma takiego przypadku
            netto= netto - zak.bez_i_vat - zak.bez_p_vat
    
        vat= (zak.sop_i_vat + zak.sop_p_vat +
              zak.soz_i_vat + zak.soz_p_vat +
              zak.kos_i_vat + zak.kos_w_vat +
              zak.bez_i_vat + zak.bez_p_vat)
    
        if netto != zak.netto:
            zak.jpk.blad('ZAK', zak.faktura, 'Netto z ekranu rozliczenia jest różne od netto faktury')            
    
        if vat != zak.vat:
            zak.jpk.blad('ZAK', zak.faktura, 'VAT z ekranu rozliczenia jest różny od VAT faktury')
    
        if netto + vat != zak.brutto:
            zak.jpk.blad('ZAK', zak.faktura, 'Brutto z ekranu rozliczenia jest różny od wartości faktury')


        if zak.k_44 != zero or zak.k_46 != zero:
            pass



class ZakupVATPozycjeZak(Pozycje):

    def przygotuj(self, zak):
        
        if (SysPar._bra() and zak.msc_roz >= utils.data_na_miesiac(zak.jpk.dataod)) or \
            zak.d_ksieg >= zak.jpk.dataod:
        
            if zak.nazwa_kon() is None or len(zak.nazwa_kon().strip()) == 0:
                zak.jpk.blad('ZAK', zak.faktura, 'Nieokreślona nazwa dostawcy')    
            if zak.adres_kon() is None or len(zak.adres_kon().strip()) == 0:
                zak.jpk.blad('ZAK', zak.faktura, 'Brak adresu dostawcy')
            if (zak.nr_id() is None or len(zak.nr_id().strip()) == 0) and not zak.dostawca.idtyp == 'IDENT':
                zak.jpk.blad('ZAK', zak.faktura, 'Brak NIP dostawcy')
            if zak.nr_id() and re.match(r'[A-Z][A-Z]', zak.nr_id()) and zak.dostawca.idtyp and not zak.dostawca.idtyp.strip() in ('NIPUE', 'IDENT'):            
                zak.jpk.blad('ZAK', zak.faktura, 'NIP kontrahenta wygląda na NIPUE ale nie jest tak oznaczony')
            if not zak.faktura:
                zak.jpk.blad('ZAK', '{}/{}'.format(zak.rodzaj, zak.lp), 'Brak numeru faktury')

        zak.nr_id= zak.nr_id()
        zak.nr_faktury= zak.faktura
        zak.data_wplywu= zak.d_otrzym
        zak.data_zakupu= zak.d_wyst
        zak.pod_rejestr= zak.rodzaj   
        zak.typ_dokumentu= None
        

    def sprawdzenie_nip_zakupow(self, zak):
        """
        Sprawdzenie czy dostawca (kontrahent w fakturze zakupu) jest 
        czynnym płatnikiem VAT.
        """

        # Nie ma podanego NIP?
        if not zak.nip:
            return

        # Kontrahent zagraniczny - nie sprawdzamy
        if zak.dostawca and zak.dostawca.idtyp == 'IDENT':
            return
        
        nip= zak.nip.strip()
        nip= nip.replace('-', '')
        
        # Brak nip nie ma co sprawdzać
        if not nip or len(nip) == 0:
            return
        
        # NIP europejski - nie sprawdzamy
        if not nip or re.match('[A-Z][A-Z].*', nip):
            return

        # Ustalenie aktualnego statusu NIP z bazy lub webserwisu
        status= '?'
        kon_vat= KonVat.objects.filter(nip= nip, aktualny='T')
        if kon_vat:
            kon_vat= kon_vat[0]
            old = int(SysPar.get_wartosc('KON-NIP-SPRAWDZ-WIELE', zak.jpk))
            if kon_vat.ostatnio.date() >= datetime.date.today() - datetime.timedelta(days= old):
                status= kon_vat.vat

        if status == '?':
            try:
                status= kon_nip_status(nip)
            except Exception as e:
                print('Błąd w sprawdzanie_platnika_vat {}'.format(e))
                status= '?'

        msg, level= None, 'warn'
                
        ZERO= decimal.Decimal(0)
        if zak.k_44 == ZERO and zak.k_46 == ZERO:
            # Jeżeli nie ma odliczenia to sprawdzamy czy NIP jest poprawny 
            if status in ('N', 'I'):
                msg, level= msg_statusu_nip(status)
        else:
            # Jeżeli jest odliczenie to musi być czynny
            if status not in ('C',):
                msg, level= msg_statusu_nip(status)
                
        if msg:
            msg= msg.format(nip)
            zak.jpk.blad('ZAK', zak.faktura, msg, level= level)

        return



class DeklaracjaVAT(ctrl.CtrlTabeli):
    """
    Deklaracja VAT.
    """
    
    def __init__(self, jpk):
        super(DeklaracjaVAT, self).__init__(jpk)
        self.tabela= 'deklaracja'
        
        self.elementy= [
            DeklaracjaVATPozycje(jpk),
        ]
        
    def sumuj(self, pozycje, dek):
        """
        Sumy kontrolne zawierają sumy podatku należnego i naliczonego.
        """
        super(DeklaracjaVAT, self).sumuj(pozycje, dek)
        
        # Pierwsza suma zawiera podatek należny
        if dek.grupa == 'C' and dek.rodzaj == '2':
            self.suma1 += dek.kwota
        # Druga suma zawiera podatek naliczony
        if dek.grupa == 'D' and dek.rodzaj == '2':
            self.suma2 += dek.kwota
                    
    def uwzglednij(self, pozycje, dek):
        """
        Wszystkie pozycje deklaracji są opcjonalne.
        """
        super(DeklaracjaVAT, self).uwzglednij(pozycje, dek)
        
        return pozycje.uwzglednij(dek)



class DeklaracjaVATPozycje(Pozycje):
    """
    Ten pozycje są wykorzystywane podczas generowania pliku XML.
    Dokładniej części deklaracyjnej.
    W tym momencie one są już wypełnione (zapisane do bazy).
    Procedura jest taka:
    
    1. Generujemy plik JPK_VAT (na podstawie rej. sprzedaży i zakupów)
    2. Tworzone są wtedy pozycje deklaracji, które są sumami z ewidencji
    3. Mamy teraz bazową/podstawową postać deklaracji.
    4. Edytujemy pozostałe pola deklaracji, pola edytowalne
    5. Po zapisaniu części edytowalnej musimy zmodyfikować XML
       (usunąć starą deklarację i wpisać na jej miejsce nową),
       tworząc nowy XML.
    """    
    def __init__(self, jpk):
        super(DeklaracjaVATPozycje, self).__init__(
            Deklaracja.objects.filter(jpk= jpk).order_by('numer')
        )


    def uwzglednij(self, dek):
        """
        Uwzględnienie pozycji deklaracji.
        """
        
        if not dek.element:
            dek.element= "P_{}".format(dek.numer)

        return True

