"""

This module handles interaction with tBB.

"""

import json
import asyncio
import aiohttp
import sys
import os
import ssl
from asyncio import coroutine


class RequestError(Exception):
    def __init__(self, request, status, text):
        self.request = request
        self.status = status
        self.text = text
        super().__init__("Got error back from request '{}': status = {}. Body: {}.".format(request, status, text))


class RequestsHandler(object):
    def __init__(self, host, port, password, use_ssl=True, loop=None):
        self.host = host
        self.port = port
        self.password = password
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop
        if use_ssl:
            self.sslcontext = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            self.sslcontext.options |= ssl.OP_NO_SSLv2
            self.sslcontext.options |= ssl.OP_NO_SSLv3
            ca_file_path = os.path.join(os.getcwd(), "certs", "cert.pem")
            key_file_path = os.path.join(os.getcwd(), "certs", "key.pem")
            if os.path.isfile(ca_file_path) and os.path.isfile(key_file_path):
                self.sslcontext.load_cert_chain(certfile=ca_file_path, keyfile=key_file_path)
                self.sslcontext.check_hostname = True
            else:
                self.sslcontext.check_hostname = False
                self.sslcontext.verify_mode = ssl.CERT_NONE
        else:
            self.sslcontext = None
        self.conn = aiohttp.TCPConnector(ssl_context=self.sslcontext)
        self.session = aiohttp.ClientSession(connector=self.conn)
        self._create_default_requests()

    @coroutine
    def fetch(self, url, include_password=True):
        with aiohttp.Timeout(4):
            response = yield from self.session.get(
                "{}://{}:{}/{}/{}".format(
                    'https' if self.sslcontext else 'http', self.host, self.port, url,
                    self.password + '/' if include_password else ''
            ))
        try:
            status = response.status
            with aiohttp.Timeout(3):
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

    def _create_request(self, name, url, include_password=True):
        @coroutine
        def do_request(*args):
            status, text = yield from self.fetch(url.format(*args), include_password)
            if status == 200:
                return text
            else:
                raise RequestError(url.format(*args), status, text)
        setattr(self, name, do_request)

    def _create_default_requests(self):
        # requests wrapped in a tuple do not require password
        requests = {
            'ip_info': 'ip_info/{}',
            'mac_info': 'mac_info/{}',
            'name_info': 'name_info/{}',
            'test': ('test',),
            'stats': 'stats',
            'status': 'status',
            'settings_get': 'settings/get/{}',
            'settings_set': 'settings/set/{}/{}',
            'ignore': 'ignore/{}/{}',
            'ignore_mac': 'ignore_mac/{}/{}',
            'ignore_name': 'ignore_name/{}/{}',
            'is_ignored': 'is_ignored/{}',
            'is_mac_ignored': 'is_mac_ignored/{}',
            'is_name_ignored': 'is_name_ignored/{}',
            'ignored_ips': 'ignored_ips',
            'ignored_macs': 'ignored_macs',
            'ignored_names': 'ignored_names',
            'set_priority': 'set_priority/{}/{}',
            'get_priority': 'get_priority/{}',
            'ip_host_changes': 'ip_host_changes/{}/{}/{}',
            'mac_host_changes': 'mac_host_changes/{}/{}/{}',
            'name_host_changes': 'name_host_changes/{}/{}/{}',
            'up_ip_hosts': 'up_ip_hosts',
            'up_mac_hosts': 'up_mac_hosts',
            'up_name_hosts': 'up_name_hosts',
        }
        for request in requests:
            if type(requests[request]) == str:
                self._create_request(request, requests[request])
            elif type(requests[request]) == tuple:
                self._create_request(request, requests[request][0], include_password=False)

    def __del__(self):
        self.session.close()
