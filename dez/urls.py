# -*- coding: utf-8 -*- 

from __future__ import unicode_literals

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import url

from dez import views

urlpatterns = staticfiles_urlpatterns()
urlpatterns += [

    url(r'^dez/powiadom/$', views.powiadom, name= 'dez-powiadom'),
]
