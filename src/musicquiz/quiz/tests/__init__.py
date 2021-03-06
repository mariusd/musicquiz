import unittest
import doctest
import urllib
from django.test import TestCase
import homophony

def suite():  
    import musicquiz.quiz.tests.wsgi_test_app as wsgi_test_app
    
    def setUp(doctest):
        """Redirect all web API calls to the local WSGI application."""
        
        def reconstruct_gdata(environ):
            return '?'.join([environ['PATH_INFO'], environ['QUERY_STRING']])
            
        def reconstruct_pylast(environ):
            query = environ['wsgi.input'].read()
            return 'http://ws.audioscrobbler.com/2.0/?' + query
        
        wsgi_test_app.redirect('gdata.youtube.com', reconstruct_gdata)
        wsgi_test_app.redirect('ws.audioscrobbler.com', reconstruct_pylast)
        
    def tearDown(doctest):
        """Remove wsgi_interceptions."""
        wsgi_test_app.remove_redirect('gdata.youtube.com')
        wsgi_test_app.remove_redirect('ws.audioscrobbler.com')
    
    suite = unittest.TestSuite([
        doctest.DocFileSuite('models.txt', setUp=setUp, tearDown=tearDown),
        doctest.DocFileSuite('views.txt', setUp=setUp, tearDown=tearDown),
        doctest.DocFileSuite('forms.txt', setUp=setUp, tearDown=tearDown),
        doctest.DocFileSuite('utility.txt', setUp=setUp, tearDown=tearDown),
        
        homophony.DocFileSuite('functional.txt'),
    ])
    return suite