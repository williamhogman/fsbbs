"""
theme selection: a cookie picks the active theme, static assets of the active
theme are served from /st/
"""
import cyclone.web
from twisted.internet import defer

from .handler import BaseHandler
from ..output.html import output


class ThemeHandler(BaseHandler):
    """ sets the theme cookie and bounces the user back """
    def get(self, name):
        if name not in output.availableThemes():
            self.set_status(404)
            self.finish("no such theme")
            return
        self.set_cookie("theme", name)
        back = self.request.headers.get("Referer")
        if not back or not back.startswith("/"):
            back = "/index.html"
        self.redirect(back)


class ThemeStaticHandler(cyclone.web.StaticFileHandler):
    """ serves the static files of the theme the visitor selected """
    def get(self, path, include_body=True):
        theme = output.OutputFormatter.themeFor(self)
        self.root = "themes/{}/static/".format(theme)
        return cyclone.web.StaticFileHandler.get(self, path, include_body)


from . import application

application.addHandler(r"/theme/([a-zA-Z0-9_-]+)", ThemeHandler)
application.addHandler2 = None if False else None
