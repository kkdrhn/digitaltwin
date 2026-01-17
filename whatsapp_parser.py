
import json
import re
import os
from datetime import datetime

INPUT_FILE = "wpchat.txt"
OUTPUT_FILE = "newwp.jsonl"
TARGET_PERSONA_NAME = "twin"
MY_WHATSAPP_NAME = "." # WhatsApp'ta kendi adınız (mesajlarda görünen isim)
GAP_THRESHOLD_MINS = 5
SESSION_GAP_HOURS = 1

def parse_line(line):
    # Regex: 16.09.2024 15:27 - Sender: Message
    match = re.search(r'^(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}) - (.*?): (.*)$', line)
    if match:
        return match.group(1), match.group(2), match.group(3)
    return None, None, None

def strip_urls(text):
    return re.sub(r'https?://\S+', '', text).strip()

def clean_messages():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return []

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    raw_msgs = []
    for line in lines:
        ts_str, sender, content = parse_line(line.strip())
        if not ts_str:
            continue
        
        # Filter 1: Remove media markers and system messages
        if "<Medya dahil edilmedi>" in content:
            continue
        
        # Filter: Remove links
        cleaned_content = strip_urls(content)
        if not cleaned_content:
            continue
            
        # Standardize names
        if sender == MY_WHATSAPP_NAME:
            display_sender = "twin"
        else:
            display_sender = "User"

        raw_msgs.append({
            "ts": datetime.strptime(ts_str, "%d.%m.%Y %H:%M"),
            "sender": display_sender,
            "text": cleaned_content
        })
    
    return raw_msgs

def group_blocks(msgs):
    if not msgs:
        return []
        
    blocks = []
    current_block = {
        "sender": msgs[0]["sender"],
        "texts": [msgs[0]["text"]],
        "start_ts": msgs[0]["ts"],
        "end_ts": msgs[0]["ts"]
    }
    
    for i in range(1, len(msgs)):
        msg = msgs[i]
        last_ts = current_block["end_ts"]
        diff_mins = (msg["ts"] - last_ts).total_seconds() / 60.0
        
        if msg["sender"] == current_block["sender"] and diff_mins <= GAP_THRESHOLD_MINS:
            # Merge into current block
            current_block["texts"].append(msg["text"])
            current_block["end_ts"] = msg["ts"]
        else:
            # Finish current block and start new one
            current_block["text"] = ". ".join(current_block["texts"])
            blocks.append(current_block)
            current_block = {
                "sender": msg["sender"],
                "texts": [msg["text"]],
                "start_ts": msg["ts"],
                "end_ts": msg["ts"]
            }
            
    current_block["text"] = ". ".join(current_block["texts"])
    blocks.append(current_block)
    return blocks

def generate_dataset(blocks):
    entries = []
    
    for i in range(len(blocks)):
        block = blocks[i]
        
        # Sadece Twin'in cevap verdiği (response) anları veri seti yapıyoruz
        if block["sender"] != "twin":
            continue
            
        temp_context = []
        last_ref_ts = block["start_ts"]
        
        # Geriye dönük 5 bloğa kadar bakabiliriz (Daha geniş bağlam için)
        lookback = 5 
        current_idx = i - 1
        
        while len(temp_context) < lookback and current_idx >= 0:
            prev_block = blocks[current_idx]
            
            
            gap_hours = (last_ref_ts - prev_block["end_ts"]).total_seconds() / 3600.0
            if gap_hours > SESSION_GAP_HOURS:
                break
            
            
            
            if prev_block["sender"] != "twin":
                temp_context.append(f"{prev_block['sender']}: {prev_block['text']}")
            
            last_ref_ts = prev_block["start_ts"]
            current_idx -= 1
            
        if not temp_context:
            continue

        temp_context.reverse()
        
        context_str = "\n".join(temp_context)
        
        entry = {
            "instruction": f"Sen {TARGET_PERSONA_NAME} kişisisin. Karşı tarafın söylediklerine doğal, kısa ve kendi tarzında cevap ver.",
            "context": context_str,
            "response": block["text"] 
        }
        entries.append(entry)
        
    return entries

def main():
    print("Step 1: Cleaning messages...")
    msgs = clean_messages()
    print(f"Total cleaned messages: {len(msgs)}")
    
    print("Step 2: Grouping into blocks...")
    blocks = group_blocks(msgs)
    print(f"Total blocks: {len(blocks)}")
    
    print("Step 3: Generating dataset entries...")
    entries = generate_dataset(blocks)
    print(f"Total entries: {len(entries)}")
    
    print(f"Step 4: Writing to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            
    print("Done!")

if __name__ == "__main__":
    main()
