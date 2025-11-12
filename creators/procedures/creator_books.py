from creators.models import Creator
from works.models import Work


def get_books_for_author(creator: Creator):


    return Work.objects.all()
