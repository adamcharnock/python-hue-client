import requests

import exceptions
from hueclient import utilities
from hueclient.models.bridge import Bridge


class Client(object):

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


if __name__ == '__main__':
    client = Client()
    bridge = Bridge.objects.get(client)
    for l in bridge.lights:
        state = l.state
        state.on = True
        state.save(client)

