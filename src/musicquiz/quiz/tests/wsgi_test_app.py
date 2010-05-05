from urlparse import urlunparse
import wsgi_intercept
import urllib2
import os
import sys

if sys.version < '2.6':
    import md5
    def md5hash(string):
        return md5.new(string).hexdigest()
else:
    from hashlib import md5
    def md5hash(string):
        return md5(string).hexdigest()
        
###########################################################################
# Source: httplib_intercept.py from wsgi_intercept SVN trunk
###########################################################################
"""intercept HTTP connections that use httplib

(see wsgi_intercept/__init__.py for examples)

"""

import httplib
import wsgi_intercept
import sys
from httplib import (
    HTTPConnection as OriginalHTTPConnection, 
    HTTPSConnection as OriginalHTTPSConnection)

def install():
    httplib.HTTPConnection = wsgi_intercept.WSGI_HTTPConnection
    httplib.HTTPSConnection = wsgi_intercept.WSGI_HTTPConnection

def uninstall():
    httplib.HTTPConnection = OriginalHTTPConnection
    httplib.HTTPSConnection = OriginalHTTPSConnection
###########################################################################

def reconstruct_url(environ):
    """Reconstruct full URL from environ dictionary.
    
    Source: http://www.python.org/dev/peps/pep-0333/#url-reconstruction
    """
    
    # Example of environ dictionary that I get from gdata request:
    
    #{'CONTENT_TYPE': 'application/atom+xml',
    # 'wsgi.multithread': 0,
    # 'SCRIPT_NAME': '',
    # 'wsgi.input': <cStringIO.StringI object at 0x018987A0>,
    # 'REQUEST_METHOD': 'GET',
    # 'HTTP_HOST': 'gdata.youtube.com',
    # 'PATH_INFO': 'http://gdata.youtube.com/feeds/videos',
    # 'SERVER_PROTOCOL': 'HTTP/1.1\r\n',
    # 'QUERY_STRING': 'vq=Ladytron+Playgirl',
    # 'HTTP_USER_AGENT': 'None GData-Python/2.0.9',
    # 'wsgi.version': (1, 0),
    # 'SERVER_NAME': 'gdata.youtube.com',
    # 'REMOTE_ADDR': '127.0.0.1',
    # 'wsgi.run_once': 0,
    # 'wsgi.errors': <cStringIO.StringO object at 0x019FB060>,
    # 'wsgi.multiprocess': 0,
    # 'wsgi.url_scheme': 'http',
    # 'SERVER_PORT': '80',
    # 'HTTP_ACCEPT_ENCODING': 'identity'}
    
    # Temporary (well, most likely it will stay here forever) solution:
    if environ['HTTP_HOST'] == 'gdata.youtube.com':
        return '?'.join([environ['PATH_INFO'], environ['QUERY_STRING']])
        
    print environ['wsgi.input'].read()
    
    from urllib import quote
    url = environ['wsgi.url_scheme']+'://'

    if environ.get('HTTP_HOST'):
        url += environ['HTTP_HOST']
    else:
        url += environ['SERVER_NAME']

        if environ['wsgi.url_scheme'] == 'https':
            if environ['SERVER_PORT'] != '443':
               url += ':' + environ['SERVER_PORT']
        else:
            if environ['SERVER_PORT'] != '80':
               url += ':' + environ['SERVER_PORT']

    url += quote(environ.get('SCRIPT_NAME',''))
    url += quote(environ.get('PATH_INFO',''))
    if environ.get('QUERY_STRING'):
        url += '?' + environ['QUERY_STRING']
    return url
   
def create_app(host, port=80):

    def test_app(environ, start_response):
        """Simplest possible application object"""
        url =  reconstruct_url(environ)
        key = md5hash(url)
        status = '200 OK'
        response_headers = [('Content-type','text/xml')]
        start_response(status, response_headers)
        dir = os.path.join(os.path.dirname(__file__), 'data', host)
        try:
            os.mkdir(dir)
        except OSError:
            # if the directory was already created
            pass 
        file = os.path.join(dir, "%s.xml" % key)
        try:
            filedata = open(file).read()
        except IOError:
            create_fn, script = wsgi_intercept._wsgi_intercept[(host, port)]
            remove_redirect(host, port)
            print url
            filedata = urllib2.urlopen(url).read()
            redirect(host, port)
            open(file, "w").write(filedata)
        return [filedata]
        
    return test_app
    
def redirect(host, port=80):
    install()
    app = create_app(host, port)
    wsgi_intercept.add_wsgi_intercept(host, port, lambda : app)

def remove_redirect(host, port=80):
    wsgi_intercept.remove_wsgi_intercept(host, port)
    uninstall()

