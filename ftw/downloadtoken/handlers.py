from zope.i18n import translate
from DateTime import DateTime
from ftw.journal.events.events import JournalEntryEvent
from ftw.downloadtoken import _
from zope.event import notify


def downloadlink_sent(event):
    emails = event.emails
    obj = event.obj
    action = _(u"label_send_dllink", default=u"Downloadlink sent")
    journal_comment = translate(
        msgid=u'msg_downloadlink_sent',
        domain='ftw.downloadtoken',
        context=obj.REQUEST,
        mapping=dict(
            mail_list=len(emails) > 0 and ', '.join(emails) + '\n' or '-',
            ))
    time = DateTime()
    notify(JournalEntryEvent(obj, journal_comment, action, time=time))

    
def downloadlink_opened(event):
    email = event.email
    obj = event.obj
    action = _(u"label_open_dllink", default=u"Downloadlink opened")
    journal_comment = translate(
        msgid=u'msg_downloadlink_open',
        domain='ftw.downloadtoken',
        context=obj.REQUEST,
        mapping=dict(
            mail=email,
            ))
    time = DateTime()
    notify(JournalEntryEvent(obj, journal_comment, action, actor=email, time=time))
    