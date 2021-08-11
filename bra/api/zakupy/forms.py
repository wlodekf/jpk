from __future__ import unicode_literals

from django import forms
from bra.models import ImportZakupow


class ApiZakupyForm(forms.ModelForm):
    
    class Meta:
        model= ImportZakupow
        fields= ('od_daty', 'do_daty')

    def __init__(self, firma, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['od_daty'].label= 'Od daty'        
        self.fields['do_daty'].label= 'Do daty'
        
        self.fields['od_daty'].help_text= 'Początek okresu w formacie rrrr-mm-dd'
        self.fields['do_daty'].help_text= 'Koniec okresu w formacie rrrr-mm-dd'        

