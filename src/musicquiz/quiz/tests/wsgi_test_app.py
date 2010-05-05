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
   
def create_app(host, port=80):

    def test_app(environ, start_response):
        """Simplest possible application object"""
        url_parts = (environ['wsgi.url_scheme'], environ['HTTP_HOST'],
                     environ['PATH_INFO'], '', environ['QUERY_STRING'], '')
        url =  urlunparse(url_parts)
        key = md5hash(url)
        status = '200 OK'
        response_headers = [('Content-type','text/xml')]
        start_response(status, response_headers)
        dir = os.path.join('data')
        file = os.path.join(os.path.dirname(__file__), dir, "%s.xml" % key)
        try:
            filedata = open(file).read()
        except IOError:
            create_fn, script = wsgi_intercept._wsgi_intercept[(host, port)]
            wsgi_intercept.remove_wsgi_intercept(host, port)
            filedata = urllib2.urlopen(url).read()
            wsgi_intercept.add_wsgi_intercept(host, port, create_fn, script)
            open(file, "w").write(filedata)
        return [filedata]
        
    return test_app
    
def redirect(host, port=80):
    from wsgi_intercept.urllib2_intercept import install_opener
    install_opener()
    app = create_app(host, port)
    wsgi_intercept.add_wsgi_intercept(host, port, lambda : app)

def remove_redirect(host, port=80):
    wsgi_intercept.remove_wsgi_intercept(host, port)
