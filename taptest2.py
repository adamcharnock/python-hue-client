from hueclient.api import hue_api
from hueclient.models.light import Light
from hueclient.models.sensors import TapSwitch, TapSwitchState

if __name__ == '__main__':
    def handle(resource, field, previous, current):
        print "Change from {} to {}".format(previous, current)

    switch = TapSwitch.objects.get(id=3)
    switch.monitor(lambda sw: sw.state.as_dict(), handle, poll_interval=0.2)

    light = Light.objects.get(id=1)
    light.monitor(lambda l: l.state.on, handle, poll_interval=0.2)

    hue_api.start_monitor_loop()
