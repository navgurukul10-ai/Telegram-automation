import json
import os
import logging
import csv
from db import record_messages
from telethon.errors import FloodWaitError

async def scrape_messages(client, group, limit=100, simulation=False):
    messages = []
    if simulation:
        logging.info(f"[SIMULATION] Would scrape {limit} messages from {group}")
        return []

    try:
        async for msg in client.iter_messages(group, limit=limit):
            messages.append({
                "id": msg.id,
                "date": str(msg.date),
                "sender_id": msg.sender_id,
                "text": msg.message
            })
    except FloodWaitError as e:
        wait_seconds = int(getattr(e, 'seconds', 60))
        logging.warning(f"⏳ Flood wait for {wait_seconds}s while scraping {group}")
        return []
    except Exception as e:
        logging.warning(f"⚠️ Failed to scrape {group}: {e}")
        return []

    os.makedirs("data/messages", exist_ok=True)
    safe_name = group.replace("https://t.me/", "")
    with open(f"data/messages/{safe_name}.json", "w") as f:
        json.dump(messages, f, indent=2)

    # CSV export
    os.makedirs("data", exist_ok=True)
    csv_path = os.path.join("data", "messages.csv")
    file_exists = os.path.exists(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["date", "group", "message_id", "sender_id", "text"])  # header
        for m in messages:
            writer.writerow([m["date"], safe_name, m["id"], m["sender_id"], (m["text"] or "").replace("\n", " ")])

    # DB export
    try:
        await record_messages(group, messages)
    except Exception as e:
        logging.warning(f"⚠️ Failed to write messages to DB for {group}: {e}")

    logging.info(f"📥 Saved {len(messages)} messages from {group}")
    return messages
