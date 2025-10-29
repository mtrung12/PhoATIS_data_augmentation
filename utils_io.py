# utils_io.py
import json

def load_phoatis_txt(path):
    """
    Loads a phoATIS .txt file (token slot\n...intent\n\n) into a list of examples.
    """
    items = []
    with open(path, "r", encoding="utf-8") as f:
        tokens = []
        slots = []
        for line in f:
            line = line.strip()
            if not line:  # Empty line indicates end of an example
                if tokens:
                    # Based on file format, the intent is the last line before the blank line.
                    if tokens:
                        intent = tokens.pop()
                        slots.pop() # Remove the 'O' tag associated with the intent
                        items.append({"tokens": tokens, "slots": slots, "intent": intent})
                    tokens = []
                    slots = []
                continue

            parts = line.split()
            if len(parts) == 2:
                tokens.append(parts[0])
                slots.append(parts[1])
            elif len(parts) == 1: # This is likely the intent line
                tokens.append(parts[0])
                slots.append("O") # Placeholder for the intent line's "slot"

    # Add the last example if file doesn't end with a blank line
    if tokens:
        intent = tokens.pop()
        slots.pop()
        items.append({"tokens": tokens, "slots": slots, "intent": intent})
        
    print(f"Loaded {len(items)} examples from {path}")
    return items

def save_phoatis_txt(items, path):
    """
    Saves a list of augmented examples to the phoATIS .txt format.
    Each item is a dict: {"tokens": [...], "slots": [...], "intent": "..."}
    """
    with open(path, "w", encoding="utf-8") as f:
        for item in items:
            tokens = item.get("tokens", [])
            slots = item.get("slots", [])
            intent = item.get("intent", "")
            
            if not tokens or not slots or not intent:
                continue # Skip invalid entries
                
            if len(tokens) != len(slots):
                print(f"Warning: Skipping misaligned item. Tokens: {len(tokens)}, Slots: {len(slots)}")
                continue
                
            # Write token slot pairs
            for tok, slot in zip(tokens, slots):
                f.write(f"{tok} {slot}\n")
            
            # Write the intent
            f.write(f"{intent}\n")
            
            # Write the blank line separator
            f.write("\n")
    print(f"Saved {len(items)} examples to {path} in phoATIS .txt format")


# --- These functions are kept in case you need them, but are not used by runner.py anymore ---
def load_jsonl(path):
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))
    return items

def save_jsonl(items, path):
    with open(path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

def whitespace_tokenize(text):
    # This dataset is already tokenized with underscores, so we just split.
    return text.strip().split()