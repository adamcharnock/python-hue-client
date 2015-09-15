from repose.managers import Manager
from repose.resources import Resource
from hueclient import fields
from booby import validators as v
from hueclient.decoders import IndexedByIdDecoder
from hueclient.monitor import MonitorMixin


class ScheduleManager(Manager):

    def get_decoders(self):
        return self.decoders + [IndexedByIdDecoder()]


class Command(MonitorMixin, Resource):
    #: The address to call (without protcol or domain). Eg:
    #: ``/api/<username>/groups/0/action``
    address = fields.String(v.Required())
    #: The body of the request
    body = fields.Dictionary()
    #: The HTTP request method
    method = fields.String(v.In(['GET', 'PUT', 'POST', 'DELETE']))


class Schedule(MonitorMixin, Resource):
    #: The name of the schedule.
    name = fields.String(v.Required())
    #: Description of the schedule
    description = fields.String()
    #: Command to execute when the scheduled event occurs
    command = fields.Embedded(Command)
    #: Local time when the scheduled event will occur
    local_time = fields.TimePattern(name='localtime')
    #: Status, either 'enabled' or 'disabled'
    status = fields.String(v.In(['enabled', 'disabled']))
    #: If set to true, the schedule will be removed automatically if expired,
    #: if set to false it will be disabled. Default is true.
    auto_delete = fields.Boolean(name='autodelete')
    #: UTC time that the timer was started. Only provided for timers.
    start_time = fields.IsoDate(name='starttime', read_only=True)
