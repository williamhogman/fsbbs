"""
handlers for voting on things, votes reorder listings via the sorted set scores
"""
from twisted.internet import defer

from .handler import BaseHandler, SessionAuthMixin
from ..output import json_out
from ..service import service
from ..data.model import ThingNotFoundError


class VoteHandler(BaseHandler, SessionAuthMixin):
    """ handler for casting a vote from a plain form """
    @defer.inlineCallbacks
    def post(self):
        yield self.verifySession()
        if not self.requireLogin():
            return

        tid = self.get_argument("tid")
        delta = self.get_argument("delta", "1")
        try:
            yield service.vote(tid, self.user.uid, delta)
        except ThingNotFoundError:
            self.set_status(404)
            self.finish("404")
            return

        back = self.get_argument("back", None) or self.request.headers.get("Referer")
        # only ever bounce back inside this site
        if not back or not back.startswith("/"):
            back = "/index.html"
        self.redirect(back)


class VoteJSONHandler(BaseHandler, SessionAuthMixin):
    """ handler for casting a vote via JSON+XHR """
    @defer.inlineCallbacks
    def post(self):
        yield self.verifySession()
        self.set_header("Content-Type", "application/json")
        if not self.logged_in:
            self.set_status(401)
            self.finish(json_out.serialize({"status": "unauthorized"}))
            return

        tid = self.get_argument("tid")
        delta = self.get_argument("delta", "1")
        try:
            res = yield service.vote(tid, self.user.uid, delta)
        except ThingNotFoundError:
            self.set_status(404)
            self.finish(json_out.serialize({"status": "not_found"}))
            return

        self.finish(json_out.serialize(res))


from . import application

application.addHandler(r"/vote", VoteHandler)
application.addHandler(r"/api/vote.json", VoteJSONHandler)
