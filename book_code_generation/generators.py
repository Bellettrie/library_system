from book_code_generation.location_number_creation import CutterCodeRange
from creators.models import CreatorLocationNumber


# A generator function gives a prefix of a book-code.
# The second value says whether the title is already included in the prefix
# If the title is already included, the title-part should not be added to the code.

# Generate a book_code for an item (or series).
def generate_code_from_author(item):
    pub = item.publication
    if hasattr(pub, 'location_code') and pub.location_code is not None:
        return item.location.category.code + "-" + pub.location_code.letter + "-" + str(
            pub.location_code.number) + "-", True
    auth = pub.get_authors()
    if len(auth) > 0:
        author = auth[0].creator

        code = "?" + CutterCodeRange.get_cutter_number(author.name).generated_affix + "?"
        cl = CreatorLocationNumber.objects.filter(creator=author, location=item.location)

        if len(cl) == 1:
            code = author.name[0] + "-" + str(cl[0].number)
        else:
            if author.is_alias_of is not None and author.is_alias_of != author:
                my_author = author.is_alias_of
                cl = CreatorLocationNumber.objects.filter(creator=my_author, location=item.location)
                if len(cl) == 1:
                    code = my_author.name[0] + "-" + str(cl[0].number)
        return item.location.category.code + "-" + code + "-", False
    return "Lacks info to generate code", True


# Generate a code for a translated item.
def generate_code_from_author_translated(item):
    pub = item.publication
    prefix = "N"
    if pub.is_translated:
        prefix = "V"
    auth = item.publication.get_authors()
    if len(auth) > 0:
        author = auth[0].creator

        code = CutterCodeRange.get_cutter_number(author.name).generated_affix
        cl = CreatorLocationNumber.objects.filter(creator=author, location=item.location)

        if len(cl) == 1:
            code = author.name[0] + "-" + str(cl[0].number)

        return prefix + "-" + code + "-", False
    return "Lacks info to generate code", True


# Get code prefix for ABC-books.
def generate_code_abc(item):
    return item.location.category.code + "-ABC-", False


# Get code prefix for ABC-books.
def generate_code_abc_translated(item):
    pub = item.publication
    prefix = "N"
    if pub.is_translated:
        prefix = "V"
    return prefix + "-ABC-", False


# Generate code based on title.
def generate_code_from_title(item):
    title = item.publication.title[0:4].upper()
    if item.location.category.code == "":
        return title, True
    else:
        return item.location.category.code + "-" + title + "-", True
