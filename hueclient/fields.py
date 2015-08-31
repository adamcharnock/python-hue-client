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

    def __getattr__(self, name):
        return getattr(self.manager, name)


class ManagedIdListCollection(ManagedCollection):
    def __init__(self, model, *args, **kwargs):
        super(ManagedIdListCollection, self).__init__(model, *args, **kwargs)
        self.options['encoders'] = [ModelToIdListEncoder()]
        self.options['decoders'] = [IdToModelListDecoder(model)]


class IdToModelListDecoder(Decoder):

    def __init__(self, model):
        self._model = model

    @nullable
    def decode(self, value):
        url_key = '{}_id'.format(self._model.__name__.lower())
        return [self._model.objects.get(**{url_key: id}) for id in value]


class ModelToIdListEncoder(Encoder):

    @nullable
    def encode(self, value):
        return [m.id for m in value]
