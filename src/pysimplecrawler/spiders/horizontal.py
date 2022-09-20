from . import AbsSpider, SpiderBase

class Horizontal(AbsSpider, SpiderBase):
    def start(self):
        links_repetition = self.send_request(self.url, depth=self.depth, prev_links=None)
        if links_repetition is not None:
            self._crawl(links_repetition, depth=self.depth)

    def _crawl(self, links_repetition:dict, depth:int):
        depth = depth - 1
        if links_repetition is not None:
            for link in links_repetition.keys():
                links_repetition_new = self.send_request(link, depth, links_repetition)
                if depth > 0:
                    self._crawl(links_repetition_new, depth)
