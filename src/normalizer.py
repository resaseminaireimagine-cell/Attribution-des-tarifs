import re
import unicodedata

STOPWORDS = {
    "de", "du", "des", "la", "le", "les", "d", "l", "et", "en", "pour",
    "the", "of", "and", "a", "an"
}


def strip_accents(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text))
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def normalize_text(text: str) -> str:
    if text is None:
        return ""
    text = str(text).strip().lower()
    text = strip_accents(text)
    text = text.replace("&", " et ")
    text = re.sub(r"['’]", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def simplify_for_match(text: str) -> str:
    base = normalize_text(text)
    tokens = [t for t in base.split() if t not in STOPWORDS]
    return " ".join(tokens)


def normalize_tarif_label(value: str) -> str:
    if value is None:
        return ""
    v = normalize_text(value)
    mapping = {
        "gratuit": "Gratuit",
        "coutant": "Coûtant",
        "coutant ": "Coûtant",
        "academique": "Académique",
        "tarif academique": "Académique",
        "plein tarif": "Plein tarif",
    }
    return mapping.get(v, str(value).strip())
