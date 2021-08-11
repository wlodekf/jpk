# -*- coding: utf-8 -*- 

from __future__ import unicode_literals

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import url, include

from bra import views

urlpatterns = staticfiles_urlpatterns()
urlpatterns += [

    url(r'^(?P<firma>[a-z]{3,8})/sprzedaz/importuj/$', views.bra_sprzedaz_pliki, name= 'bra-sprzedaz-importuj'),
    url(r'^(?P<firma>[a-z]{3,8})/sprzedaz/importy$', views.bra_sprzedaz_importy, name= 'bra-sprzedaz-importy'),    
    url(r'^bra/sprzedaz/akceptuj/(?P<imp_id>\d+)/$', views.bra_sprzedaz_akceptuj, name= 'bra-sprzedaz-akceptuj'),
    url(r'^bra/sprzedaz/rejestr/(?P<imp_id>\d+)/$', views.bra_sprzedaz_do_rejestru, name= 'bra-sprzedaz-do-rejestru'),
    url(r'^bra/sprzedaz/koniec/(?P<imp_id>\d+)/$', views.bra_sprzedaz_koniec, name= 'bra-sprzedaz-koniec'),
    url(r'^bra/sprzedaz/(?P<imp_id>\d+)/xlsx/$', views.bra_sprzedaz_xlsx, name= 'bra-sprzedaz-xlsx'), 
                
    url(r'^bra/faktury/$', views.bra_faktury, name= 'bra-faktury'),

    url(r'^bra/ajax/faktury/$', views.bra_ajax_faktury, name= 'bra-ajax-faktury'),
    url(r'^bra/ajax/(?P<firma>[a-z]{3,8})/konto/(?P<konto>.*?)/$', views.bra_ajax_konto, name= 'bra-ajax-konto'),
    url(r'^bra/ajax/(?P<firma>[a-z]{3,8})/importy/$', views.bra_ajax_importy, name= 'bra-ajax-importy'),
    url(r'^bra/ajax/(?P<imp_id>\d+)/rozwin/$', views.bra_ajax_rozwin, name= 'bra-ajax-rozwin'),

    url(r'^api/sprzedaz/', include('bra.api.sprzedaz.urls')),
    url(r'^api/zakupy/', include('bra.api.zakupy.urls')),
]
