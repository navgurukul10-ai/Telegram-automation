import asyncio
import csv
import os
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

# Import our modules
from config import (
    ACCOUNTS, GROUPS_PER_ACCOUNT, MESSAGES_PER_GROUP, GLOBAL_GROUPS_PER_DAY,
    SIMULATION_MODE, LOG_FILE, LOG_LEVEL
)
from rate_limiter import rate_limiter
from ml_pipeline import ml_pipeline
from elasticsearch_client import es_client
from simulation_mode import (
    simulate_group_join, simulate_message_scraping, simulate_authentication,
    get_simulation_stats, log_simulation_summary
)
from utils import load_universal_groups

class AdvancedTelegramCrawler:
    """Advanced Telegram crawler with all enhanced features"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.clients = []
        self.stats = {
            "groups_joined": 0,
            "messages_scraped": 0,
            "job_posts_found": 0,
            "high_score_phones": 0,
            "errors": 0
        }
        
        # CSV files for data export
        self.groups_csv = "data/groups.csv"
        self.messages_csv = "data/messages.csv"
        self.phones_csv = "data/phones.csv"
        self.jobs_csv = "data/jobs.csv"
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Initialize CSV files
        self._init_csv_files()
    
    def _init_csv_files(self):
        """Initialize CSV files with headers"""
        # Groups CSV
        if not os.path.exists(self.groups_csv):
            with open(self.groups_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['account_phone', 'group_link', 'joined_date', 'messages_read', 'job_score', 'status'])
        
        # Messages CSV
        if not os.path.exists(self.messages_csv):
            with open(self.messages_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['group_link', 'message_id', 'sender_id', 'date', 'text', 'job_score', 'processed'])
        
        # Phones CSV
        if not os.path.exists(self.phones_csv):
            with open(self.phones_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['phone_number', 'job_posts_count', 'high_score_posts', 'last_seen'])
        
        # Jobs CSV
        if not os.path.exists(self.jobs_csv):
            with open(self.jobs_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['title', 'company', 'location', 'remote', 'fresher_friendly', 'technologies', 'job_score', 'contact_phones', 'source_group', 'date'])
    
    def _write_to_csv(self, filename: str, data: List):
        """Write data to CSV file"""
        try:
            with open(filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(data)
        except Exception as e:
            self.logger.error(f"Failed to write to CSV {filename}: {e}")
    
    async def initialize(self) -> bool:
        """Initialize all components"""
        try:
            # Setup logging
            logging.basicConfig(
                filename=LOG_FILE,
                level=getattr(logging, LOG_LEVEL.upper()),
                format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            )
            
            self.logger.info("Crawler initialization started")
            
            # Connect to Elasticsearch
            if not SIMULATION_MODE:
                es_connected = await es_client.connect()
                if es_connected:
                    await es_client.create_indices()
                    self.logger.info("Connected to Elasticsearch")
                else:
                    self.logger.warning("Elasticsearch not available, using CSV only")
            
            # Initialize Telegram clients
            await self._initialize_clients()
            
            self.logger.info("Crawler initialization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return False
    
    async def _initialize_clients(self):
        """Initialize Telegram clients with enhanced session management"""
        for i, account in enumerate(ACCOUNTS):
            try:
                session_name = f"sessions/{account['phone'].replace('+', '')}"
                client = TelegramClient(session_name, account['api_id'], account['api_hash'])
                
                if SIMULATION_MODE:
                    # Simulate authentication
                    auth_result = await simulate_authentication(account['phone'])
                    if not auth_result['success']:
                        self.logger.error(f"Simulated auth failed for {account['phone']}")
                        continue
                else:
                    # Real authentication
                    await client.start(phone=account['phone'])
                
                self.clients.append({
                    "client": client,
                    "phone": account['phone'],
                    "account_index": i
                })
                
                self.logger.info(f"Client initialized: {account['phone']}")
                
            except SessionPasswordNeededError:
                self.logger.error(f"Password required for {account['phone']} - manual intervention needed")
            except PhoneCodeInvalidError:
                self.logger.error(f"Invalid code for {account['phone']} - manual intervention needed")
            except Exception as e:
                self.logger.error(f"Failed to initialize client {account['phone']}: {e}")
                self.stats["errors"] += 1
    
    async def crawl_groups(self, group_links: List[str]) -> None:
        """Main crawling logic with enhanced features"""
        try:
            self.logger.info(f"Crawling started with {len(group_links)} groups")
            
            # Process each client
            for client_info in self.clients:
                if not self.clients:
                    break
                
                client = client_info["client"]
                phone = client_info["phone"]
                
                # Get groups for this client (limit per account)
                groups_for_client = group_links[:GROUPS_PER_ACCOUNT]
                group_links = group_links[GROUPS_PER_ACCOUNT:]  # Remove processed groups
                
                if not groups_for_client:
                    self.logger.info(f"No groups left for {phone}")
                    continue
                
                self.logger.info(f"Processing {len(groups_for_client)} groups for {phone}")
                
                # Process groups for this client
                for group_link in groups_for_client:
                    await self._process_group(client, phone, group_link)
                    
                    # Rate limiting
                    await rate_limiter.wait_for_group_join()
                    
                    # Check daily limits
                    if self.stats["groups_joined"] >= GLOBAL_GROUPS_PER_DAY:
                        self.logger.info("Daily limit reached")
                        break
                
                # Check if we've reached daily limit
                if self.stats["groups_joined"] >= GLOBAL_GROUPS_PER_DAY:
                    break
            
            self.logger.info(f"Crawling completed. Stats: {self.stats}")
            
        except Exception as e:
            self.logger.error(f"Crawling failed: {e}")
            self.stats["errors"] += 1
    
    async def _process_group(self, client: TelegramClient, phone: str, group_link: str) -> None:
        """Process a single group"""
        try:
            # Rate limiting
            await rate_limiter.wait_for_general_request()
            
            if SIMULATION_MODE:
                # Simulate group join
                join_result = await simulate_group_join(group_link)
                if not join_result['success']:
                    self.logger.warning(f"Failed to join group: {group_link}")
                    return
            else:
                # Real group join
                try:
                    await client.join_chat(group_link)
                    self.logger.info(f"Joined group: {group_link}")
                except Exception as e:
                    self.logger.error(f"Failed to join group {group_link}: {e}")
                    return
            
            # Record group join
            self.stats["groups_joined"] += 1
            join_date = datetime.now().strftime("%Y-%m-%d")
            
            # Write to CSV
            self._write_to_csv(self.groups_csv, [
                phone, group_link, join_date, 0, 0.0, "joined"
            ])
            
            # Store in Elasticsearch
            if not SIMULATION_MODE and es_client.client:
                group_data = {
                    "link": group_link,
                    "joined_at": datetime.now().isoformat(),
                    "account_phone": phone,
                    "messages_read": 0,
                    "job_score": 0.0,
                    "status": "joined"
                }
                await es_client.index_group(group_data)
            
            # Scrape messages
            await self._scrape_group_messages(client, phone, group_link)
            
        except Exception as e:
            self.logger.error(f"Failed to process group {group_link}: {e}")
            self.stats["errors"] += 1
    
    async def _scrape_group_messages(self, client: TelegramClient, phone: str, group_link: str) -> None:
        """Scrape messages from a group with ML processing"""
        try:
            # Rate limiting
            await rate_limiter.wait_for_message_read()
            
            if SIMULATION_MODE:
                # Simulate message scraping
                messages = await simulate_message_scraping(group_link, MESSAGES_PER_GROUP)
            else:
                # Real message scraping
                messages = []
                async for msg in client.iter_messages(group_link, limit=MESSAGES_PER_GROUP):
                    messages.append({
                        "id": msg.id,
                        "date": str(msg.date),
                        "sender_id": msg.sender_id,
                        "text": msg.message or ""
                    })
            
            if not messages:
                self.logger.info(f"No messages found in {group_link}")
                return
            
            self.logger.info(f"Scraped {len(messages)} messages from {group_link}")
            
            # Process messages with ML pipeline
            job_scores = []
            phone_stats = {}  # Track phone numbers
            
            for message in messages:
                # ML classification
                classification = ml_pipeline.classify_message(message)
                job_score = classification['job_score']
                job_scores.append(job_score)
                
                # Write message to CSV
                self._write_to_csv(self.messages_csv, [
                    group_link, message["id"], message["sender_id"], 
                    message["date"], message["text"], job_score, classification['processed']
                ])
                
                # Store in Elasticsearch
                if not SIMULATION_MODE and es_client.client:
                    message_data = {
                        "message_id": message["id"],
                        "group_link": group_link,
                        "sender_id": message["sender_id"],
                        "text": message["text"],
                        "date": message["date"],
                        "job_score": job_score,
                        "processed": classification['processed']
                    }
                    await es_client.index_message(message_data)
                
                # Track phone numbers
                for phone_num in classification['phone_numbers']:
                    if phone_num not in phone_stats:
                        phone_stats[phone_num] = {"count": 0, "high_score": 0}
                    phone_stats[phone_num]["count"] += 1
                    if job_score >= 0.7:
                        phone_stats[phone_num]["high_score"] += 1
                
                # Extract job data if it's a job post
                if classification['is_job_post']:
                    job_data = {
                        "title": f"Job Post from {group_link}",
                        "company": "Unknown",
                        "location": classification['location'] or "Unknown",
                        "remote": classification['remote'],
                        "fresher_friendly": classification['fresher_friendly'],
                        "technologies": ",".join(classification['technologies']),
                        "job_score": job_score,
                        "contact_phones": ",".join(classification['phone_numbers']),
                        "source_group": group_link,
                        "date": message["date"]
                    }
                    
                    # Write job to CSV
                    self._write_to_csv(self.jobs_csv, [
                        job_data["title"], job_data["company"], job_data["location"],
                        job_data["remote"], job_data["fresher_friendly"], job_data["technologies"],
                        job_data["job_score"], job_data["contact_phones"], job_data["source_group"],
                        job_data["date"]
                    ])
                    
                    # Store in Elasticsearch
                    if not SIMULATION_MODE and es_client.client:
                        await es_client.index_job(job_data)
                    
                    self.stats["job_posts_found"] += 1
                
                # Rate limiting between messages
                await rate_limiter.wait_for_message_read()
            
            # Calculate group job score
            group_score = ml_pipeline.calculate_group_score(messages)
            
            # Update group CSV with final stats
            self._write_to_csv(self.groups_csv, [
                phone, group_link, datetime.now().strftime("%Y-%m-%d"), 
                len(messages), group_score, "completed"
            ])
            
            # Store phone statistics
            for phone_num, stats in phone_stats.items():
                self._write_to_csv(self.phones_csv, [
                    phone_num, stats["count"], stats["high_score"], datetime.now().isoformat()
                ])
                
                # Store in Elasticsearch
                if not SIMULATION_MODE and es_client.client:
                    phone_data = {
                        "phone_number": phone_num,
                        "job_posts_count": stats["count"],
                        "high_score_posts": stats["high_score"],
                        "last_seen": datetime.now().isoformat()
                    }
                    await es_client.index_phone(phone_data)
                
                if stats["high_score"] > 0:
                    self.stats["high_score_phones"] += 1
            
            self.stats["messages_scraped"] += len(messages)
            
            self.logger.info(f"Completed processing {group_link}: {len(messages)} messages, job score: {group_score:.2f}")
            
        except Exception as e:
            self.logger.error(f"Failed to scrape messages from {group_link}: {e}")
            self.stats["errors"] += 1
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            # Disconnect clients
            for client_info in self.clients:
                if not SIMULATION_MODE:
                    await client_info["client"].disconnect()
            
            # Disconnect Elasticsearch
            if not SIMULATION_MODE and es_client.client:
                await es_client.disconnect()
            
            # Log final stats
            self.logger.info(f"Crawler cleanup completed. Final stats: {self.stats}")
            
            if SIMULATION_MODE:
                log_simulation_summary()
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
    
    def get_stats(self) -> Dict:
        """Get crawler statistics"""
        stats = self.stats.copy()
        if SIMULATION_MODE:
            stats.update(get_simulation_stats())
        return stats

# Main execution function
async def main():
    """Main execution function"""
    crawler = AdvancedTelegramCrawler()
    
    try:
        # Initialize
        if not await crawler.initialize():
            print("Failed to initialize crawler")
            return
        
        # Load groups to crawl
        groups = load_universal_groups()
        group_links = [g["link"] for g in groups]
        
        if not group_links:
            print("No groups to crawl")
            return
        
        print(f"Starting crawler with {len(group_links)} groups")
        
        # Run crawler
        await crawler.crawl_groups(group_links)
        
        # Print final stats
        stats = crawler.get_stats()
        print(f"Crawler completed. Stats: {stats}")
        
        # Print CSV file locations
        print(f"Data exported to CSV files:")
        print(f"- Groups: {crawler.groups_csv}")
        print(f"- Messages: {crawler.messages_csv}")
        print(f"- Phones: {crawler.phones_csv}")
        print(f"- Jobs: {crawler.jobs_csv}")
        
    except KeyboardInterrupt:
        print("Crawler interrupted by user")
    except Exception as e:
        print(f"Crawler failed: {e}")
    finally:
        await crawler.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
