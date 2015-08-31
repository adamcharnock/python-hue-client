from booby import fields
from hueclient.models import Manager, Resource


class LightManager(Manager):

    def new(self):
        pass


class LightState(Resource):
    on = fields.Boolean()
    brightness = fields.Integer(name='bri')
    _hue = fields.Integer()
    _saturation = fields.Integer(name='sat')
    effect = fields.Integer()
    _xy = fields.List()
    _color_temperature = fields.Integer(name='ct')
    alert = fields.String()
    color_mode = fields.String(name='colormode')
    reachable = fields.Boolean()

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
        self.color_mode = 'xy'
        self._xy = xy

    @property
    def hue(self):
        return self._hue

    @hue.setter
    def hue(self, hue):
        self.color_mode = 'hs'
        self._hue = hue

    @property
    def saturation(self):
        return self._saturation

    @saturation.setter
    def saturation(self, saturation):
        self.color_mode = 'hs'
        self._saturation = saturation

    @property
    def color_temperature(self):
        return self._color_temperature

    @color_temperature.setter
    def color_temperature(self, xy):
        self.color_mode = 'ct'
        self._color_temperature = xy




class Light(Resource):
    id = fields.Integer()
    name = fields.String()
    type = fields.String()
    model_id = fields.String(name='modelid')
    manufacturer_name = fields.String(name='manufacturername')
    unique_id = fields.String(name='uniqueid')
    software_version = fields.String(name='swversion')

    state = fields.Embedded(LightState)

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

