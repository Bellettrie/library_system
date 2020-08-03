from django.db import models

# Create your models here.
from django.db.models import PROTECT

from bellettrie_library_system.settings import BASE_URL, FAKE_MAIL
from members.models import Member
from mail_templated import send_mail


class MailLog(models.Model):
    member = models.ForeignKey(Member, on_delete=PROTECT)
    subject = models.CharField(max_length=255)


def mail_member(template_string: str, context: dict, member: Member, is_logged: bool, connection=None):
    context['BASE_URL'] = BASE_URL
    if not member.is_anonymous_user:
        mail = member.email
        if FAKE_MAIL:
            mail = 'nander@nander.net'
        if connection:
            send_mail(template_string, context, 'info@bellettrie.utwente.nl', [mail], connection=connection)
        else:
            send_mail(template_string, context, 'info@bellettrie.utwente.nl', [mail])
        if is_logged:
            MailLog.objects.create(member=member, subject=str(context))
