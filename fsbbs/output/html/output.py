from ..template import TemplateEngine

class HTMLOutputFormatter(TemplateEngine):
    """ processes dict objects and uses a template to format them as HTML """

    def __init__(self):
        """Creates a new instance of HTMLOutputFormatter"""
        # actually we don't support themes yet :o
        TemplateEngine.__init__(self,"themes/default")


OutputFormatter = HTMLOutputFormatter()


