"""
Realtime fan-out on top of redis pub/sub.

A single subscriber connection is shared by every listener, channels are
subscribed to on demand and dropped again when the last listener goes away.
"""
import os

import txredisapi
from twisted.internet import defer, reactor
from twisted.python import log


def channel_for(tid):
    """ the channel a thing publishes its events on """
    return "fsbbs:thing:{}".format(tid)


class _Protocol(txredisapi.SubscriberProtocol):
    def connectionMade(self):
        hub.protocol = self
        # (re)subscribe to whatever listeners are waiting for
        if hub.listeners:
            self.subscribe(list(hub.listeners.keys()))

    def messageReceived(self, pattern, channel, message):
        if isinstance(channel, bytes):
            channel = channel.decode("utf-8", "replace")
        if isinstance(message, bytes):
            message = message.decode("utf-8", "replace")
        hub.dispatch(channel, message)

    def connectionLost(self, reason):
        if hub.protocol is self:
            hub.protocol = None
        txredisapi.SubscriberProtocol.connectionLost(self, reason)


class _Factory(txredisapi.SubscriberFactory):
    protocol = _Protocol
    maxDelay = 10


class EventHub(object):
    """ dispatches redis pub/sub messages to registered callables """

    def __init__(self):
        self.listeners = dict()   # channel -> set of callables
        self.protocol = None
        self._connecting = False

    def _connect(self):
        if self._connecting:
            return
        self._connecting = True
        host = os.environ.get("REDIS_HOST", "127.0.0.1")
        port = int(os.environ.get("REDIS_PORT", "6379"))
        reactor.connectTCP(host, port, _Factory())

    def dispatch(self, channel, message):
        for cb in list(self.listeners.get(channel, ())):
            try:
                cb(message)
            except Exception as err:                      # a bad listener must not kill the rest
                log.msg("event listener failed: {}".format(err))

    def listen(self, tid, callback):
        """ registers a callback for a thing, returns a function that stops listening """
        channel = channel_for(tid)
        new_channel = channel not in self.listeners
        self.listeners.setdefault(channel, set()).add(callback)

        if self.protocol is None:
            self._connect()
        elif new_channel:
            self.protocol.subscribe(channel)

        def stop():
            subs = self.listeners.get(channel)
            if not subs:
                return
            subs.discard(callback)
            if not subs:
                del self.listeners[channel]
                if self.protocol is not None:
                    self.protocol.unsubscribe(channel)

        return stop


hub = EventHub()
