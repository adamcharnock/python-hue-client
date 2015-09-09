from repose.managers import Manager
from repose.resources import Resource
from hueclient import fields
from booby import validators as v
from hueclient.models import IndexedByIdDecoder
from hueclient.monitor import MonitorMixin


class ScheduleManager(Manager):

    def get_decoders(self):
        return self.decoders + [IndexedByIdDecoder()]


class Command(MonitorMixin, Resource):
    address = fields.String(v.Required())
    body = fields.Dictionary()
    local_time = fields.TimePattern(name='localtime')
    status = fields.String(v.In(['enabled', 'disabled']))
    auto_delete = fields.Boolean(name='autodelete')
    starttime = fields.IsoDate()


class Schedule(MonitorMixin, Resource):
    name = fields.String(v.Required())
    description = fields.Embedded(Command)
