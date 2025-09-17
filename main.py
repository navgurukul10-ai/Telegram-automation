import asyncio
import logging
import os
from datetime import datetime
from config import ACCOUNTS, GROUPS_PER_ACCOUNT, MESSAGES_PER_GROUP, SIMULATION_MODE, SCRAPE_EXISTING_GROUPS, CRAWL_DELAY, GLOBAL_GROUPS_PER_DAY
from accounts import AccountManager
from utils import load_universal_groups
from group_manager import load_joined_groups, save_joined_groups, join_groups
from message_scraper import scrape_messages
from db import init_db, today_total_joins, today_joins_for_phone, all_joined_links

os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/app.log", level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

async def main():
    init_db()

    joined_groups = load_joined_groups()
    all_groups = load_universal_groups()

    # Filter out groups already joined in DB or JSON
    already_joined_db = await all_joined_links()
    already_joined_all = set(joined_groups) | set(already_joined_db)
    pending_links = [g["link"] for g in all_groups if g["link"] not in already_joined_all]

    manager = AccountManager(ACCOUNTS)
    client_items = await manager.init_clients()

    # Daily limits
    today = datetime.utcnow().strftime("%Y-%m-%d")
    # Use fixed global cap from config:
    global_cap = GLOBAL_GROUPS_PER_DAY
    total_today = await today_total_joins(today)
    remaining_global = max(0, global_cap - total_today)

    try:
        for item in client_items:
            if remaining_global <= 0:
                logging.info("Daily global cap reached. Skipping remaining accounts.")
                break
            client = item["client"]
            phone = item["phone"]

            # Per-account remaining
            acc_today = await today_joins_for_phone(today, phone)
            remaining_for_account = max(0, GROUPS_PER_ACCOUNT - acc_today)
            if remaining_for_account <= 0:
                logging.info(f"Per-account cap reached for {phone}. Skipping.")
                continue

            allowed = min(remaining_for_account, remaining_global)
            if allowed <= 0:
                continue

            # Slice the next set of groups uniquely for this account
            to_join = pending_links[:allowed]
            if not to_join:
                logging.info("No pending groups left to join.")
                break

            joined_today = await join_groups(
                client,
                to_join,
                allowed,
                joined_groups,
                SIMULATION_MODE,
                CRAWL_DELAY,
                phone
            )

            # Remove whatever we attempted (or at least the ones reported joined) from the pending queue
            for g in joined_today:
                if g in pending_links:
                    pending_links.remove(g)
                joined_groups.add(g)

            remaining_global -= len(joined_today)

            # Scrape newly joined groups
            for g in joined_today:
                await scrape_messages(client, g, MESSAGES_PER_GROUP, SIMULATION_MODE)

            # Optionally scrape messages from already joined groups
            if SCRAPE_EXISTING_GROUPS:
                for g in list(joined_groups):
                    await scrape_messages(client, g, MESSAGES_PER_GROUP, SIMULATION_MODE)

            save_joined_groups(joined_groups)
    finally:
        await manager.close_clients()

if __name__ == "__main__":
    asyncio.run(main())