from . import AbsSpider, SpiderBase

class NullSpider(AbsSpider):
    already_sent = None

    def start(self):
        raise NotImplementedError("Add your custom spider to simplecrawler/spiders")

    def _crawl(self):
        pass
