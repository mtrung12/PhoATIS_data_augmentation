# aug_utils.py
from typing import List, Tuple

def slots_to_spans(slots: List[str]) -> List[Tuple[int,int,str]]:
    """Convert BIO slots to spans: returns list of (start, end_exclusive, label_base)"""
    spans = []
    i = 0
    while i < len(slots):
        tag = slots[i]
        if tag.startswith("B-"):
            label = tag[2:]
            j = i + 1
            while j < len(slots) and slots[j].startswith("I-"):
                j += 1
            spans.append((i, j, label))
            i = j
        else:
            i += 1
    return spans

def apply_span_replacement(tokens, slots, span_idx, new_tokens, new_label):
    """
    Replace tokens[start:end] with new_tokens and adjust slot labels accordingly.
    new_label is like 'fromloc.city_name' -> we will produce B- then I-...
    Returns new_tokens_list, new_slots_list
    """
    start, end, _ = span_idx
    pre_t = tokens[:start]
    post_t = tokens[end:]
    new_toks = pre_t + new_tokens + post_t

    pre_s = slots[:start]
    post_s = slots[end:]
    if new_label is None:
        # keep O for new tokens
        new_s = ["O"] * len(new_tokens)
    else:
        if len(new_tokens) == 1:
            lab = "B-" + new_label
            new_s = [lab]
        else:
            new_s = ["B-" + new_label] + ["I-" + new_label] * (len(new_tokens) - 1)
    new_slots = pre_s + new_s + post_s
    return new_toks, new_slots

def spans_from_slots_with_indices(slots):
    # helper returns same as slots_to_spans but with original label included
    return slots_to_spans(slots)
