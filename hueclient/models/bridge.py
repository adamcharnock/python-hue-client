from booby import fields
from hueclient.models import Resource, IndexedByIdDecoder
from hueclient.models.light import Light


class Bridge(Resource):
    moo = fields.String(default='abc')
    lights = fields.Collection(Light, decoders=[IndexedByIdDecoder()])

    class Meta:
        endpoint = '/'
