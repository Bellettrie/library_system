VIEW = 'view'

def permits(permission, committee_names, committees):
    permissions = dict()
    permissions[VIEW] = ["ALL"]
    permissions['edit'] = ["BOARD", "ADMIN"]
    permissions['list'] = ["BOARD", "ADMIN"]

    return len(set(permissions.get(permission, [])) & committee_names) > 0
