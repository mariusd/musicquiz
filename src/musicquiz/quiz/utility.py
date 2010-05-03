import urlparse

def extract_youtube_code(url):
    """Extract youtube video code (e.g. EjAoBKagWQA) from url.
    
    >>> eyc = extract_youtube_code
    >>> eyc('http://www.youtube.com/watch?v=qndUS3SIf1Q&feature=related')
    'qndUS3SIf1Q'
    >>> eyc('http://www.youtube.com/watch?feature=related&v=qndUS3SIf1Q')
    'qndUS3SIf1Q'
    >>> eyc('http://youtube.com/v/3Ii8m1jgn_M?f=videos&app=youtube_gdata')
    '3Ii8m1jgn_M'
    >>> eyc('http://www.youtube.com/watch?WRONG=qndUS3SIf1Q')
    Traceback (most recent call last):
    ...
    ValueError: cannot extract code (wrong url?)
    """
    result = urlparse.urlparse(url, scheme='http')
    if result.path == '/watch':
        parse_query = urlparse.parse_qs(result.query)
        if 'v' in parse_query.keys():
            return parse_query['v'][0]
    elif result.path[:3] == '/v/':
        return result.path[3:]
    raise ValueError('cannot extract code (wrong url?)')
