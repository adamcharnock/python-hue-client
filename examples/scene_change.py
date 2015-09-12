from hueclient.api import hue_api
from hueclient.models.light import Light
from hueclient.models.scenes import SceneStateChange, Scene

if __name__ == '__main__':
    hue_api.authenticate_interactive(app_name='List Lights Example')

    # SceneStateChange is write-only. We can therefore
    # not do the usual retrieve-then-edit process.
    # Therefore instantiate the resource here, make the changes,
    # then save it.
    change = SceneStateChange(
        scene=Scene.objects.get(id='e2eab6bf6-on-0'),
        light=Light.objects.get(id=1),
    )
    change.on = True
    change.save()
