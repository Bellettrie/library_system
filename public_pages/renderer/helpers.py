from django.conf import settings
from django.templatetags.static import static


def url_conv(url):
    if url is None or url == "":
        return None
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if url.startswith("~~"):
        return settings.MEDIA_URL + url[2:]
    return static(url)