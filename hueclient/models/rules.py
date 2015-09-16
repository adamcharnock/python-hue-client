from repose import Manager, Resource
from hueclient import fields
from hueclient.decoders import IndexedByIdDecoder
from hueclient.monitor import MonitorMixin
from hueclient import validators as v


class Condition(Resource):
    #: Operator constant - value is equal to the specified ``value`` field.
    OP_EQUAL = 'eq'
    #: Operator constant - value is greater than the specified ``value``
    #: field. Only available for integer values.
    OP_GREATER = 'gt'
    #: Operator constant - value is less than the specified ``value`` field.
    #: Only available for integer values.
    OP_LESS = 'lt'
    #: Operator constant - value is different to the specified ``value`` field.
    OP_DIFF = 'dx'

    #: Path to an attribute of a sensor resource.
    address = fields.String()
    #: eq, gt, lt or dx (equals, greater than, less than or value has changed)
    operator = fields.String(v.In([OP_EQUAL, OP_GREATER, OP_LESS, OP_DIFF]))
    #: The resource attribute is compared to this value using the given
    #: operator. The value is cast to the data type of the resource attribute
    #: (in case of time, casted to a timePattern).
    value = fields.String()


class Action(Resource):
    #: The address to call (without protocol or domain). Eg:
    #: ``/api/<username>/groups/0/action``
    address = fields.String(v.Required())
    #: The body of the request
    body = fields.Dictionary()
    #: The HTTP request method
    method = fields.String(v.In(['GET', 'PUT', 'POST', 'DELETE']))


class RuleManager(Manager):

    def get_decoders(self):
        return self.decoders + [IndexedByIdDecoder()]


class Rule(MonitorMixin, Resource):
    #: The name of the rule. May me customised, but is often auto-generated,
    name = fields.String()
    #: The owner of this rule (meaning currently unclear)
    owner = fields.String()
    #: Date the rule was last triggered
    last_triggered = fields.IsoDate(name='lasttriggered')
    #: Date the rule was created
    creation_time = fields.IsoDate(name='creationtime')
    #: The number of times this rule has been triggered
    times_triggered = fields.Integer(name='timestriggered')
    #: A collection of :class:`Condition` resources. The ``actions`` will
    #: only be run if all conditions evaluate to true.
    conditions = fields.ManagedCollection(Condition)
    #: A collection of :class:`Action` resources
    actions = fields.ManagedCollection(Action)

    objects = RuleManager()

    class Meta:
        endpoint = '/rules/{id}'
        endpoint_list = '/rules'
