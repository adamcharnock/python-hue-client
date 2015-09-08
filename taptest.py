import requests
import eventlet

from hueclient.api import hue_api
from hueclient.models.sensors import TapSwitch


def monitor_switch(queue, username, switch_id):
    last_state = None
    while True:
        switch = TapSwitch.objects.get(username=username, tapswitch_id=switch_id)
        current_state = switch.state.as_dict()

        if not last_state:
            last_state = current_state

        if last_state != current_state:
            last_state = current_state
            queue.put(switch)
        eventlet.sleep(0.1)


def handle(event):
    print event


def loop():
        username = 'fa6204638b67ba73aa617aa26df60db'
        poll_pool = eventlet.GreenPool()
        handler_pool = eventlet.GreenPool()
        event_queue = eventlet.Queue()
        poll_pool.spawn_n(monitor_switch, event_queue, username, switch_id=2)
        poll_pool.spawn_n(monitor_switch, event_queue, username, switch_id=3)

        while True:
            event = event_queue.get()
            handler_pool.spawn_n(handle, event)


if __name__ == '__main__':
    loop()
