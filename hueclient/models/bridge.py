from hueclient import fields
from hueclient.models import Resource, IndexedByIdDecoder
from hueclient.models.light import Light


class Bridge(Resource):
    lights = fields.ManagedCollection(Light, decoders=[IndexedByIdDecoder()])

    class Meta:
        endpoint = '/'
