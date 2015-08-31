from booby.fields import Collection


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
