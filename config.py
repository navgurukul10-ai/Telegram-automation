import os
from dotenv import load_dotenv

load_dotenv()

GROUPS_PER_ACCOUNT = int(os.getenv("GROUPS_PER_ACCOUNT_PER_DAY", 10))
MESSAGES_PER_GROUP = int(os.getenv("MESSAGES_PER_GROUP", 100))
CRAWL_DELAY = int(os.getenv("CRAWL_DELAY", 5))
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "False").lower() == "true"
SCRAPE_EXISTING_GROUPS = os.getenv("SCRAPE_EXISTING_GROUPS", "True").lower() == "true"
CATEGORY_FILTER = os.getenv("CATEGORY_FILTER", "").strip().lower()

# New: hard global cap across all accounts per day (defaults to 40)
GLOBAL_GROUPS_PER_DAY = int(os.getenv("GLOBAL_GROUPS_PER_DAY", 40))

# Collect accounts dynamically
ACCOUNTS = []
for i in range(1, 5):
    phone = os.getenv(f"ACCOUNT_{i}_PHONE")
    api_id = os.getenv(f"ACCOUNT_{i}_API_ID")
    api_hash = os.getenv(f"ACCOUNT_{i}_API_HASH")
    if phone and api_id and api_hash:
        ACCOUNTS.append({
            "phone": phone,
            "api_id": int(api_id),
            "api_hash": api_hash
        })
