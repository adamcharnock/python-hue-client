from time import sleep
from hueclient.api import hue_api
from hueclient.models.groups import Group

if __name__ == '__main__':
    hue_api.authenticate_interactive(app_name='Blink Group Example')

    group = Group.objects.get(id=1)
    print("Blinking group named '{name}', control-c to exit".format(
        name=group.name
    ))
    while True:
        group.action.on = not group.action.on
        group.action.save()
        sleep(2)
