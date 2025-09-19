import os
from dotenv import load_dotenv

load_dotenv()

# Basic Configuration
GROUPS_PER_ACCOUNT = int(os.getenv("GROUPS_PER_ACCOUNT_PER_DAY", 10))
MESSAGES_PER_GROUP = int(os.getenv("MESSAGES_PER_GROUP", 100))
CRAWL_DELAY = int(os.getenv("CRAWL_DELAY", 5))
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "False").lower() == "true"
SCRAPE_EXISTING_GROUPS = os.getenv("SCRAPE_EXISTING_GROUPS", "True").lower() == "true"
CATEGORY_FILTER = os.getenv("CATEGORY_FILTER", "").strip().lower()
GLOBAL_GROUPS_PER_DAY = int(os.getenv("GLOBAL_GROUPS_PER_DAY", 40))

# Rate Limiting (Human-like behavior)
MIN_DELAY = float(os.getenv("MIN_DELAY", 2.0))
MAX_DELAY = float(os.getenv("MAX_DELAY", 8.0))
MESSAGE_DELAY = float(os.getenv("MESSAGE_DELAY", 1.0))
GROUP_JOIN_DELAY = float(os.getenv("GROUP_JOIN_DELAY", 5.0))

# Elasticsearch Configuration (Local)
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
ES_PORT = int(os.getenv("ELASTICSEARCH_PORT", 9200))
ES_USERNAME = os.getenv("ELASTICSEARCH_USERNAME")
ES_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")
ES_USE_SSL = os.getenv("ELASTICSEARCH_USE_SSL", "False").lower() == "true"

# Proxy Configuration (Optional)
PROXY_1_HOST = os.getenv("PROXY_1_HOST")
PROXY_1_PORT = int(os.getenv("PROXY_1_PORT", 8080))
PROXY_1_USERNAME = os.getenv("PROXY_1_USERNAME")
PROXY_1_PASSWORD = os.getenv("PROXY_1_PASSWORD")

PROXY_2_HOST = os.getenv("PROXY_2_HOST")
PROXY_2_PORT = int(os.getenv("PROXY_2_PORT", 8080))
PROXY_2_USERNAME = os.getenv("PROXY_2_USERNAME")
PROXY_2_PASSWORD = os.getenv("PROXY_2_PASSWORD")

# ML Configuration
JOB_KEYWORDS = [
    "job", "hiring", "career", "position", "opening", "vacancy",
    "fresher", "intern", "internship", "full-time", "part-time",
    "remote", "work from home", "wfh", "developer", "engineer"
]

TECH_KEYWORDS = [
    "python", "javascript", "react", "node", "java", "html", "css",
    "frontend", "backend", "fullstack", "devops", "aws", "docker"
]

MIN_CONFIDENCE_SCORE = float(os.getenv("MIN_CONFIDENCE_SCORE", 0.7))

# Telegram Accounts Configuration
ACCOUNTS = [
    {
        'name': 'Account 1',
        'phone': '+919794670665',
        'api_id': 24242582,
        'api_hash': 'd8a500dd4f6956793a0be40ac48c1669',
        'session_name': 'session_account1'
    },
    {
        'name': 'Account 2',
        'phone': '+917398227455',
        'api_id': 23717746,
        'api_hash': '23f3b527b36bf24d95435d245e73b270',
        'session_name': 'session_account2'
    },
    {
        'name': 'Account 3',
        'phone': '+919140057096',
        'api_id': 29261262,
        'api_hash': '884a43e2719d86d9023d9a82bc61db58',
        'session_name': 'session_account3'
    },
    {
        'name': 'Account 4',
        'phone': '+917828629905',
        'api_id': 29761042,
        'api_hash': 'c140669550a74b751993c941b2ab0aa7',
        'session_name': 'session_account4'
    }
]

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/crawler.log")
LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", 10485760))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))

# Simulation Mode Settings
SIMULATION_SPEED_MULTIPLIER = float(os.getenv("SIMULATION_SPEED_MULTIPLIER", 100.0))
