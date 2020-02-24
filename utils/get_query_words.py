def get_query_words(request):
    query = request.GET.get('q')
    if query is None:
        return None
    p_words = query.split(" ")
    words = []
    for word in p_words:
        if len(word) > 2:
            words.append(word)
    return words
