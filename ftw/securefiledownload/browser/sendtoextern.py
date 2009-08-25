import re
import logging
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser import BrowserView

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
                error(self.request,"enter a valid email address")
            if not comment:
                    error(self.request,"enter a comment")
        return super(SendToExtern,self).__call__()
       
    def isEmail(self,value):
        expr = re.compile(r"^(\w&.%#$&'\*+-/=?^_`{}|~]+!)*[\w&.%#$&'\*+-/=?^_`{}|~]+@(([0-9a-z]([0-9a-z-]*[0-9a-z])?\.)+[a-z]{2,6}|([0-9]{1,3}\.){3}[0-9]{1,3})$", re.IGNORECASE)
        if expr.match(value):
            return True
        return False