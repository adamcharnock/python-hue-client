from repose.validators import *
from repose.helpers import nullable


class UnsignedInteger(Integer):
    """This validator forces fields values to be an instance of `int`
    within the range 0 <= x < 2^16"""

    def __init__(self, bits=32):
        self.bits = bits

    @nullable
    def validate(self, value):
        if not isinstance(value, int):
            raise errors.ValidationError('should be an integer')
        if value < 0 or value >= 1 << self.bits:
            raise errors.ValidationError(
                'should be an integer in the range 0 to 2^{}'.format(self.bits))


class CieColorSpaceCoordinates(Validator):

    @nullable
    def validate(self, value):
        try:
            x, y = value
        except (ValueError, TypeError):
            raise errors.ValidationError('should be a tuple or list of two values')

        if not isinstance(x, int) or x < 0 or x > 1:
            raise errors.ValidationError('x coordinate must be an integer in the range 0 to 1')

        if not isinstance(y, int) or y < 0 or y > 1:
            raise errors.ValidationError('y coordinate must be an integer in the range 0 to 1')
