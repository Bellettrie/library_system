from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

from bellettrie_library_system.permissions import add_perm

perms = dict()
VIEW = 'view'

BOARD = "BOARD"
KASCO = "KASCO"
ADMIN = "ADMIN"
COMCO = "COMCO"
BOOKBUYERS = "BOOKBUYERS"
KICKIN = "KICKIN"
LENDERS = "LENDERS"
BOOKS = "BOOKS"

MEMBERS_LIST = "members.list"
MEMBERS_VIEW = "members.view"
MEMBERS_EDIT = "members.edit"
MEMBERS_NEW = "members.new"

add_perm(MEMBERS_LIST, ["ALL"])
