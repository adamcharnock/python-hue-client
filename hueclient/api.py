from repose.api import Api
from repose.apibackend import ApiBackend

from hueclient import utilities, exceptions
from hueclient.models.bridge import Bridge
from hueclient.models.groups import Group, GroupState
from hueclient.models.light import Light, LightState
from hueclient.models.sensors import TapSwitch, TapSwitchConfig, TapSwitchState
from hueclient.utilities import authenticate, authenticate_interactive


class HueApiBackend(ApiBackend):
    def parse_response(self, response):
        return utilities.parse_response(response)


class HueApi(Api):
    resources = [
        Bridge,
        Light,
        LightState,
        Group,
        GroupState,
        TapSwitch,
        TapSwitchConfig,
        TapSwitchState,
    ]
    backend_class = HueApiBackend

    def __init__(self, bridge_host='philips-hue', username=None, poll_interval=0.1):
        self.bridge_host = bridge_host
        self.username = username or utilities.load_username()
        self.poll_interval = poll_interval
        if not self.username:
            raise exceptions.UsernameRequired('Username not specified and not found on disk')
        super(HueApi, self).__init__()

    def get_base_url(self):
        return 'http://{bridge_host}/api/{username}'.format(
            bridge_host=self.bridge_host,
            username=self.username,
        )
    
    def authenticate(self, app_name, bridge_host='philips-hue', client_name=None):
        return authenticate(app_name, bridge_host, client_name)
    
    def authenticate_interactive(self, app_name, bridge_host='philips-hue', client_name=None):
        return authenticate_interactive(app_name, bridge_host, client_name)

    def handle_event(self, callback, *args):
        self.handler_pool.spawn_n(callback, *args)

    def start_monitor_loop(self):
        while True:
            event = self.event_queue.get()
            self.handle_event(*event)

    def _get_pool(self):
        from eventlet import GreenPool
        return GreenPool()

    def _get_queue(self):
        from eventlet import Queue
        return Queue()

    @property
    def poll_pool(self):
        if not hasattr(self, '_poll_pool'):
            self._poll_pool = self._get_pool()
        return self._poll_pool

    @property
    def handler_pool(self):
        if not hasattr(self, '_handler_pool'):
            self._handler_pool = self._get_pool()
        return self._handler_pool

    @property
    def event_queue(self):
        if not hasattr(self, '_event_queue'):
            self._event_queue = self._get_queue()
        return self._event_queue




hue_api = HueApi()
