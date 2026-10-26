from app.core.profanity import contains_bad_words


def test_detects_variations():
    assert contains_bad_words("que merda")
    assert contains_bad_words("QUE MERDA")
    assert contains_bad_words("m3rda")
    assert contains_bad_words("merrrrda")
    assert contains_bad_words("desgraçado")
    assert contains_bad_words("desgracado")


def test_allows_normal_text():
    assert not contains_bad_words("Olá, eu do futuro! Espero que você esteja bem.")
    #words that only contain a bad word inside them
    assert not contains_bad_words("curso de computação")
    assert not contains_bad_words("disputa")
