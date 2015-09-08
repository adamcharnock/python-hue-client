from repose.managers import Manager
from repose.resources import Resource
from hueclient import fields
from hueclient.models import IndexedByIdDecoder
from hueclient import validators as v


class LightManager(Manager):

    def get_decoders(self):
        return self.decoders + [IndexedByIdDecoder()]

    def reachable(self):
        return self.filter(lambda light: light.state.reachable)


class LightState(Resource):
    MODE_HUE_SAT = 'hs'
    MODE_COLOR_TEMP = 'ct'
    MODE_XY = 'xy'

    on = fields.Boolean()
    brightness = fields.Integer(v.UnsignedInteger(bits=8), name='bri')
    _hue = fields.Integer(v.UnsignedInteger(bits=16))
    _saturation = fields.Integer(v.UnsignedInteger(bits=8), name='sat')
    effect = fields.String(v.In(['none', 'select', 'lselect']))
    _xy = fields.List(v.CieColorSpaceCoordinates())
    _color_temperature = fields.Integer(v.UnsignedInteger(bits=16), name='ct')
    alert = fields.String(v.In(['none', 'select', 'lselect']))
    color_mode = fields.String(v.In([MODE_HUE_SAT, MODE_COLOR_TEMP, MODE_XY]), name='colormode')
    reachable = fields.Boolean()

    # Write-only properties
    transition_time = fields.Integer(v.UnsignedInteger(bits=16), name='transitiontime')
    brightness_increment = fields.Integer(v.Integer(), v.Range(min=-254, max=254), name='bri_inc')
    saturation_increment = fields.Integer(v.Integer(), v.Range(min=-254, max=254), name='sat_inc')
    hue_increment = fields.Integer(v.Integer(), v.Range(min=-65534, max=65534), name='hue_inc')
    color_temperature_increment = fields.Integer(v.Integer(), v.Range(min=-65534, max=65534), name='ct_inc')
    xy_increment = fields.Integer(v.Float(), v.Range(min=-0.5, max=0.5), name='xy_inc')

    class Meta:
        endpoint = '/lights/{light_id}/state'

    def set_rgb(self, red, green, blue):
        x, y = rgb_to_xy(red, green, blue)
        self.xy = [x, y]

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, xy):
        self.color_mode = self.MODE_XY
        self._xy = xy

    @property
    def hue(self):
        return self._hue

    @hue.setter
    def hue(self, hue):
        self.color_mode = self.MODE_HUE_SAT
        self._hue = hue

    @property
    def saturation(self):
        return self._saturation

    @saturation.setter
    def saturation(self, saturation):
        self.color_mode = self.MODE_HUE_SAT
        self._saturation = saturation

    @property
    def color_temperature(self):
        return self._color_temperature

    @color_temperature.setter
    def color_temperature(self, xy):
        self.color_mode = self.MODE_COLOR_TEMP
        self._color_temperature = xy


class Light(Resource):
    id = fields.Integer(v.UnsignedInteger())
    name = fields.String(v.Required())
    type = fields.String()
    model_id = fields.String(name='modelid')
    manufacturer_name = fields.String(name='manufacturername')
    unique_id = fields.String(name='uniqueid')
    software_version = fields.String(name='swversion')

    state = fields.Embedded(LightState)

    objects = LightManager()
    reachable = LightManager(filter=lambda light: light.state.reachable)
    unreachable = LightManager(filter=lambda light: not light.state.reachable)
    new = LightManager(results_endpoint='/lights/new')

    class Meta:
        endpoint = '/lights/{light_id}'
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

