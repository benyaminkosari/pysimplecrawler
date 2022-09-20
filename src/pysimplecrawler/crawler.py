from inspect import getmembers, isclass, isabstract
from . import spiders

class Crawl:
    instances = dict()
    spider = None

    def __init__(self, url, depth=3, priority='vertical', config=None):
        self.url = url
        self.depth = depth - 1
        self.config = self._set_default_config(config)
        self.priority = self._check_priority(priority)
        self.load_spiders()

    def load_spiders(self):
        classes = getmembers(spiders,
            lambda c: isclass(c) and not isabstract(c)
        )
        for name , type_ in classes:
            if isclass(type_) and issubclass(type_, spiders.AbsSpider):
                self.instances.update([[name, type_]])

    def create_instance(self):
        if self.priority in self.instances:
            return self.instances[self.priority](self.url, self.depth, self.config)
        else:
            return spiders.NullSpider()

    def _check_priority(self, priority) -> str:
        async_type = ''
        if self.config.get('async') is not None:
            if self.config['async']:
                async_type = 'Async'
        if not priority[0].isupper():
            return async_type + priority.capitalize()
        return async_type + priority

    @staticmethod
    def _set_default_config(config) -> dict:
        config = {} if config is None else config
        if config.get('is_async') is None:
            config['is_async'] = False
        if config.get('logs') is None:
            config['logs'] = True
        return config

    def start(self):
        self.spider = self.create_instance()
        self.spider.start()

    @property
    def data(self) -> dict:
        if self.spider is None:
            return None
        return self.spider.already_sent
