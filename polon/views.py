# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import json
import tempfile
import subprocess
import os
import zipfile
from io import BytesIO
import shutil
import hashlib

from celery import shared_task

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from .forms import FakturyForm
from app.models import UserProfile
from .models import Tworzenie

from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
    
import logging
from django.contrib.auth.decorators import login_required
logger= logging.getLogger(__name__)

from . import xls

polon_tempd= lambda job: '/tmp/pdf_{}'.format(job.tmp_dir.strip())
polon_zip_name= lambda job: 'faktury{}.zip'.format(job.id)
polon_zip_path= lambda job: os.path.join(polon_tempd(job), polon_zip_name(job))
polon_xls_name= lambda job: 'faktury{}.xlsx'.format(job.id)
polon_xls_path= lambda job: os.path.join(polon_tempd(job), polon_xls_name(job))
polon_hash= lambda job: hashlib.md5(str(job.id).encode()).hexdigest()

polon_czekaj= lambda job: HttpResponseRedirect(reverse('polon-czekaj', args= [job.id, polon_hash(job)]))
polon_link= lambda job: HttpResponseRedirect(reverse('polon-link', args=[job.id, polon_hash(job)]))
polon_home= lambda request: render_to_response('polon/polon.html', {}, context_instance= RequestContext(request)) 

DBS='gig' if settings.LOCAL_DEV else 'fk17'

@shared_task 
def polon_faktury_task(job, tempd):
    
    if settings.LOCAL_DEV:
        # Zmiana uprawnień do katalogu, właścicielem jest user JPK 
        # zapisywać będzie krezusfk
        # Nie potrzebne w wersji produkcyjnej
        os.chmod(tempd, 0o777)    
        
        # Wykonanie skryptu generującego PDF'y
        subprocess.run(['ssh', 'krezusfk@localhost', '/home/krezusfk/etc/fak_pdf', str(job.id)])
    else:
        subprocess.run(['/tools/krezusfk/etc/fak_pdf', str(job.id)])        

    # Utworzenie raportu kontrolnego w postaci XLS    
    xls.raport_kontrolny(job, polon_xls_path(job))
    # Spakowanie PDFow do katalogu tymczasowego
    zip_pdfs(job)
    
    
def reset_home(request, profil):
    response= polon_home(request)
    profil.job_id= None
    profil.save()
    return response


def del_all(request):
    profil= UserProfile.get(request)    
    if not profil.job_id: return

    try:
        job= Tworzenie.objects.get(pk= profil.job_id)
    except Tworzenie.DoesNotExist:
        return

    usun_katalog(job)

     
@login_required
def polon(request):
    profil= UserProfile.get(request)
    
    if profil.job_id:
        try:
            job= Tworzenie.objects.get(pk= profil.job_id)
        except Tworzenie.DoesNotExist:
            return reset_home(request, profil)
                    
        tempd= polon_tempd(job)
        if not os.path.exists(tempd):
            return reset_home(request, profil)
        
        if os.path.exists(polon_zip_path(job)) and job.rozmiar_zip>0:
            return polon_link(job)
        else:            
            return polon_czekaj(job)
    else:
        return polon_home(request)


@login_required    
def faktury(request): 
    """
    Obsługa generowania faktury sprzedaży w formacie PDF.
    """
    
    if request.method == 'POST':
        
        form= FakturyForm(request.POST)
        if not form.is_valid():
            logger.warning(form)
        else:
            tempd= tempfile.mkdtemp(prefix= 'pdf_')
            
            del_all(request)
            
            job= Tworzenie.objects.create(
                uzytkownik= request.user.username, 
                zlecono= datetime.datetime.now(),
                
                od_daty= form.cleaned_data['od_daty'],
                do_daty= form.cleaned_data['do_daty'],
                zaklady= form.cleaned_data['zaklady'],
                tematy= form.cleaned_data['tematy'],
                pkwiu= form.cleaned_data['pkwiu'],
                podpis= form.cleaned_data['podpis'],
                grupowanie= form.cleaned_data['grupowanie'],
                
                tmp_dir= tempd.split('/pdf_')[1],
                stan= 'Przygotowanie do generowania faktur PDF...'
            )
            
            polon_faktury_task.apply_async((job, tempd), countdown= 0)
    
            response= polon_czekaj(job)
            
            profil= UserProfile.get(request)
            profil.job_id= job.id
            profil.save()
            
            return response
    else:
        form= FakturyForm(initial= settings.PDF_INITIAL)
            
    return render_to_response('polon/faktury.html', 
                              { 
                                'form': form
                              }, 
                              context_instance= RequestContext(request))


@login_required    
def czekaj(request, job_id, hh):
    
    job= Tworzenie.objects.get(pk= int(job_id))
    # Sprawdzenie poprawności URL
    if polon_hash(job) != hh: return polon_home(request) 
    
    if job.stan.startswith('Zakończono'):
        return polon_link(job)

    try:    
        prog= (100*int(job.ktora)) // int(job.ile_faktur)
    except:
        prog= 0
        
    return render_to_response('polon/czekaj.html', 
                              { 
                                'job': job, 
                                'prog': prog,
                                'hh': polon_hash(job)                                
                              }, 
                              context_instance= RequestContext(request))


def zip_pdfs(job):
    """
    Spakowanie plików PDF z danego katalogu tymczasowego i zapisanie ich 
    w archiwum zip w tym katalogu.
    """
    
    tempd= polon_tempd(job)
    zip_subdir= 'faktury{}'.format(job.id)

    s= BytesIO()
    zf= zipfile.ZipFile(s, "w")

    filenames= [file for file in os.listdir(tempd) if file.endswith('.pdf')]
    for fname in filenames:
        zip_path= os.path.join(zip_subdir+('/'+(fname.split('-')[1] if '-' in fname else '')), fname)
        pdf_path= os.path.join(tempd, fname)
        
        print(pdf_path, zip_path)
        zf.write(pdf_path, zip_path)

    zf.close()
    
    print(job.ile_plikow, job.ile_faktur, job.zakonczono)
    
    job.rozmiar_zip= len(s.getvalue())
    job.stan= 'ZIP utworzony'
    job.save(update_fields=['rozmiar_zip', 'stan'])
    
    with open(polon_zip_path(job), 'wb') as f:
        f.write(s.getvalue())
        

def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)


@login_required                
def link(request, job_id, hh):
    """
    Udostępnienie linka do pobrania pliku ZIP.
    """
    
    job= Tworzenie.objects.get(pk= int(job_id))
    # Sprawdzenie poprawności URL
    if polon_hash(job) != hh: return polon_home(request) 
    
    return render_to_response('polon/link.html', 
                              {
                                'job': job,
                                'size': sizeof_fmt(job.rozmiar_zip),
                                'hh': polon_hash(job)
                              }, 
                              context_instance= RequestContext(request))

    
@login_required
def status(request, job_id):
    """
    Ustalenie w jakim stanie jest tworzenie plików z fakturami.
    """
    
    job= Tworzenie.objects.get(pk= int(job_id))
    try:    
        prog= (100*int(job.ktora)) // int(job.ile_faktur)
    except:
        prog= 0
            
    print('prog', prog)
    return HttpResponse(json.dumps({
                            'info': job.stan,
                            'prog': prog,
                            'pozycja': '{}/{}'.format(job.ktora, job.ile_faktur),
                        }), 
                        content_type='application/json')
            

@login_required            
def link_zip(request, job_id, hh):
    
    job= Tworzenie.objects.get(pk= int(job_id))  
    # Sprawdzenie poprawności URL
    if polon_hash(job) != hh: return polon_home(request)     
      
    zip_file= open(polon_zip_path(job), 'rb')
    
    job.pobrano= datetime.datetime.now()
    job.save(update_fields= ['pobrano'])
    
    resp = HttpResponse(zip_file.read(), content_type = "application/x-zip-compressed")
    resp['Content-Disposition']= 'attachment; filename=%s' % polon_zip_name(job)

    return resp


@login_required
def link_xls(request, job_id, hh):
    """
    Wyświetlenie arkusza kontrolnego części pliku JPK.
    """

    job= Tworzenie.objects.get(pk= int(job_id))  
    # Sprawdzenie poprawności URL
    if polon_hash(job) != hh: return polon_home(request)
    
    xls_file= open(polon_xls_path(job), 'rb')
        
    response= HttpResponse(xls_file.read(), content_type= 'application/vnd.ms-excel')
    response['Content-Disposition']= 'attachment; filename="faktury{}.xlsx"'.format(job.id)

    return response


def usun_katalog(job):
    """
    Usunięcie katalogu z plikami i odnotowanie tego faktu.
    """
    job.usunieto= datetime.datetime.now()
    job.save(update_fields= ['usunieto'])
    
    try:
        shutil.rmtree(polon_tempd(job))
    except OSError:
        pass
    
    
@login_required
def link_usun(request, job_id, hh):
    """
    Posprzątanie po generacji faktury. 
    Usuwany jest katalog tymczasowy i cookie.
    """
    job= Tworzenie.objects.get(pk= int(job_id))
    # Sprawdzenie poprawności URL
    if polon_hash(job) != hh: return polon_home(request)
    
    usun_katalog(job)
    
    return reset_home(request, UserProfile.get(request))


def pdf_podpis(request, tmpd, paczka, baza, user):
    """
    Opieczętowanie pliku podanego wydziału znajdującego się w 
    podanym katalogu tymczasowym.
    """
    
    packet= BytesIO()
    
    # Utworzenie nowego PDF
    can= canvas.Canvas(packet, pagesize= A4)
    can.setFillColorRGB(0.6, 0.6, 0.9)
    
    # Ustawienie miejsca pisania i obrotu

    if True:
        can.translate(480,680)
        can.rotate(20)
    else:
        can.translate(385,785)
        can.rotate(0)
    
    can.setFontSize(6)
    can.drawString(0, 32, "System: KREZUS.2001-FK")
    can.drawString(0, 24, "Baza: "+baza)
    can.drawString(0, 18, "Operator: "+user)
    can.drawString(0, 12, "Wydruk: "+datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
    can.setFont('Helvetica-Bold', 6)        
    can.drawString(0,  6, "Kopia: P O L O N") 
                    
    can.showPage()
    can.save()
    
    # move to the beginning of the StringIO buffer
    packet.seek(0)
    pieczatka= PdfFileReader(packet)
    
    file_pdf= '/tmp/pdf_{}/{}.pdf'.format(tmpd, paczka)
    
    # read your existing PDF
    oryginal= PdfFileReader(file_pdf)
    dup= PdfFileWriter()
    
    # add the "watermark" (which is the new pdf) on the existing page
    for i in range (0, oryginal.getNumPages() ):
        page= oryginal.getPage(i)
        page.mergePage(pieczatka.getPage(0))
        page.compressContentStreams()
        dup.addPage(page)
    
    # finally, write "dup" to a real file
    output= BytesIO()
    dup.write(output)
    
    with open('/tmp/pdf_{}/{}.pdf'.format(tmpd, paczka), 'wb') as f_out:
        f_out.write(output.getvalue())
        
    return HttpResponse(file_pdf) # output.getvalue(), content_type= 'application/pdf')

