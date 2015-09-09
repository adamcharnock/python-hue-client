from repose.managers import Manager
from repose.resources import Resource
from hueclient import fields
from hueclient.fields import ManagedIdListCollection
from hueclient.models import IndexedByIdDecoder
from hueclient import validators as v
from hueclient.models.light import Light
from hueclient.monitor import MonitorMixin


class GroupManager(Manager):

    def get_decoders(self):
        return self.decoders + [IndexedByIdDecoder()]


class Group(MonitorMixin, Resource):
    id = fields.Integer(v.UnsignedInteger(), from_endpoint='id')
    name = fields.String(v.Required())
    lights = ManagedIdListCollection(model=Light)

    objects = GroupManager()

    class Meta:
        endpoint = '/groups/{id}'
        endpoint_list = '/groups'
