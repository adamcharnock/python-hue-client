from collections import MutableSequence
from booby.decoders import Decoder
from booby.encoders import Encoder
from booby.fields import *
from booby.helpers import nullable
from hueclient import validators


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

    def contribute_parent_to_models(self, parent):
        for resource in self.manager.all():
            resource.contribute_parents(parent)

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

    def contribute_parent_to_models(self, parent):
        self.manager.results.set_parent_lazy(parent)


class Dictionary(Field):
    """:class:`Field` subclass with `dict` validation."""

    def __init__(self, *args, **kwargs):
        super(Dictionary, self).__init__(validators.Dictionary(), *args, **kwargs)


class TimePattern(String):
    """ :class:`Field` subclass for Philips Hue time pattern.

    Details can be found in the
    `Philips Hue Documentation <http://www.developers.meethue.com/documentation/datatypes-and-time-patterns>`_.

    .. todo:: The :class:`TimePattern` field needs implementing

    """
    pass


class IsoDate(String):
    """ :class:`Field` subclass for Philips Hue time pattern.

    Details can be found in the
    `Philips Hue Documentation <http://www.developers.meethue.com/documentation/datatypes-and-time-patterns>`_.

    .. todo:: The :class:`IsoDate` field needs implementing
              Should parse ISO8601 strings into datetime objects and back again.

    """
    pass


class LazyList(MutableSequence):
    """ Wraps a generate which from which data is only loaded when needed

    .. todo:: The :class:`LazyList` loading logic could be more intelligent
    """

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
            v.contribute_parents(self.parent)

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
