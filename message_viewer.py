#!/usr/bin/env python3
"""
Message Viewer Tool - View messages with group information
Usage: python3 message_viewer.py [options]
"""

import csv
import json
import os
import sys
import sqlite3
from datetime import datetime
import argparse

def print_banner():
    """Print application banner"""
    print("=" * 80)
    print("📱 TELEGRAM MESSAGE VIEWER")
    print("=" * 80)

def view_csv_messages(csv_file="data/messages.csv", limit=50, group_filter=None):
    """View messages from CSV file"""
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return
    
    print(f"\n📊 Viewing messages from CSV: {csv_file}")
    print(f"📋 Limit: {limit} messages")
    if group_filter:
        print(f"🔍 Filter: Group contains '{group_filter}'")
    print("-" * 80)
    
    messages = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if group_filter and group_filter.lower() not in row.get('group', '').lower():
                continue
            messages.append(row)
    
    if not messages:
        print("📭 No messages found")
        return
    
    # Show latest messages first
    messages = messages[-limit:] if len(messages) > limit else messages
    
    for i, msg in enumerate(messages, 1):
        group = msg.get('group', 'Unknown')
        date = msg.get('date', 'Unknown')
        text = msg.get('text', 'No text')
        sender_id = msg.get('sender_id', 'Unknown')
        message_id = msg.get('message_id', 'Unknown')
        
        print(f"\n📨 Message #{i}")
        print(f"   🏷️  Group: {group}")
        print(f"   📅 Date: {date}")
        print(f"   👤 Sender ID: {sender_id}")
        print(f"   🆔 Message ID: {message_id}")
        print(f"   💬 Text: {text[:200]}{'...' if len(text) > 200 else ''}")
        print("-" * 40)

def view_json_messages(json_dir="data/messages", limit=50):
    """View messages from JSON files"""
    if not os.path.exists(json_dir):
        print(f"❌ JSON directory not found: {json_dir}")
        return
    
    print(f"\n📊 Viewing messages from JSON directory: {json_dir}")
    print(f"📋 Limit: {limit} messages per group")
    print("-" * 80)
    
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    
    if not json_files:
        print("📭 No JSON message files found")
        return
    
    for json_file in json_files[:10]:  # Limit to 10 groups for display
        group_name = json_file.replace('.json', '')
        file_path = os.path.join(json_dir, json_file)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
            print(f"\n🏷️  GROUP: {group_name}")
            print(f"📊 Total messages: {len(messages)}")
            print("-" * 40)
            
            # Show latest messages
            recent_messages = messages[-limit:] if len(messages) > limit else messages
            
            for i, msg in enumerate(recent_messages, 1):
                date = msg.get('date', 'Unknown')
                text = msg.get('text', 'No text')
                sender_id = msg.get('sender_id', 'Unknown')
                message_id = msg.get('id', 'Unknown')
                
                print(f"\n📨 Message #{i}")
                print(f"   📅 Date: {date}")
                print(f"   👤 Sender ID: {sender_id}")
                print(f"   🆔 Message ID: {message_id}")
                print(f"   💬 Text: {text[:150]}{'...' if len(text) > 150 else ''}")
                print("-" * 30)
                
        except Exception as e:
            print(f"❌ Error reading {json_file}: {e}")

def view_db_messages(db_file="data/app.db", limit=50, group_filter=None):
    """View messages from SQLite database"""
    if not os.path.exists(db_file):
        print(f"❌ Database file not found: {db_file}")
        return
    
    print(f"\n📊 Viewing messages from database: {db_file}")
    print(f"📋 Limit: {limit} messages")
    if group_filter:
        print(f"🔍 Filter: Group contains '{group_filter}'")
    print("-" * 80)
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check if messages table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
        if not cursor.fetchone():
            print("❌ Messages table not found in database")
            conn.close()
            return
        
        # Query messages
        query = "SELECT group_link, message_id, sender_id, date, text FROM messages"
        params = []
        
        if group_filter:
            query += " WHERE group_link LIKE ?"
            params.append(f"%{group_filter}%")
        
        query += " ORDER BY date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        messages = cursor.fetchall()
        
        if not messages:
            print("📭 No messages found in database")
            conn.close()
            return
        
        print(f"📊 Found {len(messages)} messages")
        
        for i, (group_link, message_id, sender_id, date, text) in enumerate(messages, 1):
            print(f"\n📨 Message #{i}")
            print(f"   🏷️  Group: {group_link}")
            print(f"   📅 Date: {date}")
            print(f"   👤 Sender ID: {sender_id}")
            print(f"   🆔 Message ID: {message_id}")
            print(f"   💬 Text: {text[:200]}{'...' if len(text) > 200 else ''}")
            print("-" * 40)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")

def show_group_stats():
    """Show statistics about groups and messages"""
    print("
📊 GROUP AND MESSAGE STATISTICS")
    print("=" * 50)
    
    # CSV stats
    if os.path.exists("data/messages.csv"):
        with open("data/messages.csv", 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            csv_messages = list(reader)
        
        if csv_messages:
            groups = set(msg.get('group', '') for msg in csv_messages)
            print(f"📁 CSV Messages: {len(csv_messages)} total")
            print(f"🏷️  CSV Groups: {len(groups)} unique groups")
        else:
            print("📁 CSV Messages: 0")
    else:
        print("📁 CSV Messages: File not found")
    
    # JSON stats
    if os.path.exists("data/messages"):
        if os.path.isdir("data/messages"):
            json_files = [f for f in os.listdir("data/messages") if f.endswith('.json')]
            total_json_messages = 0
            for json_file in json_files:
                try:
                    with open(os.path.join("data/messages", json_file), 'r') as f:
                        messages = json.load(f)
                        total_json_messages += len(messages)
                except:
                    pass
            print(f"📁 JSON Messages: {total_json_messages} total")
            print(f"🏷️  JSON Groups: {len(json_files)} files")
        else:
            print("📁 JSON Messages: data/messages is a file, not a directory")
    else:
        print("📁 JSON Messages: Directory not found")
    
    # Database stats
    if os.path.exists("data/app.db"):
        try:
            conn = sqlite3.connect("data/app.db")
            cursor = conn.cursor()
            
            # Count messages
            cursor.execute("SELECT COUNT(*) FROM messages")
            db_message_count = cursor.fetchone()[0]
            
            # Count unique groups
            cursor.execute("SELECT COUNT(DISTINCT group_link) FROM messages")
            db_group_count = cursor.fetchone()[0]
            
            print(f"📁 Database Messages: {db_message_count} total")
            print(f"🏷️  Database Groups: {db_group_count} unique groups")
            
            conn.close()
        except Exception as e:
            print(f"📁 Database Messages: Error - {e}")
    else:
        print("📁 Database Messages: File not found")
def main():
    parser = argparse.ArgumentParser(description='View Telegram messages with group information')
    parser.add_argument('--source', choices=['csv', 'json', 'db', 'all'], default='all',
                       help='Source to view messages from')
    parser.add_argument('--limit', type=int, default=20,
                       help='Number of messages to show (default: 20)')
    parser.add_argument('--group', type=str,
                       help='Filter messages by group name')
    parser.add_argument('--stats', action='store_true',
                       help='Show statistics only')
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.stats:
        show_group_stats()
        return
    
    if args.source in ['csv', 'all']:
        view_csv_messages(limit=args.limit, group_filter=args.group)
    
    if args.source in ['json', 'all']:
        view_json_messages(limit=args.limit)
    
    if args.source in ['db', 'all']:
        view_db_messages(limit=args.limit, group_filter=args.group)

if __name__ == "__main__":
    main()
