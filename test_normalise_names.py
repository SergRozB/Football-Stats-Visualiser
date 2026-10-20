import unicodedata, re
from rapidfuzz import fuzz

def normalise(name: str) -> str:
    if not isinstance(name, str):
        return ""
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.lower()
    name = re.sub(r"[^a-z\s]", " ", name) # drop punctuation
    name = re.sub(r"\b(jr|sr|ii|iii)\b", "", name) # drop suffixes
    return re.sub(r"\s+", " ", name).strip()

print(fuzz.ratio("milan uri", "milan djuric"))