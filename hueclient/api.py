import requests

import exceptions
from hueclient import utilities


class Api(object):

    def __init__(self):
        self.resources = set()
        self.client = None

    def register_resource(self, resource):
        self.resources.add(resource)

        # Pass the client to the model if we have the client available
        if self.client:
            resource.contribute_client(self.client)

    def set_client(self, client):
        """
        Set the client for the API to use, applying it to any
        already-registered resources.
        """
        if self.client:
            raise exceptions.ClientAlreadySet()
        self.client = client

        for r in self.resources:
            r.contribute_client(client)


class Client(object):

    def make_url(self, endpoint):
        raise NotImplementedError()

    def get(self, endpoint):
        r = requests.get(self.make_url(endpoint))
        return utilities.parse_response(r)

    def put(self, endpoint, json):
        r = requests.put(self.make_url(endpoint), json=json)
        return utilities.parse_response(r)



