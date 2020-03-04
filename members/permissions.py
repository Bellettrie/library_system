from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

perms = dict()
VIEW = 'view'

BOARD = "BOARD"
KASCO = "KASCO"
ADMIN = "ADMIN"
COMCO = "COMCO"
BOOKBUYERS = "BOOKBUYERS"
KICKIN = "KICKIN"




def authorize(perm, my_function, login_url=None, raise_exception=False):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled, redirecting to the log-in page if necessary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.
    """

    def check_perms(user):
        if isinstance(perm, str):
            perms = (perm,)
        else:
            perms = perm
        if not hasattr(user, 'member'):
            return False

        print(user.member.old_customer_type)

        # As the last resort, show the login form
        committees = user.member.committees.all()
        committee_names = set(map(lambda committee: committee.code, committees))
        return my_function(perm, committee_names | {"ALL"}, user.member.committees)

    return user_passes_test(check_perms, login_url=login_url)


def permits(permission, committee_names, committees):
    permissions = dict()
    permissions[VIEW] = ["ALL"]
    permissions['edit'] = ["BOARD", "ADMIN"]
    permissions['list'] = ["BOARD", "ADMIN"]

    return len(set(permissions.get(permission, [])) & committee_names) > 0
