from hueclient import utilities, exceptions
from hueclient.api import Api, Client
from hueclient.models.bridge import Bridge
from hueclient.models.groups import Group
from hueclient.models.light import Light, LightState


class HueApi(Api):
    resources = [
        Bridge,
        Light,
        LightState,
        Group,
    ]

    def __init__(self, bridge_host='philips-hue', username=None):
        self.bridge_host = bridge_host
        self.username = username or utilities.load_username()
        if not self.username:
            raise exceptions.UsernameRequired('Username not specified and not found on disk')
        super(HueApi, self).__init__()

    def get_base_url(self):
        return 'http://{bridge_host}/api/{username}'.format(
            bridge_host=self.bridge_host,
            username=self.username,
        )

hue_api = HueApi()


if __name__ == '__main__':

    bridge = Bridge.objects.get()

    print bridge.lights.count()

    print Light.objects.count()
    print Light.reachable.count()
    print Light.new.count()

    print Group.objects.all()
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
