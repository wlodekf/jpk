# -*- coding: utf-8 -*- 

from __future__ import unicode_literals

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import url

from . import views

urlpatterns = staticfiles_urlpatterns()
urlpatterns += [

    url(r'(?P<firma>[a-z]{3,8})/importuj/$', views.zakupy_importuj, name= 'api-zakupy-importuj'),
    url(r'(?P<firma>[a-z]{3,8})/importy$', views.zakupy_importy, name= 'api-zakupy-importy'),
    url(r'(?P<firma>[a-z]{3,8})/importy/ajax/$', views.zakupy_importy_ajax, name= 'api-zakupy-importy-ajax'),

    url(r'(?P<imp_id>\d+)/rozwin/ajax/$', views.zakupy_rozwin_ajax, name= 'api-zakupy-rozwin-ajax'),
    url(r'(?P<imp_id>\d+)/xlsx/$', views.zakupy_xlsx, name= 'api-zakupy-xlsx'), 
]
