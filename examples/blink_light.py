from time import sleep
from hueclient.api import hue_api
from hueclient.models.light import Light

if __name__ == '__main__':
    hue_api.authenticate_interactive(app_name='Blink Light Example')

    light = Light.objects.get(id=1)
    print("Blinking light named '{name}', control-c to exit".format(
        name=light.name
    ))
    while True:
        light.state.on = not light.state.on
        light.state.save()
        sleep(2)
