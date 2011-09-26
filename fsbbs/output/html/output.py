from jinja2 import Environment, FileSystemLoader

#from .markdown import markdownToHTML
from ...service import service

class HTMLOutputFormatter:
    """ processes dict objects and uses a template to format them as HTML """

    def __init__(self):
        # actually we don't support themes yet :o
        self.env = Environment(loader=FileSystemLoader('themes/default/'))

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


