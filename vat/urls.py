# -*- coding: utf-8 -*- 

from __future__ import unicode_literals

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import url

from . import views

urlpatterns = staticfiles_urlpatterns()
urlpatterns += [
    url(r'^vat/czynny/(?P<nip>\d+)/$', views.czynny, name= 'czynny'),
    url(r'^krs/(?P<nip>\d+)/$', views.krs, name= 'krs')                  
]
