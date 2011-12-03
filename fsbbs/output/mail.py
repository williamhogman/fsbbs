from cStringIO import StringIO
from twisted.internet import defer
import fsbbs.config
from fsbbs.output.template import TemplateEngine


class PlainTextFormatter(TemplateEngine):
    def __init__(self):
        TemplateEngine.__init__(self,"themes/"+fsbbs.config.get("email.theme_plain")+"/")
    def _get_template(self,name):
        if not "." in name:
            name+=".txt"
        return TemplateEngine._get_template(self,name)

class MailOutput(object):
    def __init__(self):
        self._plain = PlainTextFormatter()

    def render_plain_body(self,template,data):
        """ Renders the body of a plain text email """
        bfr = StringIO()

        self._plain.dump(template,dict(thing=data),bfr)
        return bfr.getvalue()
        
        
Output = MailOutput()
