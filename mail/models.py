from django.db import models, transaction

# Create your models here.
from django.db.models import PROTECT

from members.models import Member
from mail_templated import EmailMessage
from django.conf import settings

from utils.time import get_now


class MailLog(models.Model):
    member = models.ForeignKey(Member, on_delete=PROTECT)
    contents = models.TextField()
    subject = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now=True)
    sent = models.BooleanField(default=True)

    @transaction.atomic
    def send(self):
        msg = EmailMessage(subject=self.subject,
                           body=self.contents,
                           from_email="info@bellettrie.utwente.nl",
                           to=[self.member.email])
        msg._is_rendered = True
        msg.send()
 
        self.sent = True
        self.save()


@transaction.atomic
def mail_member(template_string: str, context: dict, member: Member, now=None):
    if now is None:
        now = get_now()
    context['BASE_URL'] = settings.BASE_URL
    if not member.is_anonymous_user:
        m = EmailMessage(template_string, context, "info@bellettrie.utwente.nl", render=True)
        MailLog.objects.create(member=member, contents=m.body, subject=m.subject, date=now, sent=False)
