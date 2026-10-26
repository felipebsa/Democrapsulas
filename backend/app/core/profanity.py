import re
import unicodedata
from pathlib import Path

#one word per line, lines starting with # are ignored
WORDS_FILE = Path(__file__).parent / "bad_words.txt"

LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"})


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.translate(LEET)
    #"merrrda" -> "merda"
    return re.sub(r"(.)\1+", r"\1", text)


def load_words() -> set[str]:
    lines = WORDS_FILE.read_text(encoding="utf-8").splitlines()
    return {normalize(line.strip()) for line in lines if line.strip() and not line.startswith("#")}


BAD_WORDS = load_words()


def contains_bad_words(text: str) -> bool:
    words = re.findall(r"[a-z]+", normalize(text))
    return any(word in BAD_WORDS for word in words)
