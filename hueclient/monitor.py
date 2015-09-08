from eventlet import Queue


class Monitor(object):

    def __init__(self, resource, field, callback, poll_interval, event_queue, poll_pool, handler_pool):
        self.field = field
        self.resource = resource
        self.callback = callback
        self.poll_interval = poll_interval
        self.event_queue = event_queue
        self.poll_pool = poll_pool
        self.handler_pool = handler_pool
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
    monitor_class = Monitor

    def monitor(self, field, callback, poll_interval=None):
        poll_interval = poll_interval or self.api.poll_interval

        monitor = self.monitor_class(
            resource=self,
            field=field,
            callback=callback,
            poll_interval=poll_interval,
            event_queue=self.api.event_queue,
            poll_pool=self.api.poll_pool,
            handler_pool=self.api.handler_pool,
        )
        monitor.start()
        return monitor
