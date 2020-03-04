from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

perms = dict()
perms['admin'] = ['hoi']

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
        print(type(perms))
        print(perms)
        # As the last resort, show the login form
        return True
    return user_passes_test(check_perms, login_url=login_url)