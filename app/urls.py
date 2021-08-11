# -*- coding: utf-8 -*- 

from __future__ import unicode_literals

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import url
from django.contrib.auth.views import login, logout, password_change

from app import views, wyciagi, ajax

urlpatterns = staticfiles_urlpatterns()
urlpatterns += [

    url(r'^accounts/login/$',  login, name='login'),
    url(r'^accounts/logout/$', logout, {'next_page': '/'}, name='logout'),
    url(r'^accounts/password_change/$', password_change, {'post_change_redirect': '/'}, name='password_change'),
        
    url(r'^firmy/$', views.firmy, name='firmy'),
    url(r'^firmy/nowa/$', views.firma_edit, name='firma-nowa'),
            
    url(r'^$', views.home, name='home'),
    url(r'^(?P<firma>[a-z]{3,8})/$', views.home, name='home'),
    url(r'^ajax/(?P<firma>[a-z]{3,8})/dane/$', views.firma_dane, name='firma-dane'),
    url(r'^firma/(?P<firma>[a-z]{3,8})/$', views.firma_edit, name='firma-edit'),
        
    url(r'^(?P<firma>[a-z]{3,8})/nowe/$', views.jpk_nowe, name='jpk-nowe'),
    
    url(r'^jpk/(?P<jpk_id>\d+)/rozwin/$', views.jpk_rozwin, name='jpk-rozwin'),
    url(r'^jpk/(?P<jpk_id>\d+)/zwin/$', views.jpk_zwin, name='jpk-zwin'),
            
    url(r'^jpk/(?P<jpk_id>\d+)/usun/$', views.jpk_usun, name='jpk-usun'),
    url(r'^jpk/(?P<jpk_id>\d+)/regeneruj/$', views.jpk_regeneruj, name='jpk-regeneruj'),
    url(r'^jpk/(?P<jpk_id>\d+)/status/(?P<delay>\d+)/$', views.jpk_status, name='jpk-status'),
    url(r'^jpk/(?P<jpk_id>\d+)/refresh/$', views.jpk_refresh, name='jpk-refresh'),    
    url(r'^jpk/(?P<jpk_id>\d+)/upo/$', views.jpk_upo, name='jpk-upo'),  
    url(r'^jpk/(?P<jpk_id>\d+)/upo/wydruk/$', views.jpk_upo, {'wydruk': True}, name='jpk-upo-wydruk'),  
    url(r'^jpk/(?P<jpk_id>\d+)/xlsx/$', views.jpk_xlsx, name='jpk-xlsx'),
    url(r'^jpk/(?P<jpk_id>\d+)/download/$', views.jpk_download, name='jpk-download'),
    url(r'^jpk/(?P<jpk_id>\d+)/wyslij/$', views.jpk_wyslij, name='jpk-wyslij'),    
    url(r'^jpk/(?P<jpk_id>\d+)/validate/$', views.jpk_validate, name='jpk-validate'),
    url(r'^jpk/(?P<jpk_id>\d+)/bledy/$', views.jpk_bledy, name='jpk-bledy'),
    
    url(r'^jpk/nazwa/$', views.jpk_nazwa, name='jpk-nazwa'),
    url(r'^jpk/(?P<jpk_id>\d+)/initupload/$', views.jpk_initupload, name='jpk-initupload'),    
    url(r'^jpk/initupload/$', views.jpk_initupload, name='jpk-initupload-dev'),
    url(r'^jpk/upload/$', views.jpk_upload, name='jpk-upload'),
    url(r'^jpk/uploadsf/$', views.sf_upload, name='sf-upload'),
        
    url(r'^jpk/(?P<jpk_id>\d+)/arkusz/(?P<arkusz>.*)/$', views.jpk_arkusz, name='jpk-arkusz'),
    url(r'^jpk/(?P<jpk_ids>(\d+,?)+)/task/$', views.jpk_task, name='jpk-task'),
    
    url(r'^wyciag/(?P<bank>.*)/upload/$', wyciagi.wyciag_upload, name= 'wyciag-upload'),
    url(r'^wyciag/(?P<bank>.*)/import/$', wyciagi.wyciag_import, name= 'wyciag-import'),
              
    url(r'^ajax/(?P<firma>[a-z]{3,8})/jpk/lista/$', ajax.jpk_lista, name= 'ajax-jpk-lista'),
    url(r'^ajax/firmy/$', ajax.lista_firm, name= 'lista_firm'),
    url(r'^jpk/statusy/$', views.jpk_statusy, name='jpk-statusy'),
    
    url(r'^jpk/(?P<jpk_id>\d+)/pdf/$', views.jpk_vatpdf, name='jpk-vatpdf'),

    url(r'^jpk/deklaracja/(?P<jpk_id>\d+)/form/$', views.deklaracja_form, name='deklaracja-form'),
    url(r'^jpk/deklaracja/(?P<jpk_id>\d+)/$', views.deklaracja_edit, name='deklaracja-edit'),
        
    url(r'^jpk/(?P<jpk_id>\d+)/wizualizacja(?:/(?P<czesc>.*))?/$', views.jpk_vat_wizualizacja, name='jpk-vat-wizualizacja'),
    url(r'^xsl/styl-2020-05.xsl/(?P<jpk_id>\d+)(?:/(?P<czesc>.*))?/$', views.jpk_vat_xsl, name='jpk-vat-xsl'),
]
