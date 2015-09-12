from _socket import gethostname
import json
import os
import requests
from hueclient import exceptions


USERNAME_SAVE_PATH = '~/.python_hue'


def handle_error(error):
    exception, message = {
        '101': (exceptions.LinkButtonNotPressed, ''),
    }.get(
        str(error.get('type')),
        (exceptions.HueApiException, 'Error type {type} when calling {address}: {description}')
    )
    raise exception(message.format(**error))


def parse_response(response):
    json = response.json()
    error = None
    try:
        error = json[0]['error']
    except (IndexError, KeyError):
        pass

    if error:
        return handle_error(error)
    else:
        return json


def authenticate(app_name, bridge_host, client_name=None):
    client_name = client_name or gethostname()
    url = 'http://{}/api'.format(bridge_host)
    response = requests.post(url, json={
        'devicetype': '{}#{}'.format(app_name, client_name),
    })
    json = parse_response(response)
    return json[0]['success']['username']


def authenticate_interactive(app_name=None, bridge_host=None, client_name=None, force=False):
    if not force:
        # Don't reauthenticate if we already have the username on disk
        existing_username = load_username()
        if existing_username:
            return existing_username

    host_name = gethostname()

    bridge_host = raw_input("Philips Hue Bridge IP address or "
                            "host name [philips-hue]: "
                            ).strip() or 'philips-hue'
    app_name = raw_input("Your application name [test-app]").strip() or 'test-app'
    client_name = raw_input("Your device name [{}]" .format(host_name)).strip() or host_name

    username = None
    while not username:
        raw_input('Now press the link button on the Hue Bridge. Press enter when done.')
        try:
            username = authenticate(
                bridge_host=bridge_host, app_name=app_name, client_name=client_name)
        except exceptions.LinkButtonNotPressed:
            print 'Error, link button not pressed, trying again...'

    print 'Your username is: {}'.format(username)

    if raw_input('Save username to {} [Y/n]?'.format(USERNAME_SAVE_PATH)) != 'n':
        save_username(username)


def save_username(username):
    with open(os.path.expanduser(USERNAME_SAVE_PATH), 'w') as f:
        f.write(json.dumps({
            'philips-hue': {
                'username': username,
            }
        }))


def load_username():
    try:
        with open(os.path.expanduser(USERNAME_SAVE_PATH), 'r') as f:
            contents = f.read()
    except IOError:
        return None
    return json.loads(contents)['philips-hue']['username']

