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
LENDERS = "LENDERS"
BOOKS = "BOOKS"
RETRIEVAL = "RETRIEVAL"
WEB = "WEB"
KONNICHIWA = "KONNICHIWA"

MEMBERS_LIST = "members.list"
MEMBERS_VIEW = "members.view"
MEMBERS_EDIT = "members.edit"
MEMBERS_DELETE = "members.delete"
MEMBERS_NEW = "members.new"
