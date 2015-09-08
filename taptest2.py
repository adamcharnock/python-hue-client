from hueclient.api import hue_api
from hueclient.models.sensors import TapSwitch, TapSwitchState

if __name__ == '__main__':
    switch = TapSwitch.objects.get(id=3)

    def handle(resource, field, previous, current):
        print "Change from {} to {}".format(previous, current)

    switch.monitor(lambda sw: sw.state.button_event, handle, poll_interval=0.2)
    hue_api.start_monitor_loop()
