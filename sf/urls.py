# -*- coding: utf-8 -*- 

from __future__ import unicode_literals

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import url

from sf.api import raport, podatek, dodatkowe, wprowadz, views

urlpatterns = staticfiles_urlpatterns()
urlpatterns += [

    # patch - initialize reports
    url(r'^sf/init/(?P<raport_id>\d+)$', views.init_pozycji, name= 'sf-run'),

    # get - get xslt stylesheet
    url(r'^sf.xsl/$', views.sf_xsl, name='sf-xsl'),
    url(r'^sf.xsl/(?P<czesc>.*)/$', views.sf_xsl, name='sf-xsl'),

    url(r'^sf2.xsl/$', views.sf_xsl, {'wariant': '2'}, name='sf2-xsl'),
    url(r'^sf2.xsl/(?P<czesc>.*)/$', views.sf_xsl, {'wariant': '2'}, name='sf2-xsl'),
    
    # get - display report visualisation
    url(r'^jpk/(?P<jpk_id>\d+)/sf/xml/$', views.jpk_sf_view, name='jpk-sf-view'), # wizualizacja sprawozdanie
    url(r'^jpk/(?P<jpk_id>\d+)/sf/xml/(?P<czesc>[^/]*)/$', views.jpk_sf_view, name='jpk-sf-xml'), # wizualizacja części sprawozdania

    # get - download report additional info attachment    
    # url(r'^jpk/(?P<jpk_id>\d+)/sf/xml/dodatkowe/plik/(?P<id>\d+)/$', dodatkowe.dodatkowe_plik, name='xml-dodatkowe-plik'),  
    # url(r'^jpk/(?P<jpk_id>\d+)/sf/xml/plik/(?P<id>\d+)/$', dodatkowe.dodatkowe_plik, name='xml-plik'),

    # post - generate report xml representation
    url(r'^jpk/(?P<jpk_id>\d+)/sf/generuj/$', views.jpk_sf_generuj, name='jpk-sf-generuj'),
    # delete - usunięcie pliku xml
    url(r'^jpk/(?P<jpk_id>\d+)/sf/edit/$', views.jpk_sf_edit, name='jpk-sf-edit'),

    # get - wyświetlenie listy pozycji raportu na potrzeby pliku nazw
    url(r'^sf/pozycje/$', views.sf_pozycje, name='sf-pozycje'),
    url(r'^sf/test/', views.test, name="sf-test"),
]

urlpatterns += [

    # get - pobranie wprowadzenia
    # patch - modyfikacja wprowadzenia
    url(r'^sf/(?P<jpk_id>\d+)/wprowadz/$', wprowadz.wprowadz, name='sf-wprowadz'),

    # post - utworzenie nowego wyjaśnienia
    # patch - modyfikacja wyjaśnienia
    # delete - usunięcie dodatkowego wyjaśnienia
    url(r'^sf/(?P<jpk_id>\d+)/wprowadz/p8/(?:(?P<p8_id>\d+)/)?$', wprowadz.p8, name='wprowadz-p8'),

    # get - pobranie pozycji raportu
    # patch - modyfikacja pozycji raportu
    url(r'^sf/(?P<jpk_id>\d+)/(?P<raport>aktywa|pasywa|rzis|kapital|przeplywy)/$', raport.pozycje, name= 'sf-raport'), # pozycje raportu
                
    # get - pobranie pozycji raportu
    # patch - aktulizacja pozycji raportu
    url(r'^sf/(?P<jpk_id>\d+)/podatek/$', podatek.podatek, name= 'sf-podatek'),

    # get - pobranie listy wszystkich załączników do sprawozdania
    # post - utworzenia nowego załącznika
    # patch - modyfikacja opisu danego załącznika
    # delete - usunięcie danego załącznika
    url(r'^sf/(?P<jpk_id>\d+)/dodatkowe/(?:(?P<id>\d+)/)?$', dodatkowe.dodatkowe, name= 'sf-dodatkowe'),
    # get - pobranie danego załącznika
     
    url(r'^sf/(?P<jpk_id>\d+)/dodatkowe/(?P<id>\d+)/plik/$', dodatkowe.dodatkowe_plik, name='dodatkowe-plik'),  
]

# POST, PATCH, PUT powinien zwracać nowe/zaktualizowane dane
# POST powinien zwracać status code 201 i URI nowego obiektu w nagłówku 'location'

