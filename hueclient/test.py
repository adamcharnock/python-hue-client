from hueclient.api import Connection, hue_client
from hueclient.models.bridge import Bridge
from hueclient.models.light import Light

if __name__ == '__main__':

    connection = Connection()
    hue_client.register_connection(connection)
    # bridge = Bridge.objects.get(client)
    # print bridge.lights

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
