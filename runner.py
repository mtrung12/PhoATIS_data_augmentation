# runner.py
import argparse
from utils_io import load_phoatis_txt, save_phoatis_txt
from augment_paraphrase import simple_paraphrase_tokens
from augment_alias import alias_swaps
from augment_contrast import contrastive_depart_arrive
from augment_rare_slots import synthesize_rare_slots
from aug_utils import slots_to_spans
import copy
import random

def validate_alignment(tokens, slots):
    is_valid = len(tokens) == len(slots)
    if not is_valid:
        print(f"Validation Error: Tokens ({len(tokens)}) != Slots ({len(slots)})")
        print(f"Tokens: {tokens}")
        print(f"Slots: {slots}")
    return is_valid

def main(input_path, output_path, max_per_example=2, seed=42):
    random.seed(seed)
    items = load_phoatis_txt(input_path) 
    augmented = []
    stats = {"skipped_misaligned":0, "generated":0}
    
    for it in items:
        tokens = it.get("tokens")
        slots = it.get("slots")
        intent = it.get("intent", "")

        if not tokens or not slots:
            stats["skipped_misaligned"] += 1
            continue
            
        if not validate_alignment(tokens, slots):
            stats["skipped_misaligned"] += 1
            continue

        # Original example
        augmented.append({"tokens":tokens, "slots":slots, "intent": intent, "aug_reason": "original"})

        # apply augmentations; collect up to max_per_example per type
        local_aug = []
        
        # A) paraphrase
        pars = simple_paraphrase_tokens(tokens, slots)
        for toks, sots, reason in pars[:max_per_example]:
            if validate_alignment(toks, sots):
                augmented.append({"tokens":toks, "slots":sots, "intent": intent, "aug_reason": reason})
                stats["generated"] += 1

        # B) alias swaps
        als = alias_swaps(tokens, slots)
        for toks, sots, reason in als[:max_per_example]:
            if validate_alignment(toks, sots):
                augmented.append({"tokens":toks, "slots":sots, "intent": intent, "aug_reason": reason})
                stats["generated"] += 1

        # C) contrastive depart/arrive
        con = contrastive_depart_arrive(tokens, slots)
        for toks, sots, reason in con[:max_per_example]:
            if validate_alignment(toks, sots):
                augmented.append({"tokens":toks, "slots":sots, "intent": intent, "aug_reason": reason})
                stats["generated"] += 1

    # D) rare slot synthesis (global)
    synths = synthesize_rare_slots()
    for toks, sots, intent_tag, reason in synths:
        if validate_alignment(toks, sots):
            augmented.append({"tokens":toks, "slots":sots, "intent": intent_tag, "aug_reason": reason})
            stats["generated"] += 1

    save_phoatis_txt(augmented, output_path)
    print("DONE. Stats:", stats, "Total augmented saved:", len(augmented))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="path to original phoATIS .txt file (e.g., train.txt)")
    # ---> MODIFIED HELP TEXT <---
    parser.add_argument("--output", required=True, help="path to save augmented .txt file (e.g., train_aug.txt)")
    parser.add_argument("--max_per_example", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    main(args.input, args.output, args.max_per_example, args.seed)