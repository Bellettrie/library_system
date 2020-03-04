from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

perms = dict()
VIEW_MEMBERS='members.view'
perms['admin'] = [VIEW_MEMBERS]

def permission_required(perm, login_url=None, raise_exception=False):
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
        return user is not None
    return user_passes_test(check_perms, login_url=login_url)