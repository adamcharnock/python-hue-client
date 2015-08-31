from booby import fields
from hueclient.fields import ManagedIdListCollection
from hueclient.models import Manager, Resource, IndexedByIdDecoder
from hueclient import validators as v
from hueclient.models.light import Light


class GroupManager(Manager):

    def get_decoders(self):
        return self.decoders + [IndexedByIdDecoder()]


class Group(Resource):
    id = fields.Integer(v.UnsignedInteger())
    name = fields.String(v.Required())
    lights = ManagedIdListCollection(model=Light)

    objects = GroupManager()

    class Meta:
        endpoint = '/groups/{group_id}'
        endpoint_list = '/groups'
