# augment_contrast.py
from aug_utils import slots_to_spans, apply_span_replacement
import copy

# label mapping (Slot labels are in English, so this map remains English)
DEPART_ARRIVE_MAP = {
    "depart_date": "arrive_date",
    "depart_time": "arrive_time",
    "depart_time_relative": "arrive_time_relative",
    "arrive_date": "depart_date",
    "arrive_time": "depart_time",
    "arrive_time_relative": "depart_time_relative",
    "return_date": "depart_date",
    "return_time": "depart_time"
}

# Vietnamese words to insert/replace
WORD_SWAP = {
    "khởi_hành": "đến",
    "đi": "đến",
    "đến": "khởi_hành",
    "hạ_cánh": "khởi_hành",
    "trở_về": "khởi_hành",
    "khứ_hồi": "một_chiều" # This is a conceptual swap
}

# Map for inserting Vietnamese prefix words if no swap word is found in the span
PREFIX_WORD_MAP = {
    "arrive_date": "đến",
    "arrive_time": "đến",
    "arrive_time_relative": "đến",
    "depart_date": "khởi_hành",
    "depart_time": "khởi_hành",
    "depart_time_relative": "khởi_hành",
    "depart": "khởi_hành", # Fallback
    "arrive": "đến"      # Fallback
}


def contrastive_depart_arrive(tokens, slots):
    augs = []
    spans = slots_to_spans(slots)
    for (start, end, label) in spans:
        base = label.split(".")[0]  # e.g., 'depart_date'
        mapped_base = DEPART_ARRIVE_MAP.get(base)
        
        if mapped_base:
            # 1) Change slot labels
            new_slots = slots.copy()
            for i in range(start, end):
                if new_slots[i].startswith("B-") or new_slots[i].startswith("I-"):
                    prefix, suffix = new_slots[i].split("-", 1)
                    # Replace base label with the mapped one
                    new_suffix = suffix.replace(base, mapped_base)
                    new_slots[i] = f"{prefix}-{new_suffix}"

            # 2) Find whether tokens include depart/arrive/return words to swap
            found_swap = False
            new_tokens = tokens.copy()
            for i in range(start, end):
                w = tokens[i].lower()
                if w in WORD_SWAP:
                    new_tokens[i] = WORD_SWAP[w]
                    found_swap = True
                    break
                    
            if not found_swap:
                # 3) If no swap, prefix the span with the mapped Vietnamese word
                prefix_word = PREFIX_WORD_MAP.get(mapped_base, mapped_base.split('_')[0])
                
                # Insert the prefix word *before* the span
                new_tokens = tokens[:start] + [prefix_word] + tokens[start:]
                new_slots = slots[:start] + ["O"] + new_slots[start:]
            
            augs.append((new_tokens, new_slots, f"contrast_{base}_to_{mapped_base}"))
            
    return augs