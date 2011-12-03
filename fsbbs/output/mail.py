from cStringIO import StringIO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from twisted.internet import defer
import fsbbs.config
from fsbbs import config
from fsbbs.output.template import TemplateEngine
from fsbbs.mail.outgoing import  MimeWrap,clean_addr

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
        self._subject_format = config.get("email.subject_format")
    @defer.inlineCallbacks
    def render_message(self,template,data):
        msg = MIMEMultipart("alternative")
        if template == "new_reply":
            thing = data["thing"]
            parent = data["parent"]
            poster = yield thing.get_poster_name()
            msg['From'] = "{} <{}>".format(poster,clean_addr("user-"+poster))
            msg['Subject'] = self._subject_format.format(parent.title)
            msg['Reply-To'] = clean_addr("reply-{}".format(parent.tid))
        msg.attach(MIMEText(self.render_plain_body(template,data),"plain"))
        defer.returnValue(msg)
        
    def render_plain_body(self,template,data):
        """ Renders the body of a plain text email """
        bfr = StringIO()

        self._plain.dump(template,data,bfr)
        return bfr.getvalue()
        
        
Output = MailOutput()
