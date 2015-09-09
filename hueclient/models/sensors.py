from repose.managers import Manager
from repose.resources import Resource
from hueclient import fields
from hueclient.monitor import MonitorMixin


class Sensor(Resource):
    pass


class TapSwitchConfig(MonitorMixin, Resource):
    on = fields.Boolean()

    class Meta:
        endpoint = '/sensors/{tapswitch_id}/config'


class TapSwitchState(MonitorMixin, Resource):
    button_event = fields.Integer(name='buttonevent')
    last_updated = fields.IsoDate(name='lastupdated')

    class Meta:
        endpoint = '/sensors/{tapswitch_id}/state'


class TapSwitch(MonitorMixin, Resource):
    id = fields.Integer(from_endpoint='id')
    state = fields.Embedded(TapSwitchState)
    config = fields.Embedded(TapSwitchConfig)
    name = fields.String()
    type = fields.String()
    model_id = fields.String(name='modelid')
    manufacturer_name = fields.String(name='manufacturername')
    unique_id = fields.String(name='uniqueid')

    class Meta:
        endpoint = '/sensors/{id}'
        endpoint_list = '/sensors'
