from repose.api import Api

from hueclient import utilities, exceptions
from hueclient.models.bridge import Bridge
from hueclient.models.groups import Group
from hueclient.models.light import Light, LightState
from hueclient.models.sensors import TapSwitch, TapSwitchConfig, TapSwitchState


class HueApi(Api):
    resources = [
        Bridge,
        Light,
        LightState,
        Group,
        TapSwitch,
        TapSwitchConfig,
        TapSwitchState,
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
