from repose.managers import Manager
from repose.resources import Resource
from hueclient import fields
from hueclient.fields import ManagedIdListCollection
from hueclient.decoders import IndexedByIdDecoder
from hueclient import validators as v
from hueclient.models.light import Light, LightState, rgb_to_xy
from hueclient.monitor import MonitorMixin


class GroupState(MonitorMixin, Resource):
    """
    GroupState operates in the same way as :class:`LightState`
    except that it operates on a group of lights rather than an
    individual light. This can be a more effective way of
    controlling multiple lights rather than making API calls for
    each individual light.
    """

    #: On/Off state of the light. On=true, Off=false
    on = fields.Boolean()
    #: Brightness of the light. This is a scale from the minimum brightness
    #: the light is capable of, 1, to the maximum capable brightness, 254.
    brightness = fields.Integer(v.UnsignedInteger(bits=8), name='bri')
    _hue = fields.Integer(v.UnsignedInteger(bits=16))
    _saturation = fields.Integer(v.UnsignedInteger(bits=8), name='sat')
    _xy = fields.List(v.CieColorSpaceCoordinates())
    _color_temperature = fields.Integer(v.UnsignedInteger(bits=16), name='ct')
    #: The alert effect, which is a temporary change to the bulb's state
    #: (none/select/lselect).
    alert = fields.String(v.In(['none', 'select', 'lselect']))
    #: The dynamic effect of the light, can either be "none" or "colorloop".
    effect = fields.String(v.In(['none', 'select', 'lselect']))
    #: Indicates the color mode in which the light is working, this is
    #: the last command type it received. Values are "hs" for Hue and Saturation,
    #: "xy" for XY and "ct" for Color Temperature. Note that this will be
    #: set automatically upon setting the hue/saturation/xy/colour_temperature
    #: properties
    color_mode = fields.String(v.In([LightState.MODE_HUE_SAT, LightState.MODE_COLOR_TEMP, LightState.MODE_XY]), name='colormode')
    #: Indicates if a light can be reached by the bridge.
    reachable = fields.Boolean()

    # Write-only properties below...

    #: The duration of the transition from the light's current state to the
    #: new state. This is given as a multiple of 100ms.
    transition_time = fields.Integer(v.UnsignedInteger(bits=16), name='transitiontime')
    #: As of 1.7. Increments or decrements the value of the brightness.
    brightness_increment = fields.Integer(v.Integer(), v.Range(min=-254, max=254), name='bri_inc')
    #: As of 1.7. Increments or decrements the value of the sat.
    saturation_increment = fields.Integer(v.Integer(), v.Range(min=-254, max=254), name='sat_inc')
    #: As of 1.7. Increments or decrements the value of the hue.
    hue_increment = fields.Integer(v.Integer(), v.Range(min=-65534, max=65534), name='hue_inc')
    #: As of 1.7. Increments or decrements the value of the ct.
    color_temperature_increment = fields.Integer(v.Integer(), v.Range(min=-65534, max=65534), name='ct_inc')
    #: As of 1.7. Increments or decrements the value of the xy.
    xy_increment = fields.Integer(v.Float(), v.Range(min=-0.5, max=0.5), name='xy_inc')

    class Meta:
        endpoint = '/groups/{group_id}/action'

    def set_rgb(self, red, green, blue):
        """The red/green/blue color value of the light

        This will be converted and set as the :attr:`xy` value
        """
        x, y = rgb_to_xy(red, green, blue)
        self.xy = [x, y]

    @property
    def xy(self):
        """The x and y coordinates of a color in CIE color space.

        The first entry is the x coordinate and the second entry is the y coordinate. Both x and y are between 0 and 1.

        For more information see:
        http://www.developers.meethue.com/documentation/core-concepts#color_gets_more_complicated
        """
        return self._xy

    @xy.setter
    def xy(self, xy):
        self.color_mode = LightState.MODE_XY
        self._xy = xy

    @property
    def hue(self):
        """Hue of the light. This is a wrapping value between 0 and 65535.
        Both 0 and 65535 are red, 25500 is green and 46920 is blue."""
        return self._hue

    @hue.setter
    def hue(self, hue):
        self.color_mode = LightState.MODE_HUE_SAT
        self._hue = hue

    @property
    def saturation(self):
        """Saturation of the light. 254 is the most saturated (colored)
        and 0 is the least saturated (white)."""
        return self._saturation

    @saturation.setter
    def saturation(self, saturation):
        self.color_mode = LightState.MODE_HUE_SAT
        self._saturation = saturation

    @property
    def color_temperature(self):
        """The Mired Color temperature of the light.
        2012 connected lights are capable of 153 (6500K)
        to 500 (2000K).

        """
        return self._color_temperature

    @color_temperature.setter
    def color_temperature(self, xy):
        self.color_mode = LightState.MODE_COLOR_TEMP
        self._color_temperature = xy


class GroupManager(Manager):

    def get_decoders(self):
        return self.decoders + [IndexedByIdDecoder()]


class Group(MonitorMixin, Resource):
    #: The ID given to the group by the bridge
    id = fields.Integer(v.UnsignedInteger(), from_endpoint='id')
    #: A unique, editable name given to the group
    name = fields.String(v.Required())
    #: As of 1.4. If not provided upon creation "LightGroup" is used. Can
    #: be "LightGroup" or either "Luminiare" or "LightSource" if a
    #: Multisource Luminaire is present in the system.
    type = fields.String(read_only=True)
    #: The Light resources contained with this group
    lights = ManagedIdListCollection(model=Light)
    action = fields.Embedded(model=GroupState)

    objects = GroupManager()

    class Meta:
        endpoint = '/groups/{id}'
        endpoint_list = '/groups'
