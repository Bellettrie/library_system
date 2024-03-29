# Source code for article:
# https://hakibenita.com/django-markdown

from typing import Optional
import re
import markdown
from markdown.inlinepatterns import LinkInlineProcessor, LINK_RE, ImageReferenceInlineProcessor, IMAGE_REFERENCE_RE, \
    IMAGE_LINK_RE, ImageInlineProcessor
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.urls import reverse, NoReverseMatch


class Error(Exception):
    pass


class InvalidMarkdown(Error):

    def __init__(self, error: str, value: Optional[str] = None) -> None:
        self.error = error
        self.value = value

    def __str__(self) -> str:
        if self.value is None:
            return self.error
        return f'{self.error} "{self.value}"'


def clean_link(href: str) -> str:
    if href.startswith('mailto:'):
        email_match = re.match('^(mailto:)?([^?]*)', href)
        if not email_match:
            raise InvalidMarkdown('Invalid mailto link', value=href)

        email = email_match.group(2)
        if email:
            try:
                EmailValidator()(email)
            except ValidationError:
                raise InvalidMarkdown('Invalid email address', value=email)

        return href

    # Remove fragments or query params before trying to match the url name
    static = False
    print(href)

    if href.startswith('~~'):
        static = True
        href = '/media/' + href[2:]

    z = href.split("|")
    href = z[0]
    args = []

    for part in z:
        if part != href:
            args.append(part)
    href_parts = re.search(r'#|\?', href)
    if href_parts:
        start_ix = href_parts.start()
        url_name, url_extra = href[:start_ix], href[start_ix:]
    else:
        url_name, url_extra = href, ''

    try:
        url = reverse(url_name, args=args)
    except NoReverseMatch:
        pass
    else:
        return url + url_extra

    parsed_url = urlparse(href)

    if not static and parsed_url.scheme not in ('http', 'https'):
        raise InvalidMarkdown('Must provide an absolute URL (be sure to include https:// or http://)', href)

    return href


class DjangoLinkInlineProcessor(LinkInlineProcessor):
    def getLink(self, data, index):
        href, title, index, handled = super().getLink(data, index)
        href = clean_link(href)
        return href, title, index, handled


class CustomImageLinkProcessor(ImageInlineProcessor):
    def getLink(self, data, index):
        href, title, index, handled = super().getLink(data, index)
        print(href, title, index)
        href = clean_link(href)
        return href, title, index, handled


class DjangoUrlExtension(markdown.Extension):
    def extendMarkdown(self, md, *args, **kwrags):
        md.inlinePatterns.register(DjangoLinkInlineProcessor(LINK_RE, md), 'link', 160)
        md.inlinePatterns.register(CustomImageLinkProcessor(IMAGE_LINK_RE, md), 'image_link', 140)
