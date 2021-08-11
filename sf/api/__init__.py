# -*- coding: utf-8 -*-

import datetime

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

RZYM= {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9}


def access_control(response, cors= False):
    """
    Dodanie nagłówków pozwalających na obejście same origin policy.
    """
    if cors:
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
        
    return response
    

def GO_HOME(jpk= None, firma= None):
    response= HttpResponseRedirect(reverse('home', args= [jpk._firma() if jpk else firma]))
    response.set_cookie('tr_id', 'tr_1141')
    return response 


def txt2data(txt):
    return datetime.datetime.strptime(txt, '%Y-%m-%d') if txt else None