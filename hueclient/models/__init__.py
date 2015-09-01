import weakref
from booby import Model, fields
from booby.decoders import Decoder
from booby.models import ModelMeta
from hueclient.fields import ManagedCollection


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
        """Get a single model

        :param endpoint_params: dict Parameters which should be used to format the
                                     ``Meta.endpoint`` string
        """
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
        self.results = [self.model(**self.model.decode(d)) for d in data]

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
    """ Meta class for setting up Resource classes
    """

    def __new__(cls, clsname, bases, dct):
        resource = super(ResourceMetaclass, cls).__new__(cls, clsname, bases, dct)
        cls.setup_managers(resource, dct)
        return resource

    @classmethod
    def setup_managers(cls, resource, dct):
        """Setup the managers on a resource

        Pass a reference to the resource class to all attached managers,
        and create a default manager if none are explicitly defined
        """
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
    """ Representation of an API resource

    :ivar parent_resource:
        A list of all parent resources to this one. Often useful in
        generating endpoints for child resources. Parent resources are
        stored as :py:func:`weakref.ref`
    """
    __metaclass__ = ResourceMetaclass

    class Meta:
        """ Override this class in child resources to provide
            configuration details.
        """
        pass

    def __init__(self, **kwargs):
        self.parent_resource = []
        # Only use fields which have been specified on the resource
        data = {}
        for f in self._fields.keys():
            # Get from kwargs is available, otherwise
            # get the default value from the current attribute value
            data[f] = kwargs.get(f) or getattr(self, f)

        super(Resource, self).__init__(**data)
        self.contribute_parents()
        self._persisted_data = self.encode()


    @classmethod
    def contribute_client(cls, client):
        """Contribute the API client to this resource and its managers"""
        cls.client = client
        for manager in cls._managers:
            manager.contribute_client(client)

    def contribute_parents(self, parent=None):
        """Furnish this class with it's parent resources"""
        if parent:
            parent = weakref.proxy(parent)
        self.parent_resource = parent

        for k, v in self._fields.items():
            if hasattr(v, 'contribute_parent_to_models'):
                # This is a ManagedCollection of some sort, so
                # let it handle contributing to its models
                v.contribute_parent_to_models(parent=self)
            elif hasattr(getattr(self, k), 'contribute_parents'):
                # This is an Embedded field of some sort. The
                # value attached to the resource will be another
                # resource, so directly contribute to its parents
                getattr(self, k).contribute_parents(parent=self)

    def prepare_save(self, encoded):
        """Prepare the resource to be saved

        Will only return values which have changed

        Can be used as a hook with which to tweak data before
        sending back to the server. For example::

            def prepare_save(encoded):
                prepared = super(MyResource, self).prepare_save(encoded)
                prepared['extra_value'] = 'Something'
                return prepared

        :param encoded: dict The encoded resource data

        """
        for k, v in encoded.items():
            if k in self._persisted_data and v == self._persisted_data[k]:
                encoded.pop(k)
        return encoded

    def save(self):
        """Persist pending changes
        """
        endpoint = make_endpoint(self)
        encoded = self.encode()
        prepared_data = self.prepare_save(encoded.copy())

        self.client.put(endpoint, prepared_data)
        self._persisted_data = encoded


class IndexedByIdDecoder(Decoder):
    """ Decode object responses which are indexed by id

    For use where APIs return an object index by object ID,
    rather than a list of objects which each object contains its
    own ID.
    """

    def decode(self, value):
        decoded = []
        for k, v in value.items():
            try:
                k = int(k)
            except (ValueError, TypeError):
                continue
            # Take the key (the object's ID) and add it do the
            # dictionary of object data
            v['id'] = k
            decoded.append(v)
        return decoded

