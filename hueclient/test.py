import exceptions
from hueclient import utilities
from hueclient.api import Api, Client
from hueclient.models.bridge import Bridge
from hueclient.models.groups import Group
from hueclient.models.light import Light, LightState

hue_api = Api()
hue_api.register_resource(Bridge)
hue_api.register_resource(Light)
hue_api.register_resource(LightState)
hue_api.register_resource(Group)


class HueClient(Client):

    def __init__(self, bridge_host='philips-hue', username=None):
        username = username or utilities.load_username()
        if not username:
            raise exceptions.UsernameRequired('Username not specified and not found on disk')

        self.base_url = 'http://{bridge_host}/api/{username}'.format(**locals())

    def make_url(self, endpoint):
        return '{}/{}'.format(self.base_url, endpoint.lstrip('/'))


if __name__ == '__main__':

    client = HueClient()
    hue_api.set_client(client)
    bridge = Bridge.objects.get()
    
    print bridge.lights.count()

    print Light.objects.count()
    print Light.reachable.count()
    print Light.new.count()
    exit()

    for l in bridge.lights:
        state = l.state
        state.on = False
        # state.brightness = 100
        # state.color_temperature = 430
        state.save(client)

    current = 1
    previous = 0
    max = len(bridge.lights)
    while True:
        previous = current
        current += 1
        current %= 6
        print current, previous
        bridge.lights[current].state.on = True
        bridge.lights[previous].state.on = False
        bridge.lights[current].state.save(client)
        bridge.lights[previous].state.save(client)
        sleep(3)
