from time import sleep
from finch import Session, Collection, Model, fields
from tornado import httpclient
from hueclient import utilities, exceptions


class Client(Session):

    def __init__(self, bridge_host='philips-hue', username=None):
        username = username or utilities.load_username()
        if not username:
            raise exceptions.UsernameRequired('Username not specified and not found on disk')

        super(Client, self).__init__(
            httpclient.AsyncHTTPClient(),
            base_url='http://{bridge_host}/api/{username}'.format(**locals())
        )


class Light(Model):
    name = fields.String()


class Lights(Collection):
    model = Light
    url = '/lights'



if __name__ == '__main__':
    client = Client()
    lights = Lights(client)

    def show(*args):
        print args

    lights.all(show)
