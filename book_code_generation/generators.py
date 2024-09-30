from creators.models import CreatorLocationNumber


# A generator function gives a prefix of a book-code.
# The second value says whether the title is already included in the prefix
# If the title is already included, the title-part should not be added to the code.

# Generate a book_code for an item (or series).
def generate_code_from_author(item):
    pub = item.publication
    auth = pub.get_authors()
    if len(auth) > 0:
        author = auth[0].creator
        author_alias = author

        while author_alias is not None:
            cl = CreatorLocationNumber.objects.filter(creator=author_alias, location=item.location)
            if len(cl) == 1:
                code = author_alias.name[0] + "-" + str(cl[0].number)
                return item.location.category.code + "-" + code + "-", False

            author_alias = author_alias.is_alias_of
            if author_alias == author:
                break
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
        author_alias = author

        while author_alias is not None:
            cl = CreatorLocationNumber.objects.filter(creator=author_alias, location=item.location)
            if len(cl) == 1:
                code = author_alias.name[0] + "-" + str(cl[0].number)
                return prefix + "-" + code + "-", False

            author_alias = author_alias.is_alias_of
            if author_alias == author:
                break
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
