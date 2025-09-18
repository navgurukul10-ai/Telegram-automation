## Telegram Group Join & Scrape Automation

This project automates joining Telegram groups from `universal_groups.json` and scraping messages using Telethon. It supports multiple accounts, per-account and global daily limits, non-interactive session strings, and persists results to SQLite (`data/app.db`) and CSV/JSON files.

### Features
- Load groups from `data/universal_groups.json` or `universal_groups.json` (also supports singular filename) with optional category filter and priority sorting
- Robust join with handling for FloodWait, invalid invites, channel limits, and already-joined
- Non-interactive login via Telethon string sessions, with fallback to interactive login
- Message scraping with CSV/JSON/DB export
- Daily caps: per-account and global

### Setup
1. Create and fill an `.env` file based on `.env.example`.
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Optional: Generate session strings (recommended for non-interactive runs):
```bash
python scripts/generate_session.py
```
Paste resulting sessions into `.env` under `ACCOUNT_N_SESSION`.

### Config
See `.env.example` for all options including accounts, limits, and modes. Groups per account per day and a global cap are enforced automatically based on database history.

### Data
Place your groups in `data/universal_groups.json` (preferred) or `universal_groups.json`. Example file is provided at `data/universal_groups.json` with `link`, `category`, and `priority` fields.

### Run
```bash
python main.py
```

Logs are written to `logs/app.log`. Session files (if not using string sessions) are stored under `sessions/`.

### Notes
- Simulation mode can be enabled via `SIMULATION_MODE=true` to test without joining/scraping.
- Existing groups will be skipped using `data/joined_groups.json` and the SQLite database.

