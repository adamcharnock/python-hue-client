from siesta import API
from hueclient import utilities, exceptions





class ResourceContainer(object):
    resources = {}
    collections = {}

    def _make_resource(self, resource):
        pass

    def _make_collection(self):
        pass

    def __getattr__(self, name):
        if name in self.resources:
            return self._make_resource(self.resources['name'])
        elif name in self.collections:
            return self._make_collection(self.collections['name'])
        else:
            raise AttributeError()


class HueApi(API):

    def __init__(self, bridge_host='philips-hue', username=None):
        username = username or utilities.load_username()
        if not username:
            raise exceptions.UsernameRequired('Username not specified and not found on disk')

        super(HueApi, self).__init__(
            base_url='http://{bridge_host}/api/{username}'.format(**locals())
        )




if __name__ == '__main__':
    api = HueApi()
    import pdb; pdb.set_trace()

