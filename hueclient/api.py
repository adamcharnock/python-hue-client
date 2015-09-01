import requests

import exceptions
from hueclient import utilities


class Client(object):
    """The HTTP client used to access the remote API

    This can be extended and passed into your :class:`Api`
    instance at instantiation time.
    """

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
    """ A top-level API representation

    Initialising an ``Api`` instance is a necessary step as
    doing so will furnish all registered Resources (and their Managers)
    with access to the API client.

    For example::

        my_api = Api(base_url='http://example.com/api/v1')
        my_api.register_resource(User)
        my_api.register_resource(Comment)
        my_api.register_resource(Page)

    The same can be achieved by implementing a child class. This also
    gives the additional flexibility of being able to add more complex
    logic by overriding existing methods. For example::

        class MyApi(Api):
            # Alternative way to provide base_url and resources
            base_url = '/api/v1'
            resources = [User, Comment, Page]

            # Additionally, customise the base URL generation
            def get_base_url(self):
                return 'http://{host}/api/{account}'.format(
                    host=self.host,
                    account=self.account,
                )

        my_api = MyApi(host='myhost.com', account='my-account')

    .. note: All options passed to the Api's constructor will become
             available as instance variables. See the able example and
             the use of ``account``.
    """

    client_class = Client
    base_url = None
    resources = []

    def __init__(self, **options):
        for k, v in options.items():
            setattr(self, k, v)

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




