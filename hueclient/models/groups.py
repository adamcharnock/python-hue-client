from booby import fields
from hueclient.models import Manager, Resource, IndexedByIdDecoder
from hueclient import validators as v


class GroupManager(Manager):

    def get_decoders(self):
        return self.decoders + [IndexedByIdDecoder()]


class Group(Resource):
    name = fields.String(v.Required())
    lights = fields.List()

    objects = GroupManager()

    class Meta:
        endpoint = '/groups/{group_id}'
        endpoint_list = '/groups'
