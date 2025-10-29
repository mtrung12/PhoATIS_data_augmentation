# augment_alias.py
from aug_utils import slots_to_spans, apply_span_replacement
from utils_io import whitespace_tokenize
import random

# Vietnamese alias dictionary (based on phoATIS data)
ALIAS_MAP = {
    # canonical: [aliases...]
    "hà_nội": ["hn", "sân_bay_nội_bài", "nội_bài"],
    "thành_phố_hồ_chí_minh": ["tphcm", "sài_gòn", "sân_bay_tân_sơn_nhất", "tân_sơn_nhất"],
    "đà_nẵng": ["đn", "sân_bay_đà_nẵng"],
    "hải_phòng": ["hph", "sân_bay_cát_bi", "cát_bi"]
}

# map tokens -> canonical keys (Vietnamese)
TOKEN_TO_CANON = {
    "hà_nội": "hà_nội",
    "hn": "hà_nội",
    "nội_bài": "hà_nội",
    "sân_bay_nội_bài": "hà_nội",
    "thành_phố_hồ_chí_minh": "thành_phố_hồ_chí_minh",
    "hồ_chí_minh": "thành_phố_hồ_chí_minh",
    "tphcm": "thành_phố_hồ_chí_minh",
    "sài_gòn": "thành_phố_hồ_chí_minh",
    "tân_sơn_nhất": "thành_phố_hồ_chí_minh",
    "sân_bay_tân_sơn_nhất": "thành_phố_hồ_chí_minh",
    "đà_nẵng": "đà_nẵng",
    "đn": "đà_nẵng",
    "sân_bay_đà_nẵng": "đà_nẵng",
    "hải_phòng": "hải_phòng",
    "hph": "hải_phòng",
    "cát_bi": "hải_phòng",
    "sân_bay_cát_bi": "hải_phòng"
}

# Slot labels are in English, so these keywords are correct
CITY_SLOT_KEYWORDS = ["city_name", "airport_name", "state_name", "stoploc", "fromloc", "toloc"]

def find_canonical_key(span_tokens_lower):
    """Helper to find the canonical key from a list of span tokens."""
    # Try exact match of full span first
    full_span = "_".join(span_tokens_lower)
    if full_span in TOKEN_TO_CANON:
        return TOKEN_TO_CANON[full_span]
    
    # Try individual tokens
    for tok in span_tokens_lower:
        key = TOKEN_TO_CANON.get(tok)
        if key:
            return key
    return None

def alias_swaps(tokens, slots):
    augs = []
    spans = slots_to_spans(slots)
    
    for (start, end, label) in spans:
        # Only consider spans that include city or airport in label
        if any(k in label for k in CITY_SLOT_KEYWORDS):
            span_tokens = tokens[start:end]
            span_tokens_lower = [t.lower() for t in span_tokens]
            
            key = find_canonical_key(span_tokens_lower)
            
            if key and key in ALIAS_MAP:
                # Get all aliases *except* the one currently used
                current_alias_str = " ".join(span_tokens)
                aliases = [a for a in ALIAS_MAP[key] if a != current_alias_str and a != key]
                
                if not aliases:
                    # If no other aliases, swap to the canonical form
                    if key != current_alias_str:
                        aliases = [key]
                    else:
                        continue # Already is canonical, no other aliases

                # Pick one alias to swap with
                new_alias_str = random.choice(aliases)
                new_alias_tokens = new_alias_str.split("_") # Use underscore as per phoATIS format
                
                # Use apply_span_replacement util
                new_toks, new_slots = apply_span_replacement(tokens, slots, (start, end, label), new_alias_tokens, label)
                augs.append((new_toks, new_slots, f"alias_swap_{key}"))

    return augs