from collections import MutableSequence
from booby.decoders import Decoder
from booby.encoders import Encoder
from booby.fields import Collection, List
from booby.helpers import nullable


class ManagedCollection(Collection):

    def __init__(self, model, *args, **kwargs):
        self.manager = kwargs.pop('manager', model.objects.__class__())
        self.manager.contribute_to_class(model)
        super(ManagedCollection, self).__init__(model, *args, **kwargs)

    def _resolve(self, value):
        value = super(ManagedCollection, self)._resolve(value)
        self.manager.results = value
        return self.manager

    def encode(self, value):
        return super(ManagedCollection, self).encode(self.manager.results)

    def set_parent_in_models(self, parent):
        for resource in self.manager.all():
            resource.set_parent_values(parent)

    def __getattr__(self, name):
        return getattr(self.manager, name)


class ManagedIdListCollection(ManagedCollection):
    """ Use for providing a managed collection upon a field which contains a
    list of model IDs.

    This does a little fancy footwork to ensure that the values
    are only loaded when accessed. This functionality is largely
    provided by LazyList
    """

    def __init__(self, model, *args, **kwargs):
        super(ManagedIdListCollection, self).__init__(model, *args, **kwargs)
        self.options['encoders'] = [ModelToIdListEncoder()]
        self.options['decoders'] = [IdToLazyModelListDecoder(model)]

    def decode(self, value):
        self._initial_encoded_value = value
        return super(ManagedIdListCollection, self).decode(value)

    def encode(self, value):
        if not value.results.is_loaded():
            # Avoid loading the results if nothing has changed
            return self._initial_encoded_value
        else:
            return super(ManagedIdListCollection, self).encode(value)

    def _resolve(self, value):
        self.manager.results = value
        return self.manager

    def set_parent_in_models(self, parent):
        self.manager.results.set_parent_lazy(parent)


class LazyList(MutableSequence):
    """ Wraps a generate which from which data is only loaded when needed
    """

    # TODO: The loading logic could be more intelligent

    def __init__(self, generator, size):
        self._generator = generator
        self._size = size

    def set_parent_lazy(self, parent):
        self.parent = parent
        if self.is_loaded():
            self._set_parent()

    def is_loaded(self):
        return hasattr(self, '_values')

    def _set_parent(self):
        for v in self._values:
            v.set_parent_values(self.parent)

    def _load(self):
        if not self.is_loaded():
            self._values = list(self._generator)
            self._set_parent()

    def __len__(self):
        return self._size

    def __getitem__(self, index):
        self._load()
        return self._values[index]

    def __setitem__(self, index, value):
        self._load()
        self._values[index] = value

    def __delitem__(self, index):
        self._load()
        del self._values[index]

    def insert(self, i, x):
        self._load()
        self._values.insert(i, x)


class IdToLazyModelListDecoder(Decoder):

    def __init__(self, model):
        self._model = model

    @nullable
    def decode(self, value):
        url_key = '{}_id'.format(self._model.__name__.lower())
        gen = (self._model.objects.get(**{url_key: id}) for id in value)
        return LazyList(generator=gen, size=len(value))


class ModelToIdListEncoder(Encoder):

    @nullable
    def encode(self, value):
        return [m.id for m in value]
