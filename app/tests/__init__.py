# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
import xmlunittest
from lxml import etree
from app import utils
import decimal
from django.conf import settings

class JpkTestCase(TestCase, xmlunittest.XmlTestMixin):
    
    multi_db=True
        
    def assertXpath(self, node, xpath):
        """Asserts each xpath's result returns only one element."""
        expression= etree.XPath(xpath)
        results= expression.evaluate(node)
        if not results:
            self.fail('No result found for XPath on element %s:\n'
                      'XPath: %s\n'
                      'Element:\n%s'
                      % (node.tag, expression.path,
                         etree.tostring(node, pretty_print=True)))
                
        count= len(results)
        if count > 1:
            self.fail('Too many results found (%d) for XPath on '
                      'element %s:\n'
                      'XPath: %s\n'
                      'Element:\n'
                      '%s' % (count,
                              node.tag,
                              expression.path,
                              etree.tostring(node, pretty_print=True)))
            
        return results[0]


    def assertXpathSum(self, node, xpath, poprawna_suma):
        """Asserts each xpath's result returns only one element."""
        expression= etree.XPath(xpath)
        results= expression.evaluate(node)
        if not results:
            self.fail('No result found for XPath on element %s:\n'
                      'XPath: %s\n'
                      'Element:\n%s'
                      % (node.tag, expression.path,
                         etree.tostring(node, pretty_print=True)))
                
        suma= decimal.Decimal(0.00)
        for result in results:
            suma += decimal.Decimal(result.text)
        
        self.assertEqual(poprawna_suma, suma, 'Suma elementów')
        return suma
    
    
    def assertXpathCount(self, node, xpath, count):
        """Asserts each xpath's result returns given number of elements."""
        expression= etree.XPath(xpath)
        results= expression.evaluate(node)
        self.assertEqual(count, len(results), 'Niewłaściwa liczna elementów')
    
    def assertJpkBlad(self, zrodlo, dokument, blad):
        bledy= self.jpk.blad_set.filter(zrodlo= zrodlo, dokument= dokument, blad= blad)
        self.assertTrue(bledy.exists(), 'Brak błędu: {}/{}/{}'.format(zrodlo, dokument, blad))
            
    def node_xml(self, node):
        return etree.tostring(node)
