from urllib.parse import urlparse
import time

class LinkUtils:
    attrs = [
        'null',
        'internal_relative',
        'internal_absolute',
        'external',
        'subdomain',
        'empty',
        'hyperlink'
    ]
    other_keys = ['null', 'empty', 'hyperlink']
    useful_keys = ['internal_relative', 'internal_absolute', 'external', 'subdomain']

    def is_subdomain(self, url:str, base_url:str) -> bool:
        url_parts = self.netloc(url).split('.', 1)
        if len(url_parts) > 1:
            if url_parts[1] == urlparse(base_url).hostname:
                return True
        return False

    @staticmethod
    def netloc(url:str) -> str:
        return urlparse(url).netloc

    @staticmethod
    def fragment(url:str) -> str:
        return urlparse(url).fragment

    @staticmethod
    def scheme(url:str) -> str:
        return urlparse(url).scheme

    @staticmethod
    def has_path(href:str) -> bool:
        path_exclude = ['/', '']
        if urlparse(href).path in path_exclude:
            return True
        return False

def timed(func:callable):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = "{name:<30} finished in {elapsed:.2f} seconds".format(
            name=func.__name__, elapsed=time.time() - start
        )
        print(duration)
        return result
    return wrapper
