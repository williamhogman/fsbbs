"""
theme selection: a cookie picks the active theme, static assets of the active
theme are served from /st/
"""
import os

import cyclone.web

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
        # the theme cookie decides which directory the asset comes from
        # cyclone compares the resolved file against an absolute root
        self.root = os.path.abspath(
            "themes/{}/static".format(output.OutputFormatter.themeFor(self))) + os.sep
        return cyclone.web.StaticFileHandler.get(self, path, include_body)


from . import application

application.addHandler(r"/theme/([a-zA-Z0-9_-]+)", ThemeHandler)
