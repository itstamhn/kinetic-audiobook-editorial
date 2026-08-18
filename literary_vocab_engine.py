# Unified Literary & C1/C2 Vocabulary Engine for Kinetic Audiobooks
import re
import os
import json
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
from wordfreq import zipf_frequency
from deep_translator import GoogleTranslator

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OXFORD_JSON_PATH = os.path.join(DATA_DIR, "oxford_5000.json")
COMMON_10K_PATH = os.path.join(DATA_DIR, "common_10k_english.json")
CACHE_PATH = os.path.join(DATA_DIR, "vocab_translations_cache.json")
OVERRIDES_PATH = os.path.join(BASE_DIR, "user_gloss_overrides.json")
KNOWN_WORDS_PATH = os.path.join(BASE_DIR, "user_known_words.txt")

os.makedirs(DATA_DIR, exist_ok=True)

oxford_levels = {}
if os.path.exists(OXFORD_JSON_PATH):
    with open(OXFORD_JSON_PATH, "r", encoding="utf-8") as f:
        oxford_levels = json.load(f)

common_10k = set()
if os.path.exists(COMMON_10K_PATH):
    with open(COMMON_10K_PATH, "r", encoding="utf-8") as f:
        common_10k = set(json.load(f))

known_words = set()
if os.path.exists(KNOWN_WORDS_PATH):
    with open(KNOWN_WORDS_PATH, "r", encoding="utf-8") as f:
        known_words = set(line.strip().lower() for line in f if line.strip() and not line.startswith("#"))

user_overrides = {}
if os.path.exists(OVERRIDES_PATH):
    with open(OVERRIDES_PATH, "r", encoding="utf-8") as f:
        user_overrides = json.load(f)

translation_cache = {}
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        translation_cache = json.load(f)

wnl = WordNetLemmatizer()
translator = GoogleTranslator(source="en", target="vi")

def save_translation_cache():
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(translation_cache, f, ensure_ascii=False, indent=2)

def is_common_or_basic(word: str) -> bool:
    """Returns True if word or any of its root lemmas belongs to A1-B2 or common daily English."""
    clean = re.sub(r"[^\w]", "", word).lower()
    if not clean or len(clean) < 3:
        return True
        
    if clean in known_words:
        return True
        
    if clean in common_10k:
        return True
        
    if clean in oxford_levels and oxford_levels[clean] in ["a1", "a2", "b1", "b2"]:
        return True
        
    # Check all POS lemmas (verb, noun, adjective, adverb)
    for pos in ["v", "n", "a", "r"]:
        lemma = wnl.lemmatize(clean, pos)
        if lemma in known_words or lemma in common_10k:
            return True
        if lemma in oxford_levels and oxford_levels[lemma] in ["a1", "a2", "b1", "b2"]:
            return True
            
    # Check common English inflection suffixes
    for suffix, repl in [("ly", ""), ("iness", "y"), ("ness", ""), ("able", ""), ("ing", ""), ("ed", ""), ("s", ""), ("es", "")]:
        if clean.endswith(suffix) and len(clean) > len(suffix) + 2:
            base = clean[:-len(suffix)] + repl
            if base in known_words or base in common_10k:
                return True
            if base in oxford_levels and oxford_levels[base] in ["a1", "a2", "b1", "b2"]:
                return True
                
    return False

def classify_word(raw_word: str, custom_name_blacklist: set = None) -> dict:
    """
    Analyzes a word. Returns None if filtered out, or a dict with:
    {
       "word": clean_word,
       "level": "C1 Advanced" | "C2 Mastery" | "Literary / Archaic" | "Lore / Domain",
       "zipf": float,
       "is_literary": bool
    }
    """
    clean = re.sub(r"[^\w]", "", raw_word).lower()
    
    if not clean or len(clean) < 3:
        return None
    if re.search(r"\d", clean):
        return None
    if clean in known_words:
        return None
    if custom_name_blacklist and clean in custom_name_blacklist:
        return None
        
    # Contractions & spoken artifacts
    if clean in ["hadnt", "hasnt", "shant", "shouldnt", "youll", "youve", "thered", "anyones", "everyones", "didnt", "wont", "cant", "couldnt", "wasnt", "werent"]:
        return None
        
    # Proper nouns: Capitalized in text and not a known lowercase literary word
    if raw_word and raw_word[0].isupper() and clean not in ["inadvertently", "perpetual", "magnificent", "indisposed", "flabbergasted", "inexhaustible", "presumptuous"]:
        if custom_name_blacklist and clean in custom_name_blacklist:
            return None
        # If capitalized and not in dictionary or overrides, treat as character/place name
        if not wn.synsets(clean) and clean not in oxford_levels and clean not in user_overrides:
            return None
            
    # Filter out A1-B2 & common 10,000 daily words
    if is_common_or_basic(clean):
        return None
        
    freq = round(zipf_frequency(clean, "en"), 2)
    
    # Determine level and literary classification
    ox_level = oxford_levels.get(clean)
    if not ox_level:
        for pos in ["v", "n", "a", "r"]:
            lemma = wnl.lemmatize(clean, pos)
            if lemma in oxford_levels:
                ox_level = oxford_levels[lemma]
                break
                
    # Classify category
    if ox_level == "c1":
        category = "C1 Advanced"
    elif ox_level == "c2":
        category = "C2 Mastery"
    elif freq <= 2.8:
        category = "Literary / Archaic"
    elif freq <= 3.85:
        category = "Literary / Rare"
    else:
        category = "Literary / Domain"
        
    # Allow all literary/archaic words (Zipf <= 3.85 or in overrides) or C1/C2 certified
    if ox_level in ["c1", "c2"] or freq <= 3.85 or clean in user_overrides:
        return {
            "word": clean,
            "raw": raw_word,
            "level": category,
            "zipf": freq,
            "is_literary": True
        }
        
    return None

def translate_literary_word(word: str) -> str:
    """Translates a literary word to Vietnamese with caching and manual override support."""
    clean = word.lower().strip()
    
    if clean in user_overrides:
        return user_overrides[clean]
        
    if clean in translation_cache:
        return translation_cache[clean]
        
    try:
        vi = translator.translate(clean)
        if vi:
            vi = vi.strip().lower()
            if len(vi.split()) > 3:
                vi = " ".join(vi.split()[:2])
            translation_cache[clean] = vi
            return vi
    except Exception:
        pass
        
    return None

import concurrent.futures

def extract_literary_vocabulary(words_list: list, custom_name_blacklist: set = None) -> dict:
    candidates = {}
    for item in words_list:
        raw_word = item["word"] if isinstance(item, dict) else str(item)
        classified = classify_word(raw_word, custom_name_blacklist)
        if classified:
            w = classified["word"]
            if w not in candidates:
                candidates[w] = classified

    # Identify words needing translation
    to_translate = [w for w in candidates if w not in user_overrides and w not in translation_cache]

    if to_translate:
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            future_to_word = {executor.submit(translate_literary_word, w): w for w in to_translate}
            for future in concurrent.futures.as_completed(future_to_word):
                pass  # translate_literary_word populates translation_cache

    save_translation_cache()

    vocab_map = {}
    for w, classified in candidates.items():
        vi = translate_literary_word(w)
        if vi:
            vocab_map[w] = {
                "translation": vi,
                "level": classified["level"],
                "zipf": classified["zipf"]
            }
    return vocab_map

if __name__ == "__main__":
    test_words = [
        "knowledgeable", "labeled", "labelled", "perpetual", "indisposed",
        "curdled", "flabbergasted", "scintillating", "provender", "mathom",
        "scabbard", "sepulchre", "noisome", "eldritch", "tenebrous",
        "waistcoat", "sundry", "throes", "presumptuous", "inexhaustible",
        "gossamer", "doughty", "caterwaul", "somnambulist"
    ]
    print("--- Testing Literary Vocabulary Engine ---")
    for tw in test_words:
        res = classify_word(tw)
        if res:
            vi = translate_literary_word(res["word"])
            print(f"  ✅ {res["word"]:16} | Level: {res["level"]:20} | Zipf: {res["zipf"]} | VN: {vi}")
        else:
            print(f"  ❌ {tw:16} | Filtered out (Basic/Common)")
