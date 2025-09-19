#!/usr/bin/env python3
"""
Demo script to show message fetching with group information
"""

import asyncio
import sys
from message_scraper import scrape_messages

async def demo_scrape():
    """Demo function to show message scraping"""
    print("=" * 60)
    print("📱 DEMO: MESSAGE FETCHING WITH GROUP INFORMATION")
    print("=" * 60)
    
    # This is a demo - in real usage, you would have a Telegram client
    print("\n🎯 This demo shows how message scraping works:")
    print("   1. Connects to Telegram group")
    print("   2. Fetches messages with progress indicators")
    print("   3. Shows which group each message comes from")
    print("   4. Saves messages to multiple formats")
    print("   5. Displays detailed group information")
    
    print("\n📋 Message Information Captured:")
    print("   🏷️  Group Name/Link")
    print("   📅 Message Date")
    print("   👤 Sender ID")
    print("   🆔 Message ID")
    print("   💬 Message Text")
    
    print("\n💾 Data Storage Formats:")
    print("   📁 JSON: data/messages/groupname.json")
    print("   📊 CSV: data/messages.csv")
    print("   🗄️  Database: data/app.db")
    
    print("\n🚀 To start fetching messages:")
    print("   python3 main.py")
    
    print("\n📊 To view fetched messages:")
    print("   python3 simple_message_viewer.py stats")
    print("   python3 simple_message_viewer.py csv 20")
    print("   python3 simple_message_viewer.py db 10")
    
    print("\n🔍 To filter messages by group:")
    print("   python3 simple_message_viewer.py csv 50 job")
    print("   python3 simple_message_viewer.py db 20 tech")
    
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    asyncio.run(demo_scrape())
