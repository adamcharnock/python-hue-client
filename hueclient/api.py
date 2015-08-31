from time import sleep
import requests

import exceptions
from hueclient import utilities


class HueClient(object):
    _connection = None

    def register_connection(self, connection):
        self.__dict__['_connection'] = connection

    def __getattr__(self, item):
        return getattr(self._connection, item)

    def __setattr__(self, key, value):
        setattr(self._connection, key, value)

hue_client = HueClient()


class Connection(object):

    def __init__(self, bridge_host='philips-hue', username=None):
        username = username or utilities.load_username()
        if not username:
            raise exceptions.UsernameRequired('Username not specified and not found on disk')

        self.base_url='http://{bridge_host}/api/{username}'.format(**locals())

    def make_url(self, endpoint):
        return '{}/{}'.format(self.base_url, endpoint.lstrip('/'))

    def get(self, endpoint):
        r = requests.get(self.make_url(endpoint))
        return utilities.parse_response(r)

    def put(self, endpoint, json):
        r = requests.put(self.make_url(endpoint), json=json)
        return utilities.parse_response(r)
