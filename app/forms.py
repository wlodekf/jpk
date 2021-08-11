# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import decimal

from django import forms
from app.models import Plik, Wyciag, Firma, Deklaracja
from sf.models import Sprawozdanie
from fk.models import MagDzial, SysKli


class PlikForm(forms.ModelForm):

    jpk_kr= forms.BooleanField(required= False)
    jpk_wb= forms.BooleanField(required= False)
    jpk_vat= forms.BooleanField(required= False)
    jpk_v7m= forms.BooleanField(required= False)
    jpk_fa= forms.BooleanField(required= False)
    jpk_mag= forms.BooleanField(required= False)    
    jpk_sf= forms.BooleanField(required= False)  
        
    rachunki= forms.MultipleChoiceField(required= False)
    magazyny= forms.MultipleChoiceField(required= False)
    
    wynik= forms.CharField(required= False)
    kapital= forms.BooleanField(required= False)
    przeplywy= forms.BooleanField(required= False)
    przeplywy_metoda= forms.CharField(required= False)
    poprzednie= forms.IntegerField(required= False)

    kopia= forms.BooleanField(required= False)
    korekta= forms.CharField(required= False)
                
    class Meta:
        model= Plik   
        fields= ('dataod', 'datado')

    def __init__(self, *args, **kwargs):
        super(PlikForm, self).__init__(*args, **kwargs)
        
        firma= args[1]

        self.fields['rachunki'].choices= [(x,x) for x in Wyciag.rachunki()]
        self.fields['magazyny'].choices= [(x,x) for x in MagDzial.magazyny()]
        self.fields['poprzednie'].choices= [(x.id, x.nazwa) for x in Sprawozdanie.poprzednie(firma.oznaczenie)]
            

class NazwaForm(forms.ModelForm):

    class Meta:
        model= Plik   
        fields= ('nazwa',)
        
        
class FirmaForm(forms.ModelForm):

    class Meta:
        model= Firma   
        exclude= ('db_ostatnia', 'db_rok', 'adres', 'ostatni_plik')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['oznaczenie'].help_text= 'Z systemu FK'
        self.fields['kod_urzedu'].help_text= 'Kod urzędu skarbowego'
        self.fields['nazwa'].help_text= 'Pełna nazwa firmy'
        self.fields['email'].help_text= 'Adres e-mail do kontaktów w sprawie JPK'
        self.fields['telefon'].help_text= 'Numer telefonu kontaktowego (opcjonalny)'
        self.fields['api_url'].help_text= 'Adres URL API importu dokumentów'
        self.fields['api_auth'].help_text= 'Klucz autoryzacyjny'
        self.fields['vat7'].help_text= 'Okres deklaracji VAT-7'
                
    def clean_oznaczenie(self):
        oznaczenie= self.cleaned_data['oznaczenie']
        
        if not self.instance:
            try:        
                SysKli.objects.get(kod= oznaczenie)
            except SysKli.DoesNotExist:
                raise forms.ValidationError("Nie ma bazy FK o podanym kodzie")
                    
        return oznaczenie
    

class KwotaCField(forms.DecimalField):
    
    def clean(self, value):
        if isinstance(value, str):
            value= value.replace(' ', '')

        if value == '':
            value= 0
            
        try:
            return decimal.Decimal(value)
        except:
            raise forms.ValidationError('Niepoprawna wartość "{}"'.format(value))
        


class DeklaracjaForm(forms.ModelForm):
    """
    Formularz do wprowadzania danych deklaracji, które nie pochodzę bezpośrednio z ewidencji
    są wprowadzane "ręcznie" w momencie tworzenia deklaracji.
    """

    p_39= KwotaCField(label="39.", required= False)
    
    p_49= KwotaCField(label="49.", required= False)
    p_50= KwotaCField(label="50.", required= False)
    p_52= KwotaCField(label="52.", required= False)
    p_54= KwotaCField(label="54.", required= False)
        
    p_55= forms.BooleanField(label="55.", required= False)
    p_56= forms.BooleanField(label="56.", required= False)
    p_57= forms.BooleanField(label="57.", required= False)
    p_58= forms.BooleanField(label="58.", required= False)
    
    p_59= forms.BooleanField(label="59.", required= False)
    p_60= KwotaCField(label="60.", required= False)
    p_61= forms.CharField(label="61.", required= False)
        
    p_63= forms.BooleanField(label="63.", required= False)
    p_64= forms.BooleanField(label="64.", required= False)
    p_65= forms.BooleanField(label="65.", required= False)
    p_66= forms.BooleanField(label="66.", required= False)
    p_67= forms.BooleanField(label="67.", required= False)
    
    p_68= KwotaCField(label="68.", required= False)
    p_69= KwotaCField(label="69.", required= False)

    p_70= forms.CharField(label="70.", required= False)
                
    class Meta:
        model= Plik
        fields= (
            'p_39',
            'p_49', 'p_50', 
            'p_52', 'p_54',
            'p_55', 'p_56', 'p_57', 'p_58', 
            'p_59', 'p_60', 'p_61', 
            'p_63', 'p_64', 'p_65', 'p_66', 'p_67',
            'p_68', 'p_69', 'p_70'
        )

    def clean(self):
        cleaned_data = super().clean()

        p_38= self.dek['p_38'].kwota or 0
        p_48= self.dek['p_48'].kwota or 0
        p_53= self.dek['p_53'].kwota or 0
                
        p_49= cleaned_data.get('p_49', 0) or 0
        p_50= cleaned_data.get('p_50', 0) or 0
        p_54= cleaned_data.get('p_54', 0) or 0
        p_60= cleaned_data.get('p_60', 0) or 0
                
        if p_49 and p_49 > p_38 - p_48:
            self.add_error('p_49', 'Kwota nie może przekraczać {}'.format(p_38-p_48))

        if p_50 and p_50 > p_38 - p_48 - p_49:
            self.add_error('p_50', 'Kwota nie może przekraczać {}'.format(p_38-p_48-p_49))            
            
        if p_54 > p_53:
            self.add_error('p_54', 'Kwota nie może przekraczać {}'.format(p_53))
            
        if p_60 > p_53 - p_54:
            self.add_error('p_60', 'Kwota nie może przekraczać {}'.format(p_53-p_54)) 
                         
        return cleaned_data
            
    def __init__(self, *args, **kwargs):
        super(DeklaracjaForm, self).__init__(*args, **kwargs)

        self.dek= args[1]
        self.jpk= kwargs.get('instance')  

        self.fields['p_39'].help_text= 'Wysokość nadwyżki podatku naliczonego nad należnym z poprzedniej deklaracji'        
        self.fields['p_49'].help_text= 'Kwota wydana na zakup kas rejestrujących, do odliczenia w danym okresie rozliczeniowym pomniejszająca wysokość podatku należnego'
        self.fields['p_50'].help_text= 'Wysokość podatku objęta zaniechaniem poboru'
        self.fields['p_52'].help_text= 'Kwota wydana na zakup kas rejestrujących, do odliczenia w danym okresie rozliczeniowym przysługująca do zwrotu w danym okresie rozliczeniowym lub powiększająca wysokość podatku naliczonego do przeniesienia na następny okres rozliczeniowy'
        self.fields['p_54'].help_text= 'Wysokość nadwyżki podatku naliczonego nad należnym do zwrotu na rachunek wskazany przez podatnika'
        
        self.fields['p_55'].help_text= 'Zwrot na rachunek VAT, o którym mowa w art. 87 ust. 6a ustawy'
        self.fields['p_56'].help_text= 'Zwrot w terminie, o którym mowa w art. 87 ust. 6 ustawy'
        self.fields['p_57'].help_text= 'Zwrot w terminie, o którym mowa w art. 87 ust. 2 ustawy'
        self.fields['p_58'].help_text= 'Zwrot w terminie, o którym mowa w art. 87 ust. 5a zdanie pierwsze ustawy'

        self.fields['p_59'].help_text= 'Zaliczenie zwrotu podatku na poczet przyszłych zobowiązań podatkowych'
        self.fields['p_60'].help_text= 'Wysokość zwrotu do zaliczenia na poczet przyszłych zobowiązań podatkowych'
        self.fields['p_61'].help_text= 'Rodzaj przyszłego zobowiązania podatkowego'        
        
        self.fields['p_63'].help_text= 'Podatnik wykonywał w okresie rozliczeniowym czynności, o których mowa w<br/>art. 119 ustawy'
        self.fields['p_64'].help_text= 'art. 120 ust. 4 lub 5 ustawy'
        self.fields['p_65'].help_text= 'art. 122 ustawy'
        self.fields['p_66'].help_text= 'art. 136 ustawy'
        
        self.fields['p_67'].help_text= 'Podatnik korzysta z obniżenia zobowiązania podatkowego,<br/>o którym mowa w art. 108d ustawy'
        self.fields['p_68'].help_text= 'Wysokość korekty podstawy opodatkowania, o której mowa w art. 89a ust. 1 ustawy'
        self.fields['p_69'].help_text= 'Wysokość korekty podatku należnego, o której mowa w art. 89a ust. 1 ustawy'
        self.fields['p_70'].help_text= 'Uzasadnienie przyczyn złożenia korekty'
