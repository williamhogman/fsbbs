from cStringIO import StringIO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from twisted.internet import defer
import fsbbs.config
from fsbbs import config
from fsbbs.output.template import TemplateEngine
from fsbbs.mail.outgoing import  clean_addr

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

    def _subject_line(self,subj):
        return self._subject_format.format(subj)

    @defer.inlineCallbacks
    def render_message(self,template,data):
        msg = MIMEMultipart("alternative")
        if template == "new_reply" or template == "new_topic":
            thing = data["thing"]
            parent = data["parent"] if template == "new_reply" else data["topic"]
            poster = yield thing.get_poster_name()
            msg['From'] = "{} <{}>".format(poster,clean_addr("user-"+poster))
            msg['Subject'] = self._subject_line(parent.title)
            msg['Reply-To'] = clean_addr("reply-{}".format(parent.tid))
        elif template ==  "delivery_failed":
            msg["Subject"] = self._subject_line("Message Delivery Failed")
        elif template == "thing_not_found":
            msg['Subject'] = self._subject_line("Unable to find post")
        elif template == "reply_successful":
            msg['Subject'] = self._subject_line("Your reply has been posted")
        elif template == "post_successful":
            msg['Subject'] = self._subject_line("Your topic has been posted")
        if not "From" in msg:
            msg['From'] = clean_addr("noreply")
        msg.attach(MIMEText(self.render_plain_body(template,data),"plain"))
        defer.returnValue(msg)
        
    def render_plain_body(self,template,data):
        """ Renders the body of a plain text email """
        bfr = StringIO()

        self._plain.dump(template,data,bfr)
        return bfr.getvalue()
        
        
Output = MailOutput()
