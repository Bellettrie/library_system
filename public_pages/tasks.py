from bellettrie_library_system.settings import MEDIA_ROOT
from public_pages.models import FileUpload


class SyncUploads:
    def exec(self):
        from os import listdir
        from os.path import isfile, join
        onlyfiles = set([f for f in listdir(MEDIA_ROOT) if isfile(join(MEDIA_ROOT, f))])

        knownfiles = FileUpload.objects.all()
        file_names = []
        for f in knownfiles:
            file_names.append(f.file.name)

        for f in onlyfiles:
            if f not in file_names:
                print("Added file {}".format(f))
                try:
                    FileUpload.objects.create(file=f)
                except Exception as e:
                    print(e)
        for f in knownfiles:
            if f.file.name not in onlyfiles:
                print("Removed file {}".format(f))
                f.delete()
