# -*- coding: utf-8 -*-
"""jpk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from __future__ import unicode_literals

from django.conf.urls import url, include
from django.contrib import admin
from django import http

urlpatterns = [
    url(r'^favicon.ico$', lambda r: http.HttpResponseNotFound(), name= 'favicon' ),
    
    url(r'^admin/', admin.site.urls),
        
    url(r'', include('polon.urls')),

    url(r'', include('app.urls')),
    url(r'', include('dez.urls')),
    url(r'', include('vat.urls')),
    url(r'', include('bra.urls')),
    url(r'', include('sf.urls')),
]
