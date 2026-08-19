"""
Server sent events endpoint, streams realtime activity for a thing.

The browser opens /api/events/<tid> and gets a `message` event for every new
post, topic or vote inside that thing.
"""
import cyclone.web
from twisted.python import log

from .handler import BaseHandler
from ..data import pubsub


class EventStreamHandler(BaseHandler):
    """ streams events for a single thing as text/event-stream """

    # SSE responses are open ended, cyclone must not try to buffer or gzip them
    @cyclone.web.asynchronous
    def get(self, tid):
        self.set_header("Content-Type", "text/event-stream")
        self.set_header("Cache-Control", "no-cache")
        self.set_header("Connection", "close")
        # this cyclone build's chunked transfer transform is py2 only (it builds
        # str frames around bytes), so the stream is written raw and the
        # connection is closed by the client instead
        self._transforms = []
        # tell the client to retry after 3s if the stream drops
        # this cyclone build concatenates raw header bytes with the body, so
        # every chunk of an SSE stream has to be bytes
        self.write(b"retry: 3000\n\n")
        self.flush()

        def onEvent(message):
            payload = "data: {}\n\n".format(message.replace("\n", " "))
            self.write(payload.encode("utf-8"))
            self.flush()

        stop = pubsub.hub.listen(tid, onEvent)
        log.msg("event stream opened for thing {}".format(tid))

        def closed(_):
            stop()
            log.msg("event stream closed for thing {}".format(tid))

        # the request stays open until the client goes away, cyclone must not
        # finish it for us (hence @asynchronous and no returned deferred)
        self.notifyFinish().addBoth(closed)


from . import application

application.addHandler(r"/api/events/([0-9]+)", EventStreamHandler)
