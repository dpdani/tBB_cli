"""

This module handles interaction with tBB.

"""

import json
import asyncio
import aiohttp
import sys
from asyncio import coroutine


class RequestError(Exception):
    def __init__(self, status, text):
        super().__init__("Got error back from request: status = {}. Body: {}.".format(status, text))


class RequestsHandler(object):
    def __init__(self, host, port, password, loop=None):
        self.host = host
        self.port = port
        self.password = password
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop
        self.session = aiohttp.ClientSession()
        self._create_default_requests()

    @coroutine
    def fetch(self, url, include_password=True):
        response = yield from self.session.get(
            "{}://{}:{}/{}/{}/".format('http', self.host, self.port, url, self.password if include_password else '')
        )
        try:
            status = response.status
            text = yield from response.text()
            try:
                text = json.loads(text)
            except:
                pass
        finally:
            if sys.exc_info()[0] is not None:
                # on exceptions, close the connection altogether
                response.close()
            else:
                yield from response.release()
        return status, text

    def _create_request(self, name, url):
        @coroutine
        def do_request(*args):
            status, text = yield from self.fetch(url.format(*args))
            if status == 200:
                return text
            else:
                raise RequestError(status, text)
        setattr(self, name, do_request)

    def _create_default_requests(self):
        requests = {
            'ip_info': 'ip_info/{}',
            'mac_info': 'mac_info/{}',
            'test': 'test',
            'status': 'status',
            'settings_get': 'settings/get/{}',
            'settings_set': 'settings/set/{}/{}',
            'ignore': 'ignore/{}/{}',
            'set_priority': 'set_priority/{}/{}',
            'ip_host_changes': 'ip_host_changes/{}',
            'mac_host_changes': 'mac_host_changes/{}'
        }
        for request in requests:
            self._create_request(request, requests[request])
