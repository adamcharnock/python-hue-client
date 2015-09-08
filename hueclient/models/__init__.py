from booby.decoders import Decoder


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

