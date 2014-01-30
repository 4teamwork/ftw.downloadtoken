import logging
from zope.event import notify
from ftw.journal.events.events import JournalEntryEvent
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser import BrowserView
from zope.component import getAdapter
from Products.CMFCore.utils import getToolByName
from ftw.downloadtoken import downloadtokenMessageFactory as _
from AccessControl import SecurityManagement

logger = logging.getLogger('ftw.downloadtoken')
def msg(request, message, mtype): 
    IStatusMessage(request).addStatusMessage(message, type=mtype)
    getattr(logger, mtype)(message)
    
warn = lambda request, message: msg(request, message, "warn")
info = lambda request, message: msg(request, message, "info")
error = lambda request, message: msg(request, message, "error")

class DownloadFile(BrowserView):
    def __call__(self):
        token=self.request.get("token","")
        if self.exists(token):
            perm = self.get(token)
            return self.send_file(perm)
        else:
            error(self.request,"Leider kein korrekter hash")
        return self.request.RESPONSE.redirect("view")
        
    def exists(self, hash):
        manager = getAdapter(self.context.portal_url.getPortalObject(), name='download_permission_manager')
        return manager.download_permission_exists(hash)
        
    def get(self, hash):
        manager = getAdapter(self.context.portal_url.getPortalObject(), name='download_permission_manager')
        perm = manager.get_download_permission(hash=hash)
        # remove
        manager.invalidate_download_permission(perm)
        return perm
        
    def send_file(self,perm):
        reference_tool = getToolByName(self.context, 'reference_catalog')
        obj = reference_tool.lookupObject(perm.uid)
        file = obj.getFile()
        notify(JournalEntryEvent(obj, _(u"From")+": "+perm.email, _(u"File downloaded")))
        return file.download(self.request)
