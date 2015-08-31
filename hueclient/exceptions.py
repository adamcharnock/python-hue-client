
class UsernameRequired(Exception): pass
class ClientAlreadySet(Exception): pass

class HueApiException(Exception): pass
class LinkButtonNotPressed(HueApiException): pass
