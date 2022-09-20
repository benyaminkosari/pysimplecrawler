from ..scraper.request import Request, AsyncRequest
from ..scraper.parser import Link, Attributes
import gc

class SpiderBase:
    def __init__(self, url:str, depth:int, config : dict = None):
        self.url = url+'/' if not url.endswith('/') else url
        self.depth = depth
        self.config = config
        self.already_sent = dict()

    def get_links(self, content):
        if content is not None:
            link_obj = Link(self.url, content, self.config)
            links = link_obj.links
            link_obj.soup.decompose()
            gc.collect()
            return links

    def get_soup(self, content):
        if content is not None:
            link_obj = Link(self.url, content, self.config)
            links = link_obj.links
            link_obj.soup.decompose()
            gc.collect()
            return links

    def get_tags(self, content):
        if content is not None:
            link_obj = Link(self.url, content, self.config)
            tags = link_obj.tags
            link_obj.soup.decompose()
            gc.collect()
            return tags

    def _set_already_sent(self, url, status, depth, content, prev_links):
        if prev_links is not None:
            self.already_sent[url] = {
                "depth": self.depth-depth,
                "status": status,
                "count": prev_links[url]['count'],
                "type": prev_links[url]['type'],
                "tags": self.get_tags(content) if content else None
            }

    def send_request(self, url:str, depth:int, prev_links:dict) -> dict:
        if url not in self.already_sent.keys():
            request = Request()
            request.headers = self.config.get('headers')
            response = request.get(url)
            if self.config.get('logs') is not None:
                if self.config['logs']:
                    print(depth, url, response.status_code)
            if response:
                return self._single_links_repetition(url, response, depth, prev_links)

    def send_group_request(self, urls:list, depth:int, prev_links:dict) -> dict:
        urls = self._purge_already_sent(urls)
        if urls:
            request = AsyncRequest(self.config.get('workers'), self.config.get('logs'))
            request.headers = self.config.get('headers')
            responses = request.get(urls, depth)
            if responses:
                return self._get_group_links_repetition(request, responses, depth, prev_links)

    def _single_links_repetition(self, url, response, depth, prev_links):
        self._set_already_sent(url, response.status_code, depth, response.text, prev_links)
        links = self.get_links(response.text)
        return self._get_links_repetition(self.url, url, links)

    def _get_group_links_repetition(self, request, responses, depth, prev_links):
        group_links_repetition = {}
        for url, content in responses.items():
            self._set_already_sent(url, request.responses.get(url), depth, content, prev_links)
            links = self.get_links(content)
            group_links_repetition[url] = self._get_links_repetition(self.url, url, links)
        return group_links_repetition

    def _purge_already_sent(self, urls):
        purged_urls = []
        for i, url in enumerate(urls):
            if not url in self.already_sent.keys():
                purged_urls.append(url)
        return purged_urls

    def _is_all_same_links(self, links:list) -> bool:
        if set(links).issubset(self.already_sent):
            return False
        return True

    @staticmethod
    def _get_links_repetition(base_url, url, links):
        if links is not None:
            attrs = Attributes(base_url, url, links)
            return attrs.links_repetition
