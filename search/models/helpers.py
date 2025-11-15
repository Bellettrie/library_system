from book_code_generation.helpers import normalize_str
from search.models.search_word import SearchWord


def get_word_from_set(word: str, word_set: dict):
    """
        Given a dictionary of string -> SearchWord, get the word from the dictionary. This is an optimization for the search word generation function.
    """
    word = word.upper()
    w = word_set.get(word, None)
    if w is not None:
        return w

    word_set[word] = SearchWord.get_word(word)
    return word_set[word]


def clean_word(string):
    """
    Remove anything not alphanumeric from word.
    """
    string = normalize_str(string)
    return "".join(ch for ch in string if ch.isalnum() or ch == "*").upper()


def get_words_in_str(string):
    """
        Split string into spaces and
    """
    if string is None:
        return []
    string = string.replace("'", " ")
    z = string.strip().split(" ")
    result = []
    for w in z:
        w = clean_word(w)
        if len(w) > 1:
            result.append(w)
    return result
