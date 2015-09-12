from pprint import pprint
from hueclient.api import hue_api
from hueclient.models.light import Light

if __name__ == '__main__':
    hue_api.authenticate_interactive(app_name='List Lights Example')

    # Show a summary of all lights first
    for light in Light.objects.all():
        print(
            "Light {id} is named '{name}' and is {onoff} (brightness: {brightness})".format(
                id=light.id,
                name=light.name,
                onoff='on' if light.state.on else 'off',
                brightness=light.state.brightness,
            )
        )

    while True:
        # Let's offer the user some more detailed information
        light_id = raw_input("Enter a light ID for more information (enter to exit): ")
        if not light_id:
            print('Bye!')
            exit()

        # Get the light using the specified ID
        light = Light.objects.get(id=light_id)

        # Get the information as a dictionary using as_dict()
        light_as_dict = light.as_dict()
        light_as_dict['state'] = light.state.as_dict()

        # Prettily print it
        pprint(light_as_dict)
