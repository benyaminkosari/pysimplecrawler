import requests
from requests.models import Response
import asyncio, aiohttp
from aiohttp.client import ClientSession
from .utils import LinkUtils, timed

class RequestBase:
    utils = LinkUtils()

    def __init__(self):
        self._headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Connection': 'keep-alive',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'upgrade-insecure-requests': '1',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US,en;q=0.9',
        }

    @property
    def headers(self) -> dict:
        return self._headers

    @headers.setter
    def headers(self, headers:dict):
        if headers is not None:
            for key, value in headers.items():
                self._headers[key] = value

    @staticmethod
    def _clean_url(url:str) -> str:
        return url+'/' if not url.endswith('/') else url


class Request(RequestBase):
    def __init__(self):
        super().__init__()
        self.session = requests.session()

    def get(self, url:str) -> Response:
        try:
            a = self.session.get(url, headers=self.headers)
            return a
        except Exception as e:
            if e.__class__.__name__ == 'MissingScheme':
                print("MissingScheme:", url)
            else:
                print("Error:", e)

    def head(self, url:str) -> Response:
        url = self._clean_url(url)
        try:
            return self.session.head(url, headers=self.headers)
        except Exception as e:
            print("Error:", e)


class AsyncRequest(RequestBase):
    _responses = dict()

    def __init__(self, workers: int = 10, logs : bool = True):
        super().__init__()
        self.workers = workers
        self.logs = logs

    @property
    def responses(self) -> dict:
        return self._responses

    @timed
    def get(self, urls:list, depth:int):
        try:
            result = asyncio.run(self._get_all(urls, depth))
        except aiohttp.client_exceptions.TooManyRedirects as e:
            print("TooManyRedirects: ", e.request_info.url)
        except aiohttp.client_exceptions.ClientConnectorCertificateError as e:
            print("SSL Certificate Error: ", e.request_info.url)
        except aiohttp.client_exceptions.ClientPayloadError as e:
            print("ClientPayloadError")
        return result

    async def _get_all(self, urls:list, depth:int):
        tasks = []
        html_dict = {}
        connector = aiohttp.TCPConnector(limit=self.workers)
        async with aiohttp.ClientSession(connector=connector) as session:
            for url in urls:
                tasks.append(
                    asyncio.create_task(
                        self._fetch(session, url, self.headers, depth)
                    )
                )
            html_list = await asyncio.gather(*tasks)

            for i, url in enumerate(urls):
                html_dict[url] = html_list[i]
            return html_dict

    async def _fetch(self, session:ClientSession, url:str, headers:dict, depth:int):
        try:
            async with session.get(url, headers=headers) as response:
                if self.logs is not None:
                    if self.logs:
                        print(depth, url, response.status)
                self.responses[url] = response.status
                return await response.text()
        except asyncio.exceptions.TimeoutError:
            pass
