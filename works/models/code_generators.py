from book_code_generation.generators import generate_code_from_author, generate_code_from_author_translated, \
    generate_code_abc, generate_code_from_title, generate_code_abc_translated

GENERATORS = {
    'author': generate_code_from_author,
    'author_translated': generate_code_from_author_translated,
    'abc': generate_code_abc,
    'abc_translated': generate_code_abc_translated,
    'title': generate_code_from_title,
}
