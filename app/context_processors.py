# -*- coding: utf-8 -*-

from __future__ import unicode_literals

def alert(request):
    """
    Dodanie do konteksu alertu do wyświetlenia po załadowaniu strony.
    """

    alert= request.session.get('alert')
    if alert:
        del request.session['alert']
        return {'alert': alert} 
    else:
        return {}


def home(request):
    if(not request.user.is_authenticated()):
        return {'HOME_LABEL': 'KREZUS-FK'}
    else:
        return {}