# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _

class MyUserAdmin(UserAdmin):
    filter_horizontal= ()
    list_display= ('username', 'first_name', 'last_name', 'email', 'is_superuser')        
    fieldsets= (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    formfield_overrides = {
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
    }    
    
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin) 
