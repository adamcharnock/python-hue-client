import weakref
from booby import Model, fields
from booby.models import ModelMeta


def make_endpoint(client, model):
    parent = model.parent_resource
    models = [model]
    while parent:
        models.append(parent)
        parent = parent.parent_resource

    values = {}
    for inst in models:
        for k in inst._fields:
            values['{}_{}'.format(inst.__class__.__name__.lower(), k)] = getattr(inst, k)

    return model.Meta.endpoint.format(**values)


class Manager(object):
    model = None

    def get(self, client, *args):
        endpoint = self.model.Meta.endpoint.format(*args)
        data = client.get(endpoint)
        decoded = self.model.decode(data)
        return self.model(**decoded)

    def contribute_to_class(self, model):
        self.model = model


class ResourceMetaclass(ModelMeta):

    def __new__(cls, clsname, bases, dct):
        resource = super(ResourceMetaclass, cls).__new__(cls, clsname, bases, dct)
        cls.setup_managers(resource, dct)
        return resource

    @classmethod
    def setup_managers(cls, resource, dct):
        # Setup any custom managers
        has_custom_manager = False
        for k, v in dct.items():
            if isinstance(k, Manager):
                v.contribute_to_class(resource)
                has_custom_manager = True

        # If we don't have a custom manager, then add the
        # default manager
        if not has_custom_manager:
            manager = Manager()
            manager.contribute_to_class(resource)
            resource.objects = manager


class Resource(Model):
    __metaclass__ = ResourceMetaclass

    parent_resource = None

    def __init__(self, **kwargs):
        # Only use fields which have been specified on the resource
        data = {}
        for f in self._fields.keys():
            # Get from kwargs is available, otherwise
            # get the default value from the current attribute value
            data[f] = kwargs.get(f) or getattr(self, f)

        super(Resource, self).__init__(**data)
        self.set_parent_values()
        self._persisted_data = self.encode()

    @classmethod
    def decode(self, raw):
        return super(Resource, self).decode(raw)

    def set_parent_values(self, parent=None):
        if parent:
            parent = weakref.proxy(parent)
        self.parent_resource = parent

        for k, v in self._fields.items():
            if isinstance(v, fields.Collection):
                for inst in getattr(self, k):
                    inst.set_parent_values(parent=self)
            elif isinstance(v, fields.Embedded):
                getattr(self, k).set_parent_values(parent=self)

    def prepare_save(self):
        encoded = self.encode()
        for k, v in encoded.items():
            if v == self._persisted_data[k]:
                encoded.pop(k)
        return encoded

    def save(self, client):
        endpoint = make_endpoint(client, self)
        client.put(endpoint, self.prepare_save())


class IndexedByIdDecoder(object):

    def __call__(self, value):
        decoded = []
        for k, v in value.items():
            v['id'] = k
            decoded.append(v)
        return decoded

