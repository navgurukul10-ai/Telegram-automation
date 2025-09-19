import asyncio
import logging
import os
import sys
from datetime import datetime
from config import ACCOUNTS, GROUPS_PER_ACCOUNT, MESSAGES_PER_GROUP, SIMULATION_MODE, SCRAPE_EXISTING_GROUPS, CRAWL_DELAY, GLOBAL_GROUPS_PER_DAY
from accounts import AccountManager
from utils import load_universal_groups
from group_manager import load_joined_groups, save_joined_groups, join_groups
from message_scraper import scrape_messages
from db import init_db, today_total_joins, today_joins_for_phone, all_joined_links

# Setup logging for both console and file
os.makedirs("logs", exist_ok=True)

# Configure logging for both console and file
file_handler = logging.FileHandler("logs/app.log")
console_handler = logging.StreamHandler(sys.stdout)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[file_handler, console_handler]
)

def print_startup_info():
    """Print startup information and configuration status"""
    print('=' * 60)
    print('🤖 TELEGRAM AUTOMATION BOT')
    print('=' * 60)
    print(f'📊 Groups per account: {GROUPS_PER_ACCOUNT}')
    print(f'💬 Messages per group: {MESSAGES_PER_GROUP}')
    print(f'⏱️  Crawl delay: {CRAWL_DELAY}s')
    print(f'🎯 Simulation mode: {"ON" if SIMULATION_MODE else "OFF"}')
    print(f'🌍 Global daily limit: {GLOBAL_GROUPS_PER_DAY}')
    print(f'📚 Scrape existing groups: {"YES" if SCRAPE_EXISTING_GROUPS else "NO"}')
    print('=' * 60)
    
    if not ACCOUNTS:
        print('❌ ERROR: No Telegram accounts configured!')
        print('💡 Please check your config.py file')
        return False
    
    print(f'✅ Found {len(ACCOUNTS)} configured accounts:')
    for i, account in enumerate(ACCOUNTS, 1):
        phone = account.get('phone', 'Unknown')
        print(f'   📱 Account {i}: {phone}')
    print('=' * 60)
    return True

async def main():
    """Main application function"""
    # Print startup information
    if not print_startup_info():
        print('❌ Configuration error. Exiting...')
        return
    
    try:
        print('\n🔄 Initializing application...')
        
        # Initialize database
        print('📊 Initializing database...')
        init_db()
        
        # Load data
        print('📂 Loading joined groups...')
        joined_groups = load_joined_groups()
        
        print('🌐 Loading universal groups...')
        all_groups = load_universal_groups()
        print(f'   Found {len(all_groups)} total groups')
        
        # Filter groups
        print('🔍 Filtering already joined groups...')
        already_joined_db = await all_joined_links()
        already_joined_all = set(joined_groups) | set(already_joined_db)
        pending_links = [g["link"] for g in all_groups if g["link"] not in already_joined_all]
        
        print(f'   Already joined: {len(already_joined_all)}')
        print(f'   Pending to join: {len(pending_links)}')
        
        if not pending_links:
            print('✅ All available groups have already been joined!')
            return
        
        # Initialize account manager
        print('🔐 Initializing Telegram clients...')
        manager = AccountManager(ACCOUNTS)
        client_items = await manager.init_clients()
        
        if not client_items:
            print('❌ Failed to initialize any Telegram clients!')
            return
        
        print(f'✅ Successfully initialized {len(client_items)} clients')
        
        # Check daily limits
        today = datetime.utcnow().strftime("%Y-%m-%d")
        global_cap = GLOBAL_GROUPS_PER_DAY
        total_today = await today_total_joins(today)
        remaining_global = max(0, global_cap - total_today)
        
        print(f'\n📈 Daily statistics for {today}:')
        print(f'   Total joins today: {total_today}/{global_cap}')
        print(f'   Remaining global: {remaining_global}')
        
        if remaining_global <= 0:
            print('⏰ Daily global limit reached. No more groups can be joined today.')
            return
        
        print(f'\n🚀 Starting automation process...')
        total_joined = 0
        total_scraped = 0
        
        try:
            for i, item in enumerate(client_items, 1):
                if remaining_global <= 0:
                    print('⏰ Global daily cap reached. Stopping.')
                    break
                    
                client = item["client"]
                phone = item["phone"]
                
                print(f'\n📱 Processing account {i}/{len(client_items)}: {phone}')
                
                # Check per-account limits
                acc_today = await today_joins_for_phone(today, phone)
                remaining_for_account = max(0, GROUPS_PER_ACCOUNT - acc_today)
                
                print(f'   Today\'s joins: {acc_today}/{GROUPS_PER_ACCOUNT}')
                print(f'   Remaining: {remaining_for_account}')
                
                if remaining_for_account <= 0:
                    print(f'   ⏰ Account daily limit reached. Skipping.')
                    continue
                
                # Calculate how many groups to join
                allowed = min(remaining_for_account, remaining_global)
                to_join = pending_links[:allowed]
                
                if not to_join:
                    print('   ℹ️  No pending groups left to join.')
                    break
                
                print(f'   🎯 Attempting to join {len(to_join)} groups...')
                
                # Join groups
                joined_today = await join_groups(
                    client, to_join, allowed, joined_groups, 
                    SIMULATION_MODE, CRAWL_DELAY, phone
                )
                
                print(f'   ✅ Successfully joined {len(joined_today)} groups')
                total_joined += len(joined_today)
                
                # Update tracking
                for g in joined_today:
                    if g in pending_links:
                        pending_links.remove(g)
                    joined_groups.add(g)
                
                remaining_global -= len(joined_today)
                
                # Scrape messages from newly joined groups
                if joined_today:
                    print(f'   �� Scraping messages from {len(joined_today)} new groups...')
                    for g in joined_today:
                        scraped = await scrape_messages(client, g, MESSAGES_PER_GROUP, SIMULATION_MODE)
                        if scraped:
                            total_scraped += len(scraped)
                
                # Optionally scrape existing groups
                if SCRAPE_EXISTING_GROUPS:
                    existing_groups = list(joined_groups)
                    if existing_groups:
                        print(f'   📚 Scraping messages from {len(existing_groups)} existing groups...')
                        for g in existing_groups:
                            scraped = await scrape_messages(client, g, MESSAGES_PER_GROUP, SIMULATION_MODE)
                            if scraped:
                                total_scraped += len(scraped)
                
                # Save progress
                save_joined_groups(joined_groups)
                print(f'   💾 Progress saved')
                
        finally:
            print('\n🔒 Closing Telegram clients...')
            await manager.close_clients()
        
        # Final statistics
        print(f'\n📊 FINAL STATISTICS:')
        print(f'   Groups joined: {total_joined}')
        print(f'   Messages scraped: {total_scraped}')
        print(f'   Simulation mode: {"ON" if SIMULATION_MODE else "OFF"}')
        
        if SIMULATION_MODE:
            print('   ⚠️  Note: This was a simulation run - no actual API calls were made')
        
        print('\n✅ Automation process completed successfully!')
        
    except KeyboardInterrupt:
        print('\n⚠️  Process interrupted by user')
    except Exception as e:
        print(f'\n❌ Error occurred: {str(e)}')
        logging.exception("Unexpected error in main function")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n👋 Goodbye!')
    except Exception as e:
        print(f'\n💥 Fatal error: {str(e)}')
        sys.exit(1)
