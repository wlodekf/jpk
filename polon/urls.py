# -*- coding: utf-8 -*- 

from __future__ import unicode_literals

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import url

from . import views

urlpatterns = staticfiles_urlpatterns()
urlpatterns += [
    url(r'^polon/$', views.polon, name= 'polon'),                
    url(r'^polon/faktury/$', views.faktury, name= 'polon-faktury'),
    url(r'^polon/czekaj/(?P<job_id>\d+)/(?P<hh>[0-9a-f]+)/$', views.czekaj, name= 'polon-czekaj'),
    url(r'^polon/link/(?P<job_id>\d+)/(?P<hh>[0-9a-f]+)/$', views.link, name= 'polon-link'),    
    url(r'^polon/link/(?P<job_id>\d+)/zip/(?P<hh>[0-9a-f]+)/$', views.link_zip, name= 'polon-link-zip'),
    url(r'^polon/link/(?P<job_id>\d+)/xls/(?P<hh>[0-9a-f]+)/$', views.link_xls, name= 'polon-link-xls'),    
    url(r'^polon/link/(?P<job_id>\d+)/usun/(?P<hh>[0-9a-f]+)/$', views.link_usun, name= 'polon-link-usun'),
    url(r'^polon/status/(?P<job_id>\d+)/$', views.status, name= 'polon-status'),
     
    url(r'^polon/podpis/(?P<tmpd>[^/]+)/(?P<paczka>[^/]+)/(?P<baza>[^/]+)/(?P<user>[^/]+)/$', views.pdf_podpis, name= 'pdf-podpis'),
]
