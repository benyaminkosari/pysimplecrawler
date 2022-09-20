from . import AbsSpider, SpiderBase
from ..scraper.utils import timed

class Vertical(AbsSpider, SpiderBase):
    def __init__(self, url:str, depth:int, config:dict):
        super().__init__(url, depth, config)
        self.current_requests = dict()

    @timed
    def start(self):
        links_repetition = self.send_request(
            url=self.url,
            depth=self.depth,
            prev_links=None
        )
        for link in links_repetition.keys():
            links_repetition_new = self.send_request(link, self.depth, links_repetition)
            self.current_requests[link] = links_repetition_new
        self._crawl(depth=self.depth)

    def _crawl(self, depth:int):
        for i in range(depth-1):
            depth = depth - 1
            current_requests = dict(self.current_requests)
            for links_repetition in current_requests.values():
                if links_repetition is not None:
                    for link in links_repetition.keys():
                        links_repetition_new = self.send_request(link, depth, links_repetition)
                        self.current_requests[link] = links_repetition_new
            if current_requests == self.current_requests:
                break


class AsyncVertical(AbsSpider, SpiderBase):
    def __init__(self, url:str, depth:int, config:dict):
        super().__init__(url, depth, config)
        self.current_requests = dict()
        self._prev_links = dict()

    def start(self):
        links_repetition = self.send_request(
            url=self.url,
            depth=self.depth,
            prev_links=None
        )
        if links_repetition is not None:
            current_requests = self.send_group_request(links_repetition.keys(), self.depth, links_repetition)
            self.current_requests = current_requests
            self._crawl(depth=self.depth)

    def _crawl(self, depth:int):
        for i in range(depth):
            depth = depth - 1
            urls = []
            if self.current_requests is None:
                continue
            for links_repetition in self.current_requests.values():
                if links_repetition is not None:
                    urls.extend(list(links_repetition.keys()))

            self.current_requests = self.send_group_request(urls, depth, self.prev_links)

    @property
    def prev_links(self) -> dict:
        self._prev_links = {}
        for value in self.current_requests.values():
            for url, detail in value.items():
                self._prev_links[url] = detail
        return self._prev_links
