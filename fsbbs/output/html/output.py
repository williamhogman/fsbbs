from jinja2 import Environment, FileSystemLoader
from datetime import datetime,date
from ...service import service
import markdown

def markdownFilter(text):
    """ jinja filter for rendering markdown, not async and very slow"""
    return markdown.markdown(text,safe_mode=True)

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
        # actually we don't support themes yet :o
        self.env = Environment(loader=FileSystemLoader('themes/default/'))
        self.env.filters['markdown'] = markdownFilter
        self.env.filters['nicedate'] = dateFilter
                         

    def render(self,name,data):
        """ 
        returns an object with a dump function that can be called on a file-like object
        """
        return self._getTemplate(name).stream(data)

    def dump(self,name,data,fp):
        """ writes a rendered template to a file for output """
        self._getTemplate(name).stream(data).dump(fp)


    def _getTemplate(self,name):
        """ gets a template from the jinja2 backend """
        return self.env.get_template(name)


OutputFormatter = HTMLOutputFormatter()


