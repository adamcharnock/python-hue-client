from booby import fields
from hueclient.models import Manager, Resource


class LightManager(Manager):

    def new(self):
        pass


class LightState(Resource):
    on = fields.Boolean()
    bri = fields.Integer()
    hue = fields.Integer()
    sat = fields.Integer()
    effect = fields.Integer()
    xy = fields.List()
    ct = fields.Integer()
    alert = fields.String()
    colormode = fields.String()
    reachable = fields.Boolean()

    class Meta:
        endpoint = '/lights/{light_id}/state'


class Light(Resource):
    id = fields.Integer()
    name = fields.String()
    type = fields.String()
    modelid = fields.String()
    manufacturername = fields.String()
    uniqueid = fields.String()
    swversion = fields.String()

    state = fields.Embedded(LightState)

    class Meta:
        endpoint = '/lights/{}'
        endpoint_list = '/lights'


