# augment_paraphrase.py
from aug_utils import slots_to_spans, apply_span_replacement
from utils_io import whitespace_tokenize
import random

# Vietnamese paraphrase prefixes
PARAPHRASE_PREFIXES = [
    "làm_ơn", "vui_lòng", "tôi_muốn", "cho_tôi_biết", "tìm_cho_tôi", "cho_tôi_hỏi"
]

# Vietnamese verb swaps (using common verbs from the dataset)
PARAPHRASE_VERB_SWAPS = {
    "tìm": "hiển_thị",
    "hiển_thị": "liệt_kê",
    "liệt_kê": "tìm",
    "cho_tôi_biết": "tìm",
    "cho_tôi_xem": "hiển_thị"
}

def simple_paraphrase_tokens(tokens, slots):
    out = []
    
    # --- 1) polite prefix ---
    # Only add if the first token is not part of a slot
    if slots[0] == "O":
        prefix = random.choice(PARAPHRASE_PREFIXES)
        prefix_toks = prefix.split('_') # Handle multi-word prefixes like "cho_tôi_biết"
        
        new_tokens = prefix_toks + tokens
        new_slots = ["O"] * len(prefix_toks) + slots
        out.append((new_tokens, new_slots, "paraphrase_prefix"))

    # --- 2) verb swap for first non-slot token ---
    for i, t in enumerate(tokens):
        if slots[i] == "O" and t.lower() in PARAPHRASE_VERB_SWAPS:
            t2 = PARAPHRASE_VERB_SWAPS[t.lower()]
            
            # Handle potential multi-word tokens
            t2_toks = t2.split('_')
            
            new_tokens = tokens[:i] + t2_toks + tokens[i+1:]
            new_slots = slots[:i] + ["O"] * len(t2_toks) + slots[i+1:]
            
            out.append((new_tokens, new_slots, "paraphrase_verb_swap"))
            break # Only swap the first one
            
    return out