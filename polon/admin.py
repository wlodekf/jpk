from django.contrib import admin

from .models import Tworzenie

from django.conf.locale.pl import formats as pl_formats

pl_formats.DATE_FORMAT = "Y-m-d"
pl_formats.DATETIME_FORMAT = "Y-m-d H:i"


class TworzenieAdmin(admin.ModelAdmin):
    
    list_display= ('zlecono', 'uzytkownik', 'od_daty', 'do_daty', 'zaklady', 'tematy', 'grupowanie', 'ile_plikow', 'ile_faktur', 'pobrano')
    
    fields= ('zlecono', 'uzytkownik')

    list_per_page= 20
    ordering= ['-zlecono']         
    search_fields= ['zlecono', 'uzytkownik', 'zaklady', 'tematy']
    
    def __init__(self, *args, **kwargs):
        super(TworzenieAdmin, self).__init__(*args, **kwargs)
#         self.list_display_links= None
            
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj= None):
        return True
    def has_delete_permission(self, request, obj= None):
        return False
    
    def save_model(self, request, obj, form, change):
        pass    
    
admin.site.register(Tworzenie, TworzenieAdmin) 
