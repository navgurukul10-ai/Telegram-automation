#!/usr/bin/env python3
"""
Telegram Automation Dashboard
Shows date-wise group joins and message statistics
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

def get_total_stats():
    """Get total statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total groups
    cursor.execute("SELECT COUNT(*) FROM groups")
    total_groups = cursor.fetchone()[0]
    
    # Total messages
    cursor.execute("SELECT COUNT(*) FROM messages")
    total_messages = cursor.fetchone()[0]
    
    # Total unique groups with messages
    cursor.execute("SELECT COUNT(DISTINCT group_link) FROM messages")
    groups_with_messages = cursor.fetchone()[0]
    
    conn.close()
    return {
        'total_groups': total_groups,
        'total_messages': total_messages,
        'groups_with_messages': groups_with_messages
    }

def print_dashboard():
    """Print the main dashboard"""
    print("=" * 80)
    print("📊 TELEGRAM AUTOMATION DASHBOARD")
    print("=" * 80)
    
    # Get total stats
    stats = get_total_stats()
    print(f"\n📈 OVERALL STATISTICS:")
    print(f"   🏷️  Total Groups Joined: {stats['total_groups']}")
    print(f"   💬 Total Messages Fetched: {stats['total_messages']}")
    print(f"   📱 Groups with Messages: {stats['groups_with_messages']}")
    
    # Get available dates
    dates = get_available_dates()
    
    if not dates:
        print("\n❌ No data found in database")
        return
    
    print(f"\n📅 AVAILABLE DATES ({len(dates)} dates):")
    print("-" * 50)
    
    for i, date in enumerate(dates, 1):
        # Get groups for this date
        groups = get_groups_for_date(date)
        
        # Get message stats for this date
        message_stats = get_message_stats_for_date(date)
        total_messages = sum(count for _, count in message_stats)
        
        print(f"{i:2d}. {date} - {len(groups)} groups joined, {total_messages} messages")
    
    print("\n" + "=" * 80)
    print("📋 DETAILED DATE VIEW")
    print("=" * 80)
    
    # Show detailed view for each date
    for date in dates:
        print(f"\n🗓️  DATE: {date}")
        print("-" * 60)
        
        # Get groups joined on this date
        groups = get_groups_for_date(date)
        
        if groups:
            print(f"🏷️  GROUPS JOINED ({len(groups)}):")
            for group_link, joined_at, account_phone in groups:
                group_name = group_link.replace("https://t.me/", "")
                print(f"   • {group_name}")
                print(f"     📱 Account: {account_phone}")
                print(f"     ⏰ Joined: {joined_at}")
        else:
            print("   No groups joined on this date")
        
        # Get message statistics for this date
        message_stats = get_message_stats_for_date(date)
        
        if message_stats:
            print(f"\n💬 MESSAGES FETCHED ({sum(count for _, count in message_stats)} total):")
            for group_link, count in message_stats:
                group_name = group_link.replace("https://t.me/", "")
                print(f"   • {group_name}: {count} messages")
        else:
            print("\n💬 No messages fetched on this date")
        
        print("-" * 60)

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

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        date = sys.argv[1]
        show_date_details(date)
    else:
        print_dashboard()

if __name__ == "__main__":
    main()
