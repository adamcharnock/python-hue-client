from repose.managers import Manager
from repose.resources import Resource
from hueclient import fields

class Sensor(Resource):
    pass


class TapSwitchConfig(Resource):
    on = fields.Boolean()

    class Meta:
        endpoint = '/sensors/{tapswitch_id}/config'


class TapSwitchState(Resource):
    button_event = fields.Integer(name='buttonevent')
    last_updated = fields.IsoDate(name='lastupdated')

    class Meta:
        endpoint = '/sensors/{tapswitch_id}/state'


class TapSwitch(Resource):
    id = fields.Integer()
    state = fields.Embedded(TapSwitchState)
    config = fields.Embedded(TapSwitchConfig)
    name = fields.String()
    type = fields.String()
    model_id = fields.String(name='modelid')
    manufacturer_name = fields.String(name='manufacturername')
    unique_id = fields.String(name='uniqueid')

    class Meta:
        endpoint = '/sensors/{tapswitch_id}'
        endpoint_list = '/sensors'
