from booby import fields
from hueclient.fields import ManagedCollection
from hueclient.models import Resource, IndexedByIdDecoder
from hueclient.models.light import Light


class Bridge(Resource):
    moo = fields.String(default='abc')
    lights = ManagedCollection(Light, decoders=[IndexedByIdDecoder()])

    class Meta:
        endpoint = '/'
