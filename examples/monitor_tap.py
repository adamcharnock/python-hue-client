from hueclient.api import hue_api
from hueclient.models.sensors import TapSwitch

if __name__ == '__main__':
    def handle(resource, field, previous, current):
        print "Change from {} to {}".format(previous, current)

    hue_api.authenticate_interactive(app_name='Tap Test')

    # Ask the user which switch we want to monitor
    for tap in TapSwitch.objects.all():
        print("Switch {id}: {name}".format(**tap.as_dict()))

    # Get the switch
    switch_id = raw_input("Enter switch ID to monitor: ")
    switch = TapSwitch.objects.get(id=switch_id)

    # Setup the monitoring as follows:
    #  - Any time the switch's state changes call handle()
    #  - Check for a change every 0.2 seconds
    switch.monitor(lambda sw: sw.state.as_dict(), handle, poll_interval=0.2)

    # Start the monitoring
    print("Starting monitoring. Control-c to exit.")
    hue_api.start_monitor_loop()
    # Execution will never pass this point
