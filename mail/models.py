from django.db import models, transaction

# Create your models here.
from django.db.models import PROTECT

from members.models import Member
from mail_templated import send_mail
from django.conf import settings


class MailLog(models.Model):
    member = models.ForeignKey(Member, on_delete=PROTECT)
    contents = models.TextField()
    date = models.DateTimeField(auto_now=True)


@transaction.atomic
def mail_member(template_string: str, context: dict, member: Member, is_logged: bool, connection=None):
    context['BASE_URL'] = settings.BASE_URL
    if not member.is_anonymous_user:
        mail = member.email
        if settings.FAKE_MAIL:
            mail = settings.FAKE_MAIL_ADDRESS
        if connection:
            send_mail(template_string, context, 'info@bellettrie.utwente.nl', [mail], connection=connection)
        else:
            # send_mail(template_string, context, 'info@bellettrie.utwente.nl', [mail])
            pass
        if is_logged:
            MailLog.objects.create(member=member, contents=str(context))
