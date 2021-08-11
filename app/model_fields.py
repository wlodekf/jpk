# -*- coding: utf-8 -*- 

from __future__ import unicode_literals

from base64 import b64decode, b64encode

from django.core import validators
from django.db import models
from django.db.models import signals
from django.utils import six
from django.utils.encoding import force_bytes
from django.utils.text import compress_string

from io import BytesIO
import gzip


class BlobField(models.Field):
    description= "Blob"
    def db_type(self, connection):
        return 'BLOB'
    

def uncompress_string(s):
    """ 
    Helper function to reverse django.utils.text.compress_string.
    
    Podana wartość może być skompresowana lub nie oba przypadki są poprawne.
    Jeżeli więc dekompresja się nie udaje to cicho zwracana jest oryginalan wartość. 
    """
    ret= s        
    try:
        zbuf = BytesIO(s)
        zfile = gzip.GzipFile(fileobj=zbuf)
        ret = zfile.read()
        zfile.close()
        ret= ret.decode('utf-8')
    except Exception as e:
        pass
        
    return ret


class CompressedTextField(models.TextField):
    """
    Uwaga: Tutaj trochę jest do dupy ponieważ przypisanie wartości do pola, 
    nie powoduje jego kompresji (nie jest wywoływana get_db_prep_save).
    Więc później przy czytaniu nie powinno być dekompresji.
    
    Natomiast jeżeli obiekt został odczytany z bazy danych to wartość pola
    jest skompresowana i powinna być dekompresowana.
    
    Dlatego uncompress działa tak, że próbuje rozpakować wartość a jeżeli się
    nie uda to zwraca wartość pola i ona wtedy też jest poprawna.
    Nie powinno być natomiast sygnalizowania tutaj błędów.
    
    Nie wiadomo jeszcze co jest z encode/decode utf-8.
    Czasami (rzadko) konieczne jest zakodowanie bo inaczej jest problem.
    """

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        if not value:
            value= ''
        return value

    def get_db_prep_save(self, value, connection):
        if not value:
            value= ''
            
        if value:
            try:
                # Encodowanie powinno być robione tylko dla stringów (unicode w py2)
                # XLS nie powinny być przechowywane w tym polu!
                # To powinno być pole Byte compressowane
                value = value.encode('utf-8')
                # Po co tutaj encodujemy? Aby zamienić na bajty?
                # Bo tak potrzebuje compress?
                # Ale przecież to jest compress_string?
            except:
                pass
            
            value = compress_string(value)
        
        # Tutaj mamy str w py2 i bytes w py3
        # Nie robimy przetwarzania z TextField bo ono w py3 robi encodowanie 
        # i wtedy dupa
        return value
#         return models.TextField.get_db_prep_save(self, value, connection)
 
    def _get_val_from_obj(self, obj):
        val= self.default()
        if obj:
            val= getattr(obj, self.attname)
            if val:
                val= uncompress_string(val)
            else:
                val= ''
        return val
    
    def post_init(self, instance, force=False, *args, **kwargs):
        value = self._get_val_from_obj(instance)
        if value:
            setattr(instance, self.attname, value)

    def contribute_to_class(self, cls, name):
        super(CompressedTextField, self).contribute_to_class(cls, name)
#         dispatcher.connect(self.post_init, signal=signals.post_init, sender=cls)
        signals.post_init.connect(self.post_init, sender=cls)
                
    
    def get_internal_type(self):
        return "TextField"
                
    def db_type(self, connection):
        return 'BLOB'
    
        
# add_introspection_rules([], ["^efaktury\.ef\.model_fields\.CompressedTextField"])



class BinaryField(models.Field):
    description = "Raw binary data"
    empty_values = [None, b'']

    def __init__(self, *args, **kwargs):
        kwargs['editable'] = False
        super(BinaryField, self).__init__(*args, **kwargs)
        if self.max_length is not None:
            self.validators.append(validators.MaxLengthValidator(self.max_length))

    def get_internal_type(self):
        return "BinaryField"
    
    def db_type(self, connection):
        return 'BLOB'    

    def get_default(self):
        if self.has_default() and not callable(self.default):
            return self.default
        default = super(BinaryField, self).get_default()
        if default == '':
            return b''
        return default

    def get_db_prep_value(self, value, connection, prepared=False):
        value = super(BinaryField, self
            ).get_db_prep_value(value, connection, prepared)
        if value is not None:
            return buffer(value)
        return value

    def value_to_string(self, obj):
        """Binary data is serialized as base64"""
        return b64encode(force_bytes(self._get_val_from_obj(obj))).decode('ascii')

    def to_python(self, value):
        if isinstance(value, six.text_type):
            value= buffer(b64decode(force_bytes(value)))
        return value
