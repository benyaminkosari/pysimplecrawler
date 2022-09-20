from bs4 import BeautifulSoup, SoupStrainer
from bs4.element import Tag
from .utils import LinkUtils
import cchardet

class PageSource:
    def __init__(self, base_url:str, content:str, config : dict = None):
        self.base_url =  base_url+'/' if not base_url.endswith('/') else base_url
        self.config = self._get_config(config)
        self.soup = self._get_soup(content)

    @staticmethod
    def _get_config(config:dict) -> dict:
        if config.get('tags'):
            if 'a' not in config['tags']:
                config['tags'].append('a')
        else:
            config['tags'] = ['a']
        return config

    def _get_soup(self, content:str) -> BeautifulSoup:
        soup = BeautifulSoup(content, 'lxml',
            parse_only=SoupStrainer(self.config.get('tags'))
        )
        return soup

    @property
    def tags(self) -> dict:
        tags_dict = {}
        for tag in self.config.get('tags'):
            tags_dict[tag] = self.soup.find_all(tag)
        return tags_dict

    @property
    def a_tags(self) -> list[Tag]:
        return self._get_a_tags()

    def _get_a_tags(self) -> list[Tag]:
        return self.soup.find_all('a')

    @property
    def hrefs(self) -> list[str]:
        return self._get_hrefs()

    def _get_hrefs(self) -> list[str]:
        hrefs = []
        for a in self._get_a_tags():
            hrefs.append(a.get('href'))
        return hrefs

class Link(PageSource):
    def __init__(self, base_url:str, response:str, config:dict):
        super().__init__(base_url, response, config)
        self.utils = LinkUtils()

    @property
    def links(self) -> dict:
        return self._get_links()

    def _get_links(self) -> dict:
        self._clean_attributes()
        self._fill_attributes()
        return self._get_links_dict()

    def _clean_attributes(self):
        for attr in self.utils.attrs:
            setattr(self, attr, list())

    def _get_links_dict(self) -> dict:
        links = dict()
        for attr in self.utils.attrs:
            links[attr] = getattr(self, attr)
        return links

    def _fill_attributes(self):
        for href in self.hrefs:
            if href is None:
                self.null.append(href)
            elif href.startswith('#') or self.utils.fragment(href):
                self.hyperlink.append(href)
            elif href == '':
                self.empty.append(href)
            else:
                if self.utils.has_path(href):
                    href = href+'/' if not href.endswith('/') else href
                if self.utils.is_subdomain(href, self.base_url):
                    self.subdomain.append(href)
                else:
                    bare_href = self.utils.netloc(href)
                    if not bare_href and href.find(":") < 0:
                        self.internal_relative.append(href)
                    elif bare_href.startswith(self.utils.netloc(self.base_url)):
                        self.internal_absolute.append(href)
                    else:
                        self.external.append(href)


class Attributes:
    utils = LinkUtils()

    def __init__(self, base_url:str, url:str, links:dict):
        self.base_url =  base_url+'/' if not base_url.endswith('/') else base_url
        self.url =  url
        self.links = links
        self.useful_links = self._get_useful_links()
        self._all_links = dict()

    def _get_useful_links(self) -> list:
        useful_links = dict(self.links)
        for key in self.utils.other_keys:
            useful_links.pop(key)
        return useful_links

    @property
    def internal_relatives(self) -> list:
        internals = list()
        for link in self.useful_links['internal_relative']:
            if link == '/' or link == './' or link == '../':
                continue
            if link.startswith('/') or link.startswith('?'):
                scheme = self.utils.scheme(self.url)
                netloc = self.utils.netloc(self.url)
                internals.append(f'{scheme}://{netloc}{link}')
            else:
                internals.append(self.url+link)
        return internals

    @property
    def all_links(self) -> list:
        self._all_links = dict(self.useful_links)
        self._all_links.pop('external')
        self._all_links.pop('subdomain')
        self._all_links['internal_relative'] = self.internal_relatives
        return self._all_links

    @property
    def links_repetition(self) -> dict:
        result = {}
        for type_, links in self.all_links.items():
            for link in links:
                result[link] = {
                    "type": type_,
                    "count": links.count(link)
                }
        return result
