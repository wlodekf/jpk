# -*- coding: utf-8 -*- 

from __future__ import unicode_literals

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import url

from . import views

urlpatterns = staticfiles_urlpatterns()
urlpatterns += [
    url(r'^(?P<firma>[a-z]{3,8})/importuj/$', views.sprzedaz_importuj, name= 'api-sprzedaz-importuj'),
    url(r'^(?P<firma>[a-z]{3,8})/importy/$', views.sprzedaz_importy, name= 'api-sprzedaz-importy'),
    url(r'^(?P<firma>[a-z]{3,8})/importy/ajax/$', views.sprzedaz_importy_ajax, name= 'api-sprzedaz-importy-ajax'),
    
    url(r'^(?P<imp_id>\d+)/rozwin/ajax/$', views.sprzedaz_rozwin_ajax, name= 'api-sprzedaz-rozwin-ajax'),
    url(r'^(?P<imp_id>\d+)/xlsx/$', views.sprzedaz_xlsx, name= 'api-sprzedaz-xlsx'), 
]
