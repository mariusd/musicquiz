import urlparse
import collections

def extract_youtube_code(url):
    """Extract youtube video code (e.g. EjAoBKagWQA) from URL."""
    
    result = urlparse.urlparse(url, scheme='http')
    if result.path == '/watch':
        parse_query = urlparse.parse_qs(result.query)
        if 'v' in parse_query.keys():
            return parse_query['v'][0]
    elif result.path[:3] == '/v/':
        return result.path[3:]
    raise ValueError('cannot extract code (wrong url?)')
    

def create_fragment(objects_iter, obj, size):
    """Return a tuple (slice, position), where slice is a continuous
    subsequence of `objects_iter` containing the specified object `obj`
    and its closes neighbours. Position shows the beginning of slice.
    
    There are many examples of this function in tests/utility.txt.
    """

    if size <= 0:
        raise ValueError('size must be bigger than zero')
    fragment = collections.deque()
    last_removed = collections.deque()
    object_added = False
    for index, element in enumerate(objects_iter):
        fragment.append((index, element))
        if element == obj:
            object_added = True
        if not object_added and len(fragment) == (size + 1) / 2:
            last_removed.append(fragment.popleft())
            if len(last_removed) > size:
                last_removed.popleft()
        if len(fragment) == size:
            break
    else:
        for removed in reversed(last_removed):
            fragment.appendleft(removed)
            if len(fragment) == size:
                break
    if not object_added:
        raise ValueError('specified object was not found')
    pos = fragment[0][0]
    return [b for (a, b) in fragment], pos
