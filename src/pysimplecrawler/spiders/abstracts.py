from abc import ABCMeta, abstractmethod

class AbsSpider(metaclass=ABCMeta):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def _crawl(self):
        pass
