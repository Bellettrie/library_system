def hx_wrap(view):
    def wrapper(*args, **kwargs):
        return view(hx_enabled=True, *args, **kwargs)
    return wrapper