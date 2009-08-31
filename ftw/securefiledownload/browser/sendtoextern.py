import re
import logging
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser import BrowserView
from ftw.securefiledownload import securefiledownloadMessageFactory as _

from zope.event import notify
from ftw.journal.events.events import JournalEntryEvent
from zope.component import getAdapter

from ftw.sendmail.composer import HTMLComposer
from zope import component
from zope.sendmail.interfaces import IMailer

logger = logging.getLogger('ftw.securefiledownload')

def msg(request, message, mtype): 
    IStatusMessage(request).addStatusMessage(message, type=mtype)
    getattr(logger, mtype)(message)
    
warn = lambda request, message: msg(request, message, "warn")
info = lambda request, message: msg(request, message, "info")
error = lambda request, message: msg(request, message, "error")

class SendToExtern(BrowserView):
    def __call__(self):
        email=self.request.get("email","")
        comment=self.request.get("comment","")
        submit=self.request.get("submit","")
        if submit:
            if not self.isEmail(email):
                error(self.request,_(u"Enter a valid email address"))
            elif not comment:
                error(self.request,_(u"Enter a comment"))
            else:
                hash=self.create(email)
                link="http://localhost:8080/emt-kva.teamraum.ch/platform/download_file?token="+hash
                
                composer = HTMLComposer('Guten Tag<br /><br />BLABLABLA schickt Ihnen eine Datei zum <b>einmaligen</b> Download.<br />Bitte innert einer Woche herunterladen! Ansonsten verfällt der Download.<br /><br />link: %s <br />kommentar: %s'%(link,comment), 'Download-Link erhalten', [(email,email)])
                try:
                    email_message = composer.render()
                except Exception, e:
                    email_message = None
                    error(self.request,_(u"There is appeard an error"))
                if email_message is not None:
                    smtp = component.getUtility(IMailer, 'plone.smtp')
                    smtp.update_settings()
                    smtp.send(email_message['From'], email_message['To'], email_message.as_string())
                    
                    notify(JournalEntryEvent(self.context, _(u"To")+": "+email, _(u"File sent to external")))
                    info(self.request,_(u"The file has been sent"))
        return super(SendToExtern,self).__call__()
       
    def isEmail(self,value):
        expr = re.compile(r"^(\w&.%#$&'\*+-/=?^_`{}|~]+!)*[\w&.%#$&'\*+-/=?^_`{}|~]+@(([0-9a-z]([0-9a-z-]*[0-9a-z])?\.)+[a-z]{2,6}|([0-9]{1,3}\.){3}[0-9]{1,3})$", re.IGNORECASE)
        if expr.match(value):
            return True
        return False
        
    def create(self, email):
        manager = getAdapter(self.context.portal_url.getPortalObject(), name='download_permission_manager')
        perm = manager.create_download_permission(self.context, email)
        print perm, perm.hash
        return perm.hash