def hx_wrap(view):
    """
     Wraps a view function in a function that checks whether htmx is enabled
     This allows using the same view for both the htmx and fallback flows.
    """

    def wrapper(request, *args, **kwargs):
        hx_enabled = False
        if request.headers.get('Hx-Request'):
            hx_enabled = True
        return view(request, hx_enabled=hx_enabled, *args, **kwargs)

    return wrapper
