# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
logger= logging.getLogger(__name__)

from .delegacje import Delegacje


def powiadom(request): 
    """
    Wysłanie e-maili przypomnienia o rozliczeniu delegacji.
    """
    
    d= Delegacje()
    d.wyslij_przypomnienia()
    
    return d.as_view(request)
