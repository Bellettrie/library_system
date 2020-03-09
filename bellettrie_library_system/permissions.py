from django.contrib.auth.decorators import user_passes_test
from django.template.loader_tags import register
from django.urls import path

roles = dict()


def add_perm(perm, my_roles):
    roles[perm] = my_roles


PERM_ALL = ".all"

add_perm(PERM_ALL, ["ALL"])


def authorize(perm, login_url=None, raise_exception=False):
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
        return len(set(roles.get(perm, [])) & (committee_names | {"ALL"})) > 0

    return user_passes_test(check_perms, login_url=login_url)


def authorized_path(url, view, perm, name=None):
    name = name or perm
    return path(url, authorize(perm)(view), name=name)


@register.simple_tag
def permission(name):
    return getattr(settings, name, "")