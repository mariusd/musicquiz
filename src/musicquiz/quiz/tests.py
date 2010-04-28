import unittest
import doctest
import forms
from django.test import TestCase
import homophony

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)
        
def suite():
    suite = unittest.TestSuite([
        SimpleTest('test_basic_addition'),
        doctest.DocTestSuite(forms),
        homophony.DocFileSuite('tests.txt'),
    ])
    return suite