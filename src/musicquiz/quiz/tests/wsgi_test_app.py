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
  
def create_app(host, reconstruct_url):
    """Return WSGI app which intercepts calls to `host` and returns
    a local copy of response data. If a local copy does not exist, this
    app connects to the original data source, saves a local copy, and
    then returns data to user.
    
    Parameter `recontruct_url` is a function which recontructs original
    url from WSGI environment dictionary. It is needed because of the
    different ways that libraries make requests. There must be a better
    solution for this problem, but this one is good enough for me..
    """

    def test_app(environ, start_response):
        """Simplest possible application object"""
        
        url, port =  reconstruct_url(environ), 80
        key = md5hash(url)
        status = '200 OK'
        response_headers = [('Content-type', 'text/xml')]
        start_response(status, response_headers)
        dir = os.path.join(os.path.dirname(__file__), 'data', host)
        try:
            os.makedirs(dir)
        except OSError:
            # if the directory was already created
            pass 
        file = os.path.join(dir, "%s.xml" % key)
        try:
            filedata = open(file).read()
        except IOError:
            create_fn, script = wsgi_intercept._wsgi_intercept[(host, port)]
            remove_redirect(host)
            try:
                filedata = urllib2.urlopen(url).read()
            except urllib2.HTTPError, e:
                filedata = e.read()
            redirect(host, reconstruct_url)
            open(file, "w").write(filedata)
        return [filedata]
        
    return test_app
    
def redirect(host, reconstruct_url):
    install()
    app = create_app(host, reconstruct_url)
    wsgi_intercept.add_wsgi_intercept(host, 80, lambda : app)

def remove_redirect(host):
    wsgi_intercept.remove_wsgi_intercept(host, 80)
    uninstall()

