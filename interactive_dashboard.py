#!/usr/bin/env python3
"""
Interactive Telegram Automation Dashboard
Interactive date selection and detailed views
"""

import sqlite3
import json
from datetime import datetime, timedelta
import os

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect("data/app.db")

def get_available_dates():
    """Get all available dates from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get dates from groups table
    cursor.execute("""
        SELECT DISTINCT substr(joined_at, 1, 10) as date 
        FROM groups 
        WHERE joined_at IS NOT NULL 
        ORDER BY date DESC
    """)
    
    dates = [row[0] for row in cursor.fetchall()]
    conn.close()
    return dates

def get_groups_for_date(date):
    """Get groups joined on specific date"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT link, joined_at, account_phone
        FROM groups 
        WHERE substr(joined_at, 1, 10) = ?
        ORDER BY joined_at DESC
    """, (date,))
    
    groups = cursor.fetchall()
    conn.close()
    return groups

def get_message_stats_for_date(date):
    """Get message statistics for specific date"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get message count per group for the date
    cursor.execute("""
        SELECT group_link, COUNT(*) as message_count
        FROM messages 
        WHERE substr(date, 1, 10) = ?
        GROUP BY group_link
        ORDER BY message_count DESC
    """, (date,))
    
    message_stats = cursor.fetchall()
    conn.close()
    return message_stats

def get_messages_for_group_date(group_link, date, limit=10):
    """Get actual messages for a specific group and date"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, sender_id, date, text
        FROM messages 
        WHERE group_link = ? AND substr(date, 1, 10) = ?
        ORDER BY date DESC
        LIMIT ?
    """, (group_link, date, limit))
    
    messages = cursor.fetchall()
    conn.close()
    return messages

def show_date_menu():
    """Show interactive date selection menu"""
    dates = get_available_dates()
    
    if not dates:
        print("❌ No data found in database")
        return
    
    print("=" * 80)
    print("📊 TELEGRAM AUTOMATION DASHBOARD")
    print("=" * 80)
    
    print(f"\n📅 SELECT DATE ({len(dates)} dates available):")
    print("-" * 50)
    
    for i, date in enumerate(dates, 1):
        # Get groups for this date
        groups = get_groups_for_date(date)
        
        # Get message stats for this date
        message_stats = get_message_stats_for_date(date)
        total_messages = sum(count for _, count in message_stats)
        
        print(f"{i:2d}. {date} - {len(groups)} groups joined, {total_messages} messages")
    
    print(f"\n{len(dates)+1:2d}. Show All Dates Summary")
    print(f"{len(dates)+2:2d}. Exit")
    
    return dates

def show_date_details(date):
    """Show detailed information for a specific date"""
    print(f"\n🗓️  DETAILED VIEW FOR: {date}")
    print("=" * 60)
    
    # Get groups for this date
    groups = get_groups_for_date(date)
    
    if not groups:
        print("❌ No groups joined on this date")
        return
    
    print(f"\n🏷️  GROUPS JOINED ({len(groups)}):")
    print("-" * 40)
    
    for i, (group_link, joined_at, account_phone) in enumerate(groups, 1):
        group_name = group_link.replace("https://t.me/", "")
        print(f"\n{i}. {group_name}")
        print(f"   🔗 Link: {group_link}")
        print(f"   📱 Account: {account_phone}")
        print(f"   ⏰ Joined: {joined_at}")
        
        # Get message count for this group on this date
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM messages 
            WHERE group_link = ? AND substr(date, 1, 10) = ?
        """, (group_link, date))
        message_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"   💬 Messages: {message_count}")
    
    # Get message statistics
    message_stats = get_message_stats_for_date(date)
    
    if message_stats:
        print(f"\n💬 MESSAGE SUMMARY:")
        print("-" * 40)
        total_messages = sum(count for _, count in message_stats)
        print(f"📊 Total Messages: {total_messages}")
        print(f"📱 Groups with Messages: {len(message_stats)}")
        
        print(f"\n📋 MESSAGES BY GROUP:")
        for group_link, count in message_stats:
            group_name = group_link.replace("https://t.me/", "")
            print(f"   • {group_name}: {count} messages")
    
    # Ask if user wants to see actual messages
    print(f"\n🔍 Would you like to see actual messages? (y/n): ", end="")
    choice = input().lower().strip()
    
    if choice == 'y':
        show_group_messages_menu(date, groups)

def show_group_messages_menu(date, groups):
    """Show menu to select group and view messages"""
    print(f"\n📱 SELECT GROUP TO VIEW MESSAGES:")
    print("-" * 40)
    
    for i, (group_link, _, _) in enumerate(groups, 1):
        group_name = group_link.replace("https://t.me/", "")
        print(f"{i}. {group_name}")
    
    print(f"{len(groups)+1}. Back to date selection")
    
    try:
        choice = int(input(f"\nEnter choice (1-{len(groups)+1}): "))
        
        if choice == len(groups)+1:
            return
        
        if 1 <= choice <= len(groups):
            selected_group = groups[choice-1][0]
            show_group_messages(date, selected_group)
        else:
            print("❌ Invalid choice")
    except ValueError:
        print("❌ Please enter a valid number")

def show_group_messages(date, group_link):
    """Show messages for a specific group and date"""
    group_name = group_link.replace("https://t.me/", "")
    
    print(f"\n💬 MESSAGES FROM: {group_name}")
    print(f"📅 Date: {date}")
    print("=" * 60)
    
    messages = get_messages_for_group_date(group_link, date, 20)
    
    if not messages:
        print("❌ No messages found for this group on this date")
        return
    
    print(f"📊 Found {len(messages)} messages:")
    print("-" * 40)
    
    for i, (msg_id, sender_id, msg_date, text) in enumerate(messages, 1):
        print(f"\n📨 Message #{i}")
        print(f"   🆔 ID: {msg_id}")
        print(f"   👤 Sender: {sender_id}")
        print(f"   📅 Time: {msg_date}")
        print(f"   💬 Text: {text[:100]}{'...' if len(text) > 100 else ''}")
        print("-" * 30)

def show_all_dates_summary():
    """Show summary of all dates"""
    dates = get_available_dates()
    
    print("\n📊 ALL DATES SUMMARY")
    print("=" * 60)
    
    total_groups = 0
    total_messages = 0
    
    for date in dates:
        groups = get_groups_for_date(date)
        message_stats = get_message_stats_for_date(date)
        messages_count = sum(count for _, count in message_stats)
        
        total_groups += len(groups)
        total_messages += messages_count
        
        print(f"{date}: {len(groups)} groups, {messages_count} messages")
    
    print("-" * 60)
    print(f"📈 TOTAL: {total_groups} groups joined, {total_messages} messages fetched")

def main():
    """Main interactive function"""
    while True:
        try:
            dates = show_date_menu()
            
            if not dates:
                break
            
            choice = int(input(f"\nEnter your choice (1-{len(dates)+2}): "))
            
            if choice == len(dates)+2:  # Exit
                print("👋 Goodbye!")
                break
            elif choice == len(dates)+1:  # Show all dates summary
                show_all_dates_summary()
            elif 1 <= choice <= len(dates):  # Show specific date
                selected_date = dates[choice-1]
                show_date_details(selected_date)
            else:
                print("❌ Invalid choice. Please try again.")
            
            print("\n" + "="*80)
            input("Press Enter to continue...")
            
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
