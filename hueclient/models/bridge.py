from repose.resources import Resource
from hueclient import fields
from hueclient.decoders import IndexedByIdDecoder
from hueclient.models.light import Light
from hueclient.monitor import MonitorMixin


class Bridge(MonitorMixin, Resource):
    lights = fields.ManagedCollection(Light, decoders=[IndexedByIdDecoder()])

    class Meta:
        endpoint = '/'
