import requests

import exceptions
from hueclient import utilities


class Client(object):

    def __init__(self, base_url):
        self.base_url = base_url

    def make_url(self, endpoint):
        return '{}/{}'.format(self.base_url, endpoint.lstrip('/'))

    def get(self, endpoint):
        r = requests.get(self.make_url(endpoint))
        return utilities.parse_response(r)

    def put(self, endpoint, json):
        r = requests.put(self.make_url(endpoint), json=json)
        return utilities.parse_response(r)


class Api(object):
    resources = []
    client_class = Client
    base_url = '/'

    def __init__(self):
        self.client = self.get_client()
        for resource in self.resources:
            resource.contribute_client(self.client)

    def register_resource(self, resource):
        self.resources.add(resource)

        # Pass the client to the model if we have the client available
        if self.client:
            resource.contribute_client(self.client)

    def get_client_class(self):
        return self.client_class

    def get_client(self):
        client_class = self.get_client_class()
        return client_class(self.get_base_url())

    def get_base_url(self):
        return self.base_url




