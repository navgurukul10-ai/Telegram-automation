#!/usr/bin/env python3
"""
Web-based Telegram Automation Dashboard
Beautiful UI for viewing database data
"""

from flask import Flask, render_template, jsonify, request
import sqlite3
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect("data/app.db")

def get_available_dates():
    """Get all available dates from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
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

def get_messages_for_group(group_link, limit=50):
    """Get messages for a specific group"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, sender_id, date, text
        FROM messages 
        WHERE group_link = ?
        ORDER BY date DESC
        LIMIT ?
    """, (group_link, limit))
    
    messages = cursor.fetchall()
    conn.close()
    return messages

def get_total_stats():
    """Get total statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM groups")
    total_groups = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM messages")
    total_messages = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT group_link) FROM messages")
    groups_with_messages = cursor.fetchone()[0]
    
    conn.close()
    return {
        'total_groups': total_groups,
        'total_messages': total_messages,
        'groups_with_messages': groups_with_messages
    }

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/dates')
def api_dates():
    """API endpoint to get available dates"""
    dates = get_available_dates()
    return jsonify(dates)

@app.route('/api/stats')
def api_stats():
    """API endpoint to get total statistics"""
    stats = get_total_stats()
    return jsonify(stats)

@app.route('/api/date/<date>')
def api_date_data(date):
    """API endpoint to get data for specific date"""
    groups = get_groups_for_date(date)
    message_stats = get_message_stats_for_date(date)
    
    # Format groups data
    groups_data = []
    for group_link, joined_at, account_phone in groups:
        group_name = group_link.replace("https://t.me/", "")
        groups_data.append({
            'name': group_name,
            'link': group_link,
            'joined_at': joined_at,
            'account': account_phone
        })
    
    # Format message stats
    messages_data = []
    for group_link, count in message_stats:
        group_name = group_link.replace("https://t.me/", "")
        messages_data.append({
            'group': group_name,
            'link': group_link,
            'count': count
        })
    
    return jsonify({
        'groups': groups_data,
        'messages': messages_data,
        'total_groups': len(groups_data),
        'total_messages': sum(count for _, count in message_stats)
    })

@app.route('/api/messages/<path:group_link>')
def api_group_messages(group_link):
    """API endpoint to get messages for specific group"""
    messages = get_messages_for_group(group_link, 100)
    
    messages_data = []
    for msg_id, sender_id, msg_date, text in messages:
        messages_data.append({
            'id': msg_id,
            'sender_id': sender_id,
            'date': msg_date,
            'text': text
        })
    
    return jsonify(messages_data)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 Starting Web Dashboard...")
    print("📱 Open your browser and go to: http://localhost:3000")
    print("🔄 Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=3000)
