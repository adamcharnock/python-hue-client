Python Hue Client
=================

.. image:: https://img.shields.io/pypi/v/python-hue-client.svg
    :target: https://badge.fury.io/py/python-hue-client

.. image:: https://img.shields.io/pypi/dm/python-hue-client.svg
    :target: https://pypi.python.org/pypi/python-hue-client

.. image:: https://img.shields.io/github/license/adamcharnock/python-hue-client.svg
    :target: https://pypi.python.org/pypi/python-hue-client/

.. image:: http://unmaintained.tech/badge.svg
    :target: http://unmaintained.tech
    :alt: No Maintenance Intended


A full-featured Python client for the Philips Hue lighting system.

Installation
------------

Installation using pip (recommended)::

    pip install python-hue-client

Installation using easy_install::

    easy_install python-hue-client

Documentation
-------------

Documentation can be found at http://python-hue-client.readthedocs.org

Quick Start
-----------

This library is modelled roughly on concepts borrowed from Django's ORM.
There are some `examples`_ available in GitHub, but let's dive in
with an example that list all the available lights::

    from pprint import pprint
    from hueclient.api import hue_api
    from hueclient.models.light import Light

    if __name__ == '__main__':
        hue_api.authenticate_interactive(app_name='List Lights Example')

        for light in Light.objects.all():
            print(
                "Light {id} is named '{name}' and is {onoff} (brightness: {brightness})".format(
                    id=light.id,
                    name=light.name,
                    onoff='on' if light.state.on else 'off',
                    brightness=light.state.brightness,
                )
            )

Here is an example which blinks a specific light::

    from time import sleep
    from hueclient.api import hue_api
    from hueclient.models.light import Light

    # examples/blink_light.py
    if __name__ == '__main__':
        # Make sure we are authenticated with the hue bridge.
        # You will be prompted if no username is found in ~/.python_hue
        hue_api.authenticate_interactive(app_name='Blink Light Example')

        # Get light ID 1
        light = Light.objects.get(id=1)

        # Loop forever
        while True:
            # Flip the on state from on -> off / off -> on
            light.state.on = not light.state.on

            # Save the state back to the bridge
            # (Note: required in order for your changes to take effect)

            light.state.save()

            # Pause here for a couple of seconds to create a slow blink
            # (Note: It is important to sleep here at least a little to
            # avoid overloading the bridge with API requests)
            sleep(2)

For more information see the `full documentation <http://python-hue-client.readthedocs.org>`_.

Credits
-------

Developed by `Adam Charnock`_, contributions very welcome!

python-hue-client is packaged using seed_.

.. _seed: https://github.com/adamcharnock/seed/
.. _examples: https://github.com/adamcharnock/python-hue-client/tree/master/examples
.. _Adam Charnock: https://adamcharnock.com
