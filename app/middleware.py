# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
from django.http import HttpResponseBadRequest

class HttpMethodsMiddleware(object):
    
    def process_request(self, request):
        
        if not request.method in ('GET', 'POST'):
        
            method= request.method
    
            if hasattr(request, '_post'):
                del request._post
                del request._files
                
            try:
                request.method = "POST"
                request._load_post_and_files()
                request.method = method
            except AttributeError as e:
                request.META['REQUEST_METHOD'] = 'POST'
                request._load_post_and_files()
                request.META['REQUEST_METHOD'] = method
                
            setattr(request, method, request.POST)

        # Z axios'a content type jest równy application/json;charset=UTF-8
        # Trzeba by to odpowiednio przetworzyć
        content_type= request.META['CONTENT_TYPE'].split(';')
        encoding= 'UTF-8'
        if len(content_type)>1:
            encoding= content_type[1].split('=')
            if len(encoding)>1:
                encoding= encoding[1]
            content_type= content_type[0]
        
        if request.method != "GET" and content_type == 'application/json':
            try:
                request.JSON = json.loads(request.body.decode(encoding, errors= 'ignore'))
                
            except ValueError as ve:
                return HttpResponseBadRequest("Unable to parse JSON data. Error : {0}".format(ve))
