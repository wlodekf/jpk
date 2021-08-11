from __future__ import unicode_literals

from django import forms
from bra.models import ImportSprzedazy, ImportZakupow
from fk.models import Spo

class SprzedazPlikiForm(forms.ModelForm):

    class Meta:
        model= ImportSprzedazy   
        fields= ('faktury', 'wiersze')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
#         self.fields['rejestr'].help_text= 'Dwuznakowy kod podrejestru sprzedaży'


class SprzedazRejestrForm(forms.ModelForm):

    class Meta:
        model= ImportSprzedazy   
        fields= ('do_rejestru', 'rejestr', 'konto_kon', 'konto_spr')
        
    def __init__(self, firma, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        choices= [(p.spokod[1:].strip(), '{} - {}'.format(p.spokod[1:].strip(), p.pnazwa.strip())) for p in Spo.slo_pozycje(firma, 'RDOK') if p.spokod.startswith('S')]
                
        self.fields['rejestr']= forms.ChoiceField(choices= choices)        
        self.fields['rejestr'].help_text= 'Dwuznakowy kod podrejestru sprzedaży'

        self.fields['konto_kon'].label= 'Konto kontrahenta'        
        self.fields['konto_spr'].label= 'Konto sprzedaży'
