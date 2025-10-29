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
            if not line:  
                if tokens:
                    if tokens:
                        intent = tokens.pop()
                        slots.pop()
                        items.append({"tokens": tokens, "slots": slots, "intent": intent})
                    tokens = []
                    slots = []
                continue

            parts = line.split()
            if len(parts) == 2:
                tokens.append(parts[0])
                slots.append(parts[1])
            elif len(parts) == 1: 
                tokens.append(parts[0])
                slots.append("O") 

    if tokens:
        intent = tokens.pop()
        slots.pop()
        items.append({"tokens": tokens, "slots": slots, "intent": intent})
        
    print(f"Loaded {len(items)} examples from {path}")
    return items

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
    return text.strip().split()