# import json
# import os
# import logging
# import asyncio
# from urllib.parse import urlparse
# from telethon import functions
# from datetime import datetime
# from db import record_group_join

# JOINED_GROUPS_FILE = "data/joined_groups.json"

# def load_joined_groups():
#     if os.path.exists(JOINED_GROUPS_FILE):
#         try:
#             with open(JOINED_GROUPS_FILE, "r") as f:
#                 raw = f.read().strip()
#                 if not raw:
#                     return set()
#                 data = json.loads(raw)
#                 if isinstance(data, list):
#                     return set(data)
#         except Exception as e:
#             logging.warning(f"⚠️ Could not parse {JOINED_GROUPS_FILE}: {e}. Starting with empty set.")
#             return set()
#     return set()

# def save_joined_groups(joined_groups):
#     os.makedirs("data", exist_ok=True)
#     with open(JOINED_GROUPS_FILE, "w") as f:
#         json.dump(list(joined_groups), f, indent=2)

# async def _extract_join_target(client, link_or_username):
#     """Return a tuple (mode, value) where mode is 'invite' or 'public'.
#     - For invite links (t.me/+HASH or t.me/joinchat/HASH), return ('invite', HASH)
#     - For public links/usernames (t.me/username or username), return ('public', entity)
#     """
#     text = (link_or_username or "").strip()
#     if not text:
#         raise ValueError("Empty group link/username")

#     # Accept plain usernames too
#     if not text.startswith("http://") and not text.startswith("https://"):
#         entity = await client.get_entity(text)
#         return ("public", entity)

#     parsed = urlparse(text)
#     if parsed.netloc not in {"t.me", "telegram.me"}:
#         # Try resolving as entity directly
#         entity = await client.get_entity(text)
#         return ("public", entity)

#     path = (parsed.path or "/").lstrip("/")
#     if not path:
#         raise ValueError(f"Unrecognized Telegram link: {text}")

#     # Invite links: t.me/+HASH or t.me/joinchat/HASH
#     if path.startswith("+"):
#         return ("invite", path.lstrip("+"))
#     if path.lower().startswith("joinchat/"):
#         return ("invite", path.split("/", 1)[1])

#     # Otherwise treat as public username
#     username = path.split("/", 1)[0]
#     entity = await client.get_entity(username)
#     return ("public", entity)

# async def _append_group_csv(group_link, account_phone):
#     os.makedirs("data", exist_ok=True)
#     path = os.path.join("data", "groups.csv")
#     exists = os.path.exists(path)
#     with open(path, "a", newline="", encoding="utf-8") as f:
#         from csv import writer
#         w = writer(f)
#         if not exists:
#             w.writerow(["date", "group", "account_phone"])  # header
#         safe_name = group_link.replace("https://t.me/", "")
#         w.writerow([datetime.utcnow().isoformat(), safe_name, account_phone])

# async def join_groups(client, groups, count, joined_groups, simulation=False, delay=5, account_phone: str = ""):
#     joined_today = []
#     for group in groups:
#         if group in joined_groups:
#             continue
#         try:
#             if simulation:
#                 logging.info(f"[SIMULATION] Would join group: {group}")
#                 # Still log to CSV and DB for audit of planned joins
#                 await _append_group_csv(group, account_phone)
#                 await record_group_join(group, datetime.utcnow().isoformat(), account_phone)
#             else:
#                 mode, target = await _extract_join_target(client, group)
#                 if mode == "invite":
#                     await client(functions.messages.ImportChatInviteRequest(hash=target))
#                 else:
#                     await client(functions.channels.JoinChannelRequest(channel=target))
#                 logging.info(f"✅ Joined: {group}")
#                 await _append_group_csv(group, account_phone)
#                 await record_group_join(group, datetime.utcnow().isoformat(), account_phone)
#             joined_groups.add(group)
#             joined_today.append(group)
#             if len(joined_today) >= count:
#                 break
#             await asyncio.sleep(delay)
#         except Exception as e:
#             logging.warning(f"⚠️ Could not join {group}: {e}")
#             await asyncio.sleep(delay)
#     return joined_today

import json
import os
import logging
import asyncio
from urllib.parse import urlparse
from telethon import functions
from datetime import datetime
from db import record_group_join

JOINED_GROUPS_FILE = "data/joined_groups.json"

def load_joined_groups():
    if os.path.exists(JOINED_GROUPS_FILE):
        try:
            with open(JOINED_GROUPS_FILE, "r") as f:
                raw = f.read().strip()
                if raw:
                    data = json.loads(raw)
                    if isinstance(data, list):
                        return set(data)
        except Exception as e:
            logging.warning(f"⚠️ Could not parse {JOINED_GROUPS_FILE}: {e}. Starting empty.")
    return set()

def save_joined_groups(joined_groups):
    os.makedirs("data", exist_ok=True)
    with open(JOINED_GROUPS_FILE, "w") as f:
        json.dump(list(joined_groups), f, indent=2)

async def _extract_join_target(client, link_or_username):
    text = (link_or_username or "").strip()
    if not text:
        raise ValueError("Empty group link/username")
    if not text.startswith("http://") and not text.startswith("https://"):
        entity = await client.get_entity(text)
        return ("public", entity)
    parsed = urlparse(text)
    path = (parsed.path or "/").lstrip("/")
    if path.startswith("+"):
        return ("invite", path.lstrip("+"))
    if path.lower().startswith("joinchat/"):
        return ("invite", path.split("/", 1)[1])
    username = path.split("/", 1)[0]
    entity = await client.get_entity(username)
    return ("public", entity)

async def _append_group_csv(group_link, account_phone):
    os.makedirs("data", exist_ok=True)
    path = os.path.join("data", "groups.csv")
    exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        from csv import writer
        w = writer(f)
        if not exists:
            w.writerow(["date", "group", "account_phone"])
        safe_name = group_link.replace("https://t.me/", "")
        w.writerow([datetime.utcnow().isoformat(), safe_name, account_phone])

async def join_groups(client, groups, count, joined_groups, simulation=False, delay=5, account_phone: str = ""):
    joined_today = []
    for group in groups:
        if group in joined_groups:
            continue
        try:
            if not simulation:
                mode, target = await _extract_join_target(client, group)
                if mode == "invite":
                    await client(functions.messages.ImportChatInviteRequest(hash=target))
                else:
                    await client(functions.channels.JoinChannelRequest(channel=target))
                logging.info(f"✅ Joined: {group}")
            else:
                logging.info(f"[SIMULATION] Would join group: {group}")

            await _append_group_csv(group, account_phone)
            await record_group_join(group, datetime.utcnow().isoformat(), account_phone)
            joined_groups.add(group)
            joined_today.append(group)
            if len(joined_today) >= count:
                break
            await asyncio.sleep(delay)
        except Exception as e:
            logging.warning(f"⚠️ Could not join {group}: {e}")
            await asyncio.sleep(delay)
    return joined_today
