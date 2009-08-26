import logging
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser import BrowserView
from zope.component import getAdapter
from ftw.journal.events.events import JournalEntryEvent
from zope.event import notify
from Products.CMFCore.utils import getToolByName
from ftw.securefiledownload import securefiledownloadMessageFactory as _

logger = logging.getLogger('ftw.securefiledownload')
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
            info(self.request,"Korrekter hash...")
            info(self.request,"email: %s / file: %s"%(perm.email,perm.uid))
            notify(JournalEntryEvent(self.context, _(u"From")+": "+perm.email, _(u"File downloaded")))
            # benutzer wechseln
            # self.context.acl_users.getUser("zopemaster")
            self.get_file_by_uid(perm.uid)
            # benutzer zurück
        else:
            error(self.request,"Leider kein korrekter hash")
        return super(DownloadFile,self).__call__()
        
    def exists(self, hash):
        manager = getAdapter(self.context.portal_url.getPortalObject(), name='download_permission_manager')
        return manager.download_permission_exists(hash)
        
    def get(self, hash):
        manager = getAdapter(self.context.portal_url.getPortalObject(), name='download_permission_manager')
        perm = manager.get_download_permission(hash=hash)
        print perm, perm.hash
        # remove
        # manager.invalidate_download_permission(perm)
        return perm
        
    def get_file_by_uid(self,uid):
        request = self.context.REQUEST
        response = request.RESPONSE
        target=""
        reference_tool = getToolByName(self.context, 'reference_catalog')
        obj = reference_tool.lookupObject(uid)
        if not obj:
            return response.notFoundError('''The link you followed appears to be broken''')
        else:
            target=obj.absolute_url()+"/at_download"
        return response.redirect(target, status=301)