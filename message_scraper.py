import json
import os
import logging
import csv
from db import record_messages

async def scrape_messages(client, group, limit=100, simulation=False):
    """Scrape messages from a Telegram group with detailed logging"""
    print(f"\n📝 Starting message scraping from: {group}")
    print(f"   📊 Limit: {limit} messages")
    print(f"   🎯 Simulation: {'ON' if simulation else 'OFF'}")
    
    messages = []
    if simulation:
        print(f"   [SIMULATION] Would scrape {limit} messages from {group}")
        logging.info(f"[SIMULATION] Would scrape {limit} messages from {group}")
        return []

    try:
        print(f"   🔄 Fetching messages...")
        message_count = 0
        async for msg in client.iter_messages(group, limit=limit):
            message_count += 1
            if message_count % 10 == 0:  # Progress indicator every 10 messages
                print(f"   📥 Fetched {message_count} messages...")
            
            messages.append({
                "id": msg.id,
                "date": str(msg.date),
                "sender_id": msg.sender_id,
                "text": msg.message
            })
        
        print(f"   ✅ Successfully fetched {len(messages)} messages")
        
    except Exception as e:
        print(f"   ❌ Failed to scrape {group}: {e}")
        logging.warning(f"⚠️ Failed to scrape {group}: {e}")
        return []

    # Save to JSON
    print(f"   💾 Saving messages to JSON...")
    os.makedirs("data/messages", exist_ok=True)
    safe_name = group.replace("https://t.me/", "")
    json_path = f"data/messages/{safe_name}.json"
    with open(json_path, "w") as f:
        json.dump(messages, f, indent=2)
    print(f"   📁 Saved to: {json_path}")

    # Save to CSV
    print(f"   💾 Saving messages to CSV...")
    os.makedirs("data", exist_ok=True)
    csv_path = os.path.join("data", "messages.csv")
    file_exists = os.path.exists(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["date", "group", "message_id", "sender_id", "text"])  # header
        for m in messages:
            # Clean text for CSV
            text = (m["text"] or "").replace("\n", " ").replace("\r", " ")
            writer.writerow([m["date"], safe_name, m["id"], m["sender_id"], text])
    print(f"   📁 Appended to: {csv_path}")

    # Save to Database
    print(f"   💾 Saving messages to database...")
    try:
        await record_messages(group, messages)
        print(f"   ✅ Database updated successfully")
    except Exception as e:
        print(f"   ⚠️ Database error: {e}")
        logging.warning(f"⚠️ Failed to write messages to DB for {group}: {e}")

    print(f"   🎉 Completed! Total messages saved: {len(messages)}")
    logging.info(f"📥 Saved {len(messages)} messages from {group}")
    return messages
