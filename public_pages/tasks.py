from bellettrie_library_system.settings import MEDIA_ROOT
from public_pages.models import FileUpload


class SyncUploads:
    def exec(self):
        print("HIT")
        from os import listdir
        from os.path import isfile, join
        onlyfiles = set([f for f in listdir(MEDIA_ROOT) if isfile(join(MEDIA_ROOT, f))])

        knownfiles = FileUpload.objects.all()
        knownfilenames = map(lambda x: x.file.name, knownfiles)
        for f in onlyfiles:
            if f not in knownfilenames:
                 FileUpload.objects.create(file=f)

        for f in knownfiles:
            if f.file.name not in onlyfiles:
                f.delete()