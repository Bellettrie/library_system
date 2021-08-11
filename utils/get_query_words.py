def get_query_words(query):
    if query is None:
        return None
    p_words = query.split(" ")
    words = []
    for word in p_words:
        if len(word) > 0:
            words.append(word)
    return words
