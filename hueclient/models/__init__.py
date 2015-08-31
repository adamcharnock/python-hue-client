import weakref
from booby import Model, fields
from booby.models import ModelMeta


def make_endpoint(model):
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
    results = None
    results_endpoint = None

    def __init__(self, decoders=None, results_endpoint=None, filter=None):
        self.decoders = decoders or []
        self.results_endpoint = results_endpoint
        self.filter_fn = filter

    def get(self, **endpoint_params):
        """Get a single model"""
        endpoint = self.model.Meta.endpoint.format(**endpoint_params)
        data = self.client.get(endpoint)
        decoded = self.model.decode(data)
        return self.model(**decoded)

    def _load_results(self):
        """Load all the results for this manager"""
        if self.results is not None:
            return
        data = self.client.get(self.get_results_endpoint())
        for decoder in self.get_decoders():
            data = decoder(data)
        self.results = [self.model(**d) for d in data]

    def get_decoders(self):
        return self.decoders

    def get_results_endpoint(self):
        return self.results_endpoint or self.model.Meta.endpoint_list

    def contribute_to_class(self, model):
        self.model = model

    @classmethod
    def contribute_client(cls, client):
        cls.client = client

    def filter(self, results):
        if self.filter_fn:
            return filter(self.filter_fn, results)
        else:
            return results

    def all(self):
        self._load_results()
        return self.filter(self.results)

    def __iter__(self):
        return iter(self.all())

    def count(self):
        return len(self.all())


class ResourceMetaclass(ModelMeta):

    def __new__(cls, clsname, bases, dct):
        resource = super(ResourceMetaclass, cls).__new__(cls, clsname, bases, dct)
        cls.setup_managers(resource, dct)
        return resource

    @classmethod
    def setup_managers(cls, resource, dct):
        # Setup any custom managers
        has_custom_manager = False
        managers = []
        for k, v in dct.items():
            if isinstance(v, Manager):
                v.contribute_to_class(resource)
                has_custom_manager = True
                managers.append(v)

        # If we don't have a custom manager, then add the
        # default manager
        if not has_custom_manager:
            manager = Manager()
            manager.contribute_to_class(resource)
            resource.objects = manager
            managers.append(manager)

        resource._managers = managers


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

    @classmethod
    def contribute_client(cls, client):
        cls.client = client
        for manager in cls._managers:
            manager.contribute_client(client)

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

    def save(self):
        endpoint = make_endpoint(self)
        self.client.put(endpoint, self.prepare_save())


class IndexedByIdDecoder(object):

    def __call__(self, value):
        decoded = []
        for k, v in value.items():
            try:
                k = int(k)
            except (ValueError, TypeError):
                continue
            v['id'] = k
            decoded.append(v)
        return decoded

