from repose import fields
from repose.managers import Manager
from repose.resources import Resource
from hueclient.decoders import IndexedByIdDecoder
from hueclient.models.light import Light
from hueclient.monitor import MonitorMixin
from hueclient import validators as v


class SceneManager(Manager):
    def get_decoders(self):
        return self.decoders + [IndexedByIdDecoder(type=str)]

    def get(self, **kwargs):
        # One cannot retrieve a specific scene, so retrieve
        # all of them and filter manually
        for scene in self.all():
            matches = True
            for k, v in kwargs.items():
                if getattr(scene, k) != v:
                    matches = False
            if matches:
                return scene


class Scene(MonitorMixin, Resource):
    """
    Note that scene state is not available on this resource
    as scene state is write-only. See :class:`SceneStateChange` for details.
    """

    #: The ID given to the scene by the bridge (alphanumeric, Eg: `s123457`)
    id = fields.Integer(v.UnsignedInteger(), from_endpoint='id')
    #: An editable name given to the scene
    name = fields.String(v.Required())
    #: The Light resources effected by this scene
    lights = fields.ManagedIdListCollection(model=Light)
    #: Is this scene active?
    active = fields.Boolean()

    objects = SceneManager()

    class Meta:
        endpoint = '/scenes/{id}'
        endpoint_list = '/scenes'


class SceneStateChange(Resource):
    """
    ``SceneStateChange`` work differently to :class:`LightState` and
    :class:`GroupState`. ``SceneStateChange`` specifies a change in
    state for a specific scene & light combination.

    For example, to change light ID 1 in scene `e2eab6bf6-on-0` to `on`::

        change = SceneStateChange(
            scene=Scene.objects.get(id='e2eab6bf6-on-0'),
            light=Light.objects.get(id=1),
        )
        change.on = True
        change.save()

    """

    #: The scene to which this change applies
    scene = fields.Embedded(model=Scene, read_only=True)
    #: The light to which this scene applies
    light = fields.Embedded(model=Light, read_only=True)
    #: On/Off state of the light. On=true, Off=false
    on = fields.Boolean()
    #: Brightness of the light. This is a scale from the minimum brightness
    #: the light is capable of, 1, to the maximum capable brightness, 254.
    brightness = fields.Integer(v.UnsignedInteger(bits=8), name='bri')
    #: The hue value is a wrapping value between 0 and 65535.
    #: Both 0 and 65535 are red, 25500 is green and 46920 is blue.
    hue = fields.Integer(v.UnsignedInteger(bits=16))
    #: Saturation of the light. 255 is the most saturated (colored) and 0
    #: is the least saturated (white).
    saturation = fields.Integer(v.UnsignedInteger(bits=8), name='sat')
    #: The x and y coordinates of a color in CIE color space.
    xy = fields.List(v.CieColorSpaceCoordinates())
    #: The Mired Color temperature of the light. 2012 connected lights are
    #: capable of 153 (6500K) to 500 (2000K).
    color_temperature = fields.Integer(v.UnsignedInteger(bits=16), name='ct')
    #: The duration of the transition from the light's current state to the
    #: new state. This is given as a multiple of 100ms.
    transition_time = fields.Integer(v.UnsignedInteger(bits=16), name='transitiontime')

    class Meta:
        endpoint = '/scenes/{scene_id}/lights/{light_id}/state'

    def get_endpoint_values(self):
        return {
            'scene_id': self.scene.id,
            'light_id': self.light.id,
        }
