from repose.resources import Resource
from hueclient import fields
from hueclient.models import IndexedByIdDecoder
from hueclient.models.light import Light


class Bridge(Resource):
    lights = fields.ManagedCollection(Light, decoders=[IndexedByIdDecoder()])

    class Meta:
        endpoint = '/'
