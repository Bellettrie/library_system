from django.db import models

# Create your models here.
from django.db.models import PROTECT

from members.models import Committee


#

def youtube_header():
    return """<div class="video-container">
<iframe class="video-frame" width="560" height="315" src="https://www.youtube-nocookie.com/embed/9TTleauNhkA?controls=0&rel=0" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>"""


class PublicPageGroup(models.Model):
    name = models.CharField(max_length=64)
    committees = models.ForeignKey(Committee, on_delete=PROTECT)


class PublicPage(models.Model):
    def exec_header(self):
        if self.custom_header == 'youtube':
            return youtube_header()
        return ''

    name = models.CharField(max_length=64)
    title = models.CharField(max_length=128)
    text = models.TextField()
    group = models.ForeignKey(PublicPageGroup, on_delete=PROTECT)
    custom_header = models.CharField(max_length=64, null=True, blank=True)
