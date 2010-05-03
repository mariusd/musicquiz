import unittest
import doctest
import musicquiz.quiz.forms
import musicquiz.quiz.utility
import musicquiz.quiz.views
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
        doctest.DocTestSuite(musicquiz.quiz.forms),
        doctest.DocTestSuite(musicquiz.quiz.utility),
        doctest.DocTestSuite(musicquiz.quiz.views),
        homophony.DocFileSuite('tests.txt'),
    ])
    return suite