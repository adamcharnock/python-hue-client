"""
The monitoring API provides an `eventlet`_-based polling layer
allowing you to respond to changes in state of Philips
Hue devices.

.. note:: Use of the monitoring API requires you install `eventlet`_. You can do so
        using pip::

            pip install eventlet

There are two stages to setting up this monitoring:

1. Setup your the changes you wish to monitor.

2. Call :func:`hue_api.start_monitor_loop()`. Doing so will pause execution
   and begin monitoring for events.

For example::

    def handle(resource, field, previous, current):
        print "Change from {} to {}".format(previous, current)

    switch = TapSwitch.objects.get(id=3)
    # Monitor the entire state of the switch
    switch.monitor(field=lambda sw: sw.state.as_dict(), callback=handle, poll_interval=0.2)

    light = Light.objects.get(id=1)
    # Monitor only the on state of the light
    light.monitor(field=lambda l: l.state.on, callback=handle, poll_interval=1)

    # Start the monitoring loop
    hue_api.start_monitor_loop()
    print "This will never be printed!"

The value given by ``field`` will be checked every ``poll_interval`` seconds. If
the values changes, ``callback`` will be called.

See :func:`MonitorMixin.monitor()` for more information, and details of callback
parameters.

.. _eventlet: http://eventlet.net

"""


class Monitor(object):
    """ Manages the process of monitoring a resource

    .. note: You probably do not need to worry about this to much.
             You can monitor resources without having to use this class.

    Attributes:

        field (string|callable): The field to monitor. See :func:`MonitorMixin.monitor`.
        resource (Resource): The resource instance to monitor. See :func:`MonitorMixin.monitor`.
        callback (callable): The callback to call when complete
        poll_interval (float): The interval between polls in milliseconds
        event_queue (eventlet.Queue): The queue onto which to push the change events
        poll_pool (eventlet.Pool): The pool for the eventlets tasked with polling the API

    """

    def __init__(self, resource, field, callback, poll_interval, event_queue, poll_pool):
        self.field = field
        self.resource = resource
        self.callback = callback
        self.poll_interval = poll_interval
        self.event_queue = event_queue
        self.poll_pool = poll_pool
        self._previous_value = self._get_field_value()

    def _get_field_value(self):
        if callable(self.field):
            return self.field(self.resource)
        else:
            return getattr(self.resource, self.field)

    def trigger(self, resource):
        self.callback(resource)

    def start(self):
        self.poll_pool.spawn_n(self.poll_loop)

    def poll_loop(self):
        from eventlet import sleep
        while True:
            self.resource.refresh()
            current_value = self._get_field_value()
            if self._previous_value != current_value:
                self.event_queue.put(
                    (self.callback, self.resource, self.field, self._previous_value, current_value)
                )
                self._previous_value = current_value
            sleep(self.poll_interval)


class MonitorMixin(object):
    """ Mixin to provide monitoring functionality to Resources.

    Attributes:

        monitor_class (Monitor): The :class:`Monitor` class to instantiate. Provided to
                                 facilitate extending monitoring
                                 functionality.
    """
    monitor_class = Monitor

    def monitor(self, field, callback, poll_interval=None):
        """ Monitor `field` for change

        Will monitor ``field`` for change and execute ``callback`` when
        change is detected.

        Example usage::

            def handle(resource, field, previous, current):
                print "Change from {} to {}".format(previous, current)

            switch = TapSwitch.objects.get(id=3)
            # Note that we monitor the entire state of the Hue Tap
            # switch rather than a specific field
            switch.monitor(lambda sw: sw.state.as_dict(), handle, poll_interval=0.2)

            # Execution will stop here and the API client will begin polling for changes
            hue_api.start_monitor_loop()

        Args:

            field (string): The name of the field to be monitored. This may also
                be a callable which will be called with the resource
                instance as its single argument and must return a
                value which can be compared to previous values.

            callback (callable): The callable to be called when a change is
                detected. It will be called with parameters
                as follows:

                * resource instance
                * field name,
                * previous value
                * current value.

            poll_interval (float): Interval between polling in seconds.
                Defaults to the API's `poll_interval` value (which defaults
                to 0.1 second.

        Returns:
            Monitor:
        """
        poll_interval = poll_interval or self.api.poll_interval

        monitor = self.monitor_class(
            resource=self,
            field=field,
            callback=callback,
            poll_interval=poll_interval,
            event_queue=self.api.event_queue,
            poll_pool=self.api.poll_pool,
        )
        monitor.start()
        return monitor
