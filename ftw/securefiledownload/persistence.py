
import random
import md5
from datetime import datetime, timedelta

from persistent import Persistent
from persistent.list import PersistentList
from Acquisition import aq_inner
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations

from interfaces import IDownloadPermissionManager

DOWNLOAD_PERMISSION_EXPIRATION = 7 # days

class DownloadPermissionManager(object):

    implements(IDownloadPermissionManager)

    def __init__(self, context):
        self.context = aq_inner(context.portal_url.getPortalObject())
        self.annotations = IAnnotations(self.context)

    def get_download_permissions(self):
        return self.annotations.get('download_permissions', PersistentList())

    def set_download_permissions(self, download_permissions):
        if not isinstance(download_permissions, PersistentList):
            raise TypeError('Excpected PersistentList')
        self.annotations['download_permissions'] = download_permissions

    def create_download_permission(self, file, receiver_email):
        hash = self._create_unique_hash()
        download_permission = DownloadPermission(hash=hash, uid=file.UID(), email=receiver_email)
        permlist = self.get_download_permissions()
        permlist.append(download_permission)
        self.set_download_permissions(permlist)
        return download_permission

    def invalidate_download_permission(self, download_permission):
        permlist = self.get_download_permissions()
        permlist.remove(download_permission)
        self.set_download_permissions(permlist)

    def get_download_permission(self, hash):
        for perm in self.get_download_permissions():
            if perm.hash == hash:
                if datetime.now() > perm.expiration:
                    self.invalidate_download_permission(perm)
                    raise Exception('Download Permission expired: %s' % hash)
                return perm
        raise Exception('Download Permission not found: %s' % hash)

    def download_permission_exists(self, hash):
        try:
            self.get_download_permission(hash)
            return True
        except Exception:
            return False

    def _create_unique_hash(self):
        date = datetime.now().isoformat()
        def make_hash():
            return md5.md5(date + str(random.random())).hexdigest()
        hash = make_hash()
        while self.download_permission_exists(hash):
            hash = make_hash()
        return hash


class DownloadPermission(Persistent):

    def __init__(self, hash, uid, email):
        self.hash = hash
        self.uid = uid
        self.email = email
        self.expiration = datetime.now() + timedelta(days=DOWNLOAD_PERMISSION_EXPIRATION)

