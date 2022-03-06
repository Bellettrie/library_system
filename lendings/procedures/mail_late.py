from datetime import timezone, timedelta, datetime

from lendings.models import Lending
from mail.models import mail_member


def late_mails(fake=False):
    lendings = Lending.objects.filter(handed_in=False)
    late_dict = dict()
    almost_late_dict = dict()
    should_mail = set()
    for lending in lendings:
        if lending.is_late():
            if not lending.mailed_for_late or lending.last_mailed + timedelta(days=7) < datetime.now():
                should_mail.add(lending.member)
            my_list = late_dict.get(lending.member, [])
            my_list.append(lending)
            late_dict[lending.member] = my_list
        elif lending.is_almost_late():
            if lending.last_mailed + timedelta(days=2) < datetime.now():
                should_mail.add(lending.member)
            my_list = almost_late_dict.get(lending.member, [])
            my_list.append(lending)
            almost_late_dict[lending.member] = my_list

    for member in should_mail:

        if not fake:
            late_list = late_dict.get(member, [])
            almost_late_list = almost_late_dict.get(member, [])
            mail_member('mails/late_mail.tpl',
                        {'member': member, 'has_late': len(late_list) > 0,
                         'has_nearly_late': len(almost_late_list) > 0, 'lendings': late_list,
                         'almost_late': almost_late_list}, member, True)
            for lending in late_list:
                lending.last_mailed = datetime.now()

                lending.mailed_for_late = True
                lending.save()
            for lending in almost_late_list:
                lending.last_mailed = datetime.now()

                lending.save()
    return almost_late_dict, late_dict, should_mail
