from __future__ import unicode_literals

from django import forms

PODPISY= (('stopka', 'Stopka'), ('pieczatka', 'Pieczątka'))
GRUPOWANIE= (('zaklady', 'Zakłady'), ('tematy', 'Tematy'))

class FakturyForm(forms.Form):

    od_daty= forms.DateField(required= True, label= 'Początek okresu', 
                            help_text= 'Data w formacie RRRR-MM-DD')
    
    do_daty= forms.DateField(required= True, label= 'Koniec okresu',
                            help_text= 'Data w formacie RRRR-MM-DD')                             
    
    zaklady= forms.CharField(required= False, label= 'Zakłady', 
                            help_text= 'Lista wzorców (oddzielonych spacjami) na zakłady prowadzące tematy')
    
    tematy= forms.CharField(required= False, label= 'Tematy',
                            help_text= 'Lista wzorców na tematy do uwzględnienia w fakturach')
    
    pkwiu= forms.CharField(required= False, label= 'PKWiU',
                           help_text= 'Lista wzorców na symbole PKWiU tematów do uwzględnienia')

    podpis= forms.ChoiceField(widget= forms.RadioSelect, choices= PODPISY)
    grupowanie= forms.ChoiceField(widget= forms.RadioSelect, choices= GRUPOWANIE)
    
    def clean(self):
        cleaned_data= super(FakturyForm, self).clean()
        od_daty= cleaned_data.get("od_daty")
        do_daty= cleaned_data.get("do_daty")

        if od_daty and do_daty and do_daty < od_daty:
            raise forms.ValidationError(
                "Koniec okresu nie może być wcześniejszy niż początek"                                        
            )
