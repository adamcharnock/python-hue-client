from unittest.case import TestCase
from repose.exceptions import LinkButtonNotPressed


class AuthenticateTestCase(TestCase):

    def setUp(self):
        from repose.tests import TestApi
        self.api = TestApi()
        self.client = self.api.client

    def test_ok(self):
        from repose.utilities import authenticate
        self.client.add_response('POST', '/api', [{
            'success': {'username': 'newusername'}
        }])
        response = authenticate(self.client, 'test-app', 'test-client')
        self.assertEqual(response, 'newusername')

    def test_error(self):
        from repose.utilities import authenticate
        self.client.add_response('POST', '/api', [{
            'error': {
                'type': 101,
                'address': '',
                'description': 'link button not pressed',
            }
        }])
        self.assertRaises(LinkButtonNotPressed, authenticate,
                          self.client, 'test-app', 'test-client')
