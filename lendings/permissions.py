from bellettrie_library_system.permissions import add_perm
from members.permissions import ADMIN, LENDERS

LENDING_LIST = 'lendings.list'
LENDING_VIEW = 'lendings.view'
LENDING_NEW = 'lendings.new'
LENDING_FINALIZE = 'lendings.finalize'
LENDING_MY_LENDINGS = 'lendings.me'


add_perm(LENDING_VIEW, [ADMIN, LENDERS])
add_perm(LENDING_LIST, [ADMIN, LENDERS])
add_perm(LENDING_NEW, [ADMIN, LENDERS])
