"""
Server sent events endpoint, streams realtime activity for a thing.

The browser opens /api/events/<tid> and gets a `message` event for every new
post, topic or vote inside that thing.
"""
from twisted.internet import defer
from twisted.python import log

from .handler import BaseHandler
from ..data import pubsub


class EventStreamHandler(BaseHandler):
    """ streams events for a single thing as text/event-stream """

    # SSE responses are open ended, cyclone must not try to buffer or gzip them
    def get(self, tid):
        self.set_header("Content-Type", "text/event-stream")
        self.set_header("Cache-Control", "no-cache")
        self.set_header("Connection", "keep-alive")
        # tell the client to retry after 3s if the stream drops
        self.write("retry: 3000\n\n")
        self.flush()

        def onEvent(message):
            self.write("data: {}\n\n".format(message.replace("\n", " ")))
            self.flush()

        stop = pubsub.hub.listen(tid, onEvent)
        log.msg("event stream opened for thing {}".format(tid))

        d = self.notifyFinish()

        def closed(_):
            stop()
            log.msg("event stream closed for thing {}".format(tid))

        d.addBoth(closed)
        # never call finish, the client closes the stream
        return d


from . import application

application.addHandler(r"/api/events/([0-9]+)", EventStreamHandler)
