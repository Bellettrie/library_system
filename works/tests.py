from works.models import Publication


def create_work(title):
    return Publication.objects.create(title=title,
                                      is_translated=False,
                                      date_added='1900-01-01',
                                      hidden=False,
                                      old_id=0
                                      )
