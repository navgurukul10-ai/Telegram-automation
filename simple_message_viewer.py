#!/usr/bin/env python3
"""
Simple Message Viewer - View messages with group information
"""

import csv
import json
import os
import sqlite3

def print_banner():
    print("=" * 60)
    print("📱 TELEGRAM MESSAGE VIEWER")
    print("=" * 60)

def show_stats():
    """Show statistics about messages"""
    print("\n📊 MESSAGE STATISTICS")
    print("=" * 40)
    
    # CSV stats
    if os.path.exists("data/messages.csv"):
        try:
            with open("data/messages.csv", 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                csv_messages = list(reader)
            
            if csv_messages:
                groups = set(msg.get('group', '') for msg in csv_messages)
                print(f"📁 CSV Messages: {len(csv_messages)} total")
                print(f"🏷️  CSV Groups: {len(groups)} unique groups")
                
                # Show group list
                print("\n📋 Groups found:")
                for group in sorted(groups):
                    count = sum(1 for msg in csv_messages if msg.get('group') == group)
                    print(f"   • {group}: {count} messages")
            else:
                print("📁 CSV Messages: 0")
        except Exception as e:
            print(f"📁 CSV Messages: Error - {e}")
    else:
        print("📁 CSV Messages: File not found")
    
    # Database stats
    if os.path.exists("data/app.db"):
        try:
            conn = sqlite3.connect("data/app.db")
            cursor = conn.cursor()
            
            # Check if messages table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
            if cursor.fetchone():
                # Count messages
                cursor.execute("SELECT COUNT(*) FROM messages")
                db_message_count = cursor.fetchone()[0]
                
                # Count unique groups
                cursor.execute("SELECT COUNT(DISTINCT group_link) FROM messages")
                db_group_count = cursor.fetchone()[0]
                
                print(f"\n📁 Database Messages: {db_message_count} total")
                print(f"��️  Database Groups: {db_group_count} unique groups")
            else:
                print("\n📁 Database Messages: No messages table found")
            
            conn.close()
        except Exception as e:
            print(f"\n📁 Database Messages: Error - {e}")
    else:
        print("\n�� Database Messages: File not found")

def view_csv_messages(limit=10, group_filter=None):
    """View messages from CSV"""
    if not os.path.exists("data/messages.csv"):
        print("❌ CSV file not found: data/messages.csv")
        return
    
    print(f"\n📊 Viewing messages from CSV")
    print(f"📋 Limit: {limit} messages")
    if group_filter:
        print(f"🔍 Filter: Group contains '{group_filter}'")
    print("-" * 60)
    
    try:
        with open("data/messages.csv", 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            messages = []
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
            print(f"   💬 Text: {text[:150]}{'...' if len(text) > 150 else ''}")
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")

def view_db_messages(limit=10, group_filter=None):
    """View messages from database"""
    if not os.path.exists("data/app.db"):
        print("❌ Database file not found: data/app.db")
        return
    
    print(f"\n📊 Viewing messages from database")
    print(f"📋 Limit: {limit} messages")
    if group_filter:
        print(f"🔍 Filter: Group contains '{group_filter}'")
    print("-" * 60)
    
    try:
        conn = sqlite3.connect("data/app.db")
        cursor = conn.cursor()
        
        # Check if messages table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
        if not cursor.fetchone():
            print("❌ Messages table not found in database")
            conn.close()
            return
        
        # Query messages
        query = "SELECT group_link, id, sender_id, date, text FROM messages"
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
            print(f"   �� Text: {text[:150]}{'...' if len(text) > 150 else ''}")
            print("-" * 40)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")

def main():
    import sys
    
    print_banner()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "stats":
            show_stats()
        elif command == "csv":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            group_filter = sys.argv[3] if len(sys.argv) > 3 else None
            view_csv_messages(limit, group_filter)
        elif command == "db":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            group_filter = sys.argv[3] if len(sys.argv) > 3 else None
            view_db_messages(limit, group_filter)
        else:
            print("Usage: python3 simple_message_viewer.py [stats|csv|db] [limit] [group_filter]")
    else:
        print("Usage: python3 simple_message_viewer.py [stats|csv|db] [limit] [group_filter]")
        print("\nExamples:")
        print("  python3 simple_message_viewer.py stats")
        print("  python3 simple_message_viewer.py csv 20")
        print("  python3 simple_message_viewer.py db 10 job")

if __name__ == "__main__":
    main()
