from django.db import models

# Create your models here.
from django.db.models import PROTECT

from members.models import Member
from mail_templated import send_mail


class MailLog(models.Model):
    member = models.ForeignKey(Member, on_delete=PROTECT)
    subject = models.CharField(max_length=255)


def mail_member(template_string: str, context: dict, member: Member, is_logged: bool, connection=None):
    if not member.is_anonymous_user:
        if connection:
            send_mail(template_string, context, 'info@bellettrie.utwente.nl', [member.email], connection=connection)
        else:
            send_mail(template_string, context, 'info@bellettrie.utwente.nl', [member.email])
        if is_logged:
            MailLog.objects.create(member=member, subject=str(context))
