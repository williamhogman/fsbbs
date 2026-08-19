import os

from jinja2 import Environment, FileSystemLoader, ChoiceLoader
from datetime import datetime,date
from ...service import service
import markdown

THEME_ROOT = "themes"
DEFAULT_THEME = os.environ.get("FSBBS_THEME","default")

def availableThemes():
    """ every directory under themes/ is a theme """
    try:
        return sorted(d for d in os.listdir(THEME_ROOT)
                      if os.path.isdir(os.path.join(THEME_ROOT,d)))
    except OSError:
        return ["default"]

def markdownFilter(text):
    """ jinja filter for rendering markdown, not async and very slow"""
    return markdown.markdown(text or "")

def dateFilter(dt):
    """ a human readable date"""
    # TODO: expand on this to include timedeltas and other things.
    if dt.date() == date.today():
        return dt.strftime("Today %H:%M")
    elif dt.year != datetime.now().year:
        return dt.strftime("%a, %d. %b %Y %H:%M")
    else:
        return dt.strftime("%a, %d. %b %H:%M")

class HTMLOutputFormatter:
    """ processes dict objects and uses a template to format them as HTML """

    def __init__(self):
        """Creates a new instance of HTMLOutputFormatter"""
        # one jinja environment per theme, built on demand
        self._envs = dict()

    def _environment(self,theme):
        """ gets (and caches) the environment for a theme, falling back to default """
        if theme not in self._envs:
            loaders = [FileSystemLoader(os.path.join(THEME_ROOT,theme))]
            if theme != "default":
                # a theme only has to ship the templates it actually changes
                loaders.append(FileSystemLoader(os.path.join(THEME_ROOT,"default")))
            env = Environment(loader=ChoiceLoader(loaders))
            env.filters['markdown'] = markdownFilter
            env.filters['nicedate'] = dateFilter
            self._envs[theme] = env
        return self._envs[theme]

    def themeFor(self,fp=None):
        """ resolves the theme for a request, the `theme` cookie wins over the default """
        theme = DEFAULT_THEME
        if fp is not None and hasattr(fp,"get_cookie"):
            cookie = fp.get_cookie("theme")
            if cookie and cookie in availableThemes():
                theme = cookie
        if theme not in availableThemes():
            theme = "default"
        return theme

    def render(self,name,data,fp=None):
        """ 
        returns an object with a dump function that can be called on a file-like object
        """
        return self._getTemplate(name,self.themeFor(fp)).stream(data)

    def dump(self,name,data,fp):
        """ writes a rendered template to a file for output """
        theme = self.themeFor(fp)
        if isinstance(data,dict):
            data.setdefault("theme",theme)
            data.setdefault("themes",availableThemes())
        self._getTemplate(name,theme).stream(data).dump(fp)


    def _getTemplate(self,name,theme="default"):
        """ gets a template from the jinja2 backend """
        return self._environment(theme).get_template(name)


OutputFormatter = HTMLOutputFormatter()

