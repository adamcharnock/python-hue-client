from repose.managers import Manager
from repose.resources import Resource
from hueclient import fields
from hueclient.decoders import IndexedByIdDecoder
from hueclient import validators as v
from hueclient.monitor import MonitorMixin


class LightManager(Manager):

    def get_decoders(self):
        return self.decoders + [IndexedByIdDecoder()]

    def reachable(self):
        return self.filter(lambda light: light.state.reachable)


class LightState(MonitorMixin, Resource):
    MODE_HUE_SAT = 'hs'
    MODE_COLOR_TEMP = 'ct'
    MODE_XY = 'xy'

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
    color_mode = fields.String(v.In([MODE_HUE_SAT, MODE_COLOR_TEMP, MODE_XY]), name='colormode')
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
        endpoint = '/lights/{light_id}/state'

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
        self.color_mode = self.MODE_XY
        self._xy = xy

    @property
    def hue(self):
        """Hue of the light. This is a wrapping value between 0 and 65535.
        Both 0 and 65535 are red, 25500 is green and 46920 is blue."""
        return self._hue

    @hue.setter
    def hue(self, hue):
        self.color_mode = self.MODE_HUE_SAT
        self._hue = hue

    @property
    def saturation(self):
        """Saturation of the light. 254 is the most saturated (colored)
        and 0 is the least saturated (white)."""
        return self._saturation

    @saturation.setter
    def saturation(self, saturation):
        self.color_mode = self.MODE_HUE_SAT
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
        self.color_mode = self.MODE_COLOR_TEMP
        self._color_temperature = xy


class Light(MonitorMixin, Resource):
    #: The ID given to the light by the bridge
    id = fields.Integer(v.UnsignedInteger(), from_endpoint='id')
    #: A unique, editable name given to the light
    name = fields.String(v.Required())
    #: A fixed name describing the type of light e.g. "Extended color light"
    type = fields.String()
    #: The hardware model of the light
    model_id = fields.String(name='modelid')
    #: As of bridge version 1.7. The manufacturer name
    manufacturer_name = fields.String(name='manufacturername')
    #: As of bridge version 1.4. Unique id of the device.
    #: The MAC address of the device with a unique
    #: endpoint id in the form: AA:BB:CC:DD:EE:FF:00:11-XX
    unique_id = fields.String(name='uniqueid')
    #: An identifier for the software version running on the light.
    software_version = fields.String(name='swversion')

    #: The state of the light as a :class:`LightState` object
    state = fields.Embedded(LightState)

    #: A managed collection of all lights
    objects = LightManager()
    #: A managed collection of all lights which are reachable
    reachable = LightManager(filter=lambda light: light.state.reachable)
    #: A managed collection of all lights which are unreachable
    unreachable = LightManager(filter=lambda light: not light.state.reachable)
    #: A managed collection of all lights which are new
    new = LightManager(results_endpoint='/lights/new')

    class Meta:
        endpoint = '/lights/{id}'
        endpoint_list = '/lights'


# RGB -> XY conversion from: https://gist.github.com/error454/6b94c46d1f7512ffe5ee
# TODO: Seems buggy, needs work
def enhance_color(normalized):
    if normalized > 0.04045:
        return pow( (normalized + 0.055) / (1.0 + 0.055), 2.4)
    else:
        return normalized / 12.92


def rgb_to_xy(r, g, b):
    rNorm = r / 255.0
    gNorm = g / 255.0
    bNorm = b / 255.0

    rFinal = enhance_color(rNorm)
    gFinal = enhance_color(gNorm)
    bFinal = enhance_color(bNorm)

    X = rFinal * 0.649926 + gFinal * 0.103455 + bFinal * 0.197109
    Y = rFinal * 0.234327 + gFinal * 0.743075 + bFinal * 0.022598
    Z = rFinal * 0.000000 + gFinal * 0.053077 + bFinal * 1.035763

    if X + Y + Z == 0:
        return (0,0)
    else:
        xFinal = X / (X + Y + Z)
        yFinal = Y / (X + Y + Z)

        return (xFinal, yFinal)

