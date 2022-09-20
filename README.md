

Python Simple Crawler
===============
This is an extendable and easy-to-use crawler which can be fully customized according to your needs.
* Supports asynchronous requests
* Able to add special crawling strategies within custom spiders
* Specify needed tags to be scraped
* Access to full logs and detailed execution timing
* Minimize RAM usage by making use of BeautifulSoup's decomposition and python's garbage collection


Getting Started
====
Install the package using pip:
```bash
pip install pysimplecrawler
```
Or download the source code using this command:

    git clone https://github.com/benyaminkosari/pysimplecrawler.git

Usage
====
1. Import Crawler
```python
from pysimplecrawler import crawler
```

2. Define the main url to crawl:
```python
url = "https://example.com/"
```
3. Add custom config if needed:
```python
config = {
    "async": True,
    "workers": 5,
    "headers": {"cookies", "my_cookie"}
}
```
4. Execute the process:
```python
spider = crawler.Crawl(url, depth=3, config=config)
spider.start()
```
5. Access result:
```python
print(spider.data)
```

Reference
====
### crawler.Crawl(url, depth, priority, config)
 * `url : str (required)`</br>
 Target's address to start crawling
 * `depth : int (optional) default=3`</br>
 Maximum level which crawlers must go deep through target's urls
 * `priority : str (optional) default='vertical'`</br>
 Strategy which the crawler uses. It's the name of the spider's class (all lowercase)</br>
 Note that starting the class name with 'Async' will be automatically handled from config
 * `config : dict (optional)`</br>
 Change default and add extra settings

    * `tags : list = ["img", "h1", "meta", "title", ...]`</br>
    Html tags to be scraped while crawling
    * `async : bool default=False`</br>
    Whether requests must be sent concurrently
    * `workers : int default=10`</br>
    Number of requests to be sent simultaneously
    * `logs : bool default=True`</br>
    Whether logs must be shown
    * `headers : dict`</br>
    Headers of the requests.</br>
    Note that there are already some default headers which will be overridden.


How does it work?
====
Crawl class of `pysimplecrawler.crawler` to Spider classes of `pysimplecrawler.spiders` are
connected as a Factory to its Products. Considering inheritance from AbsSpider as the abstract class
and SpiderBase as a helper class, You can add you own custom strategies to `/spiders` directory.

<p align="center">
  <img src="/pattern-uml.png">
</p>
