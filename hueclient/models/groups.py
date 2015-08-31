from booby import fields
from hueclient.models import Manager, Resource
from hueclient import validators as v


class GroupManager(Manager):
    pass


class Group(Resource):
    name = fields.String(v.Required())
    lights = fields.List()
