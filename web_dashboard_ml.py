#!/usr/bin/env python3
"""
Enhanced Web Dashboard with ML Job Filtering
Beautiful UI for viewing filtered jobs and ML results
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

def get_ml_stats():
    """Get ML pipeline statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total filtered jobs
    cursor.execute("SELECT COUNT(*) FROM filtered_jobs")
    total_jobs = cursor.fetchone()[0]
    
    # Good jobs
    cursor.execute("SELECT COUNT(*) FROM filtered_jobs WHERE is_good_job = 1")
    good_jobs = cursor.fetchone()[0]
    
    # Fresher-friendly jobs
    cursor.execute("SELECT COUNT(*) FROM filtered_jobs WHERE is_fresher_friendly = 1")
    fresher_jobs = cursor.fetchone()[0]
    
    # Remote-friendly jobs
    cursor.execute("SELECT COUNT(*) FROM filtered_jobs WHERE is_remote_friendly = 1")
    remote_jobs = cursor.fetchone()[0]
    
    # Top skills
    cursor.execute("""
        SELECT extracted_skills, COUNT(*) as count 
        FROM filtered_jobs 
        WHERE extracted_skills IS NOT NULL AND extracted_skills != ''
        GROUP BY extracted_skills 
        ORDER BY count DESC 
        LIMIT 10
    """)
    top_skills = cursor.fetchall()
    
    conn.close()
    
    return {
        'total_jobs': total_jobs,
        'good_jobs': good_jobs,
        'fresher_jobs': fresher_jobs,
        'remote_jobs': remote_jobs,
        'top_skills': top_skills
    }

def get_filtered_jobs(filters=None, limit=50, offset=0):
    """Get filtered jobs with optional filters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Base query
    query = """
        SELECT fj.*, m.date as message_date
        FROM filtered_jobs fj
        JOIN messages m ON fj.original_message_id = m.id AND fj.group_link = m.group_link
    """
    
    conditions = []
    params = []
    
    if filters:
        if filters.get('good_jobs_only'):
            conditions.append("fj.is_good_job = 1")
        
        if filters.get('fresher_friendly_only'):
            conditions.append("fj.is_fresher_friendly = 1")
        
        if filters.get('remote_friendly_only'):
            conditions.append("fj.is_remote_friendly = 1")
        
        if filters.get('min_score'):
            conditions.append("fj.job_score >= ?")
            params.append(filters['min_score'])
        
        if filters.get('skills'):
            conditions.append("fj.extracted_skills LIKE ?")
            params.append(f"%{filters['skills']}%")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY fj.job_score DESC, fj.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    jobs = cursor.fetchall()
    
    # Get column names
    column_names = [description[0] for description in cursor.description]
    
    # Convert to list of dictionaries
    job_list = []
    for job in jobs:
        job_dict = dict(zip(column_names, job))
        job_list.append(job_dict)
    
    conn.close()
    return job_list

def get_job_details(job_id):
    """Get detailed information for a specific job"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT fj.*, m.date as message_date, m.sender_id
        FROM filtered_jobs fj
        JOIN messages m ON fj.original_message_id = m.id AND fj.group_link = m.group_link
        WHERE fj.id = ?
    """, (job_id,))
    
    job = cursor.fetchone()
    if not job:
        conn.close()
        return None
    
    # Get column names
    column_names = [description[0] for description in cursor.description]
    job_dict = dict(zip(column_names, job))
    
    conn.close()
    return job_dict

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard_ml.html')

@app.route('/api/ml-stats')
def api_ml_stats():
    """API endpoint to get ML statistics"""
    stats = get_ml_stats()
    return jsonify(stats)

@app.route('/api/filtered-jobs')
def api_filtered_jobs():
    """API endpoint to get filtered jobs"""
    # Get query parameters
    filters = {}
    if request.args.get('good_jobs_only') == 'true':
        filters['good_jobs_only'] = True
    if request.args.get('fresher_friendly_only') == 'true':
        filters['fresher_friendly_only'] = True
    if request.args.get('remote_friendly_only') == 'true':
        filters['remote_friendly_only'] = True
    if request.args.get('min_score'):
        filters['min_score'] = int(request.args.get('min_score'))
    if request.args.get('skills'):
        filters['skills'] = request.args.get('skills')
    
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    
    jobs = get_filtered_jobs(filters, limit, offset)
    return jsonify(jobs)

@app.route('/api/job/<int:job_id>')
def api_job_details(job_id):
    """API endpoint to get job details"""
    job = get_job_details(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job)

@app.route('/api/skills')
def api_skills():
    """API endpoint to get available skills"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT extracted_skills 
        FROM filtered_jobs 
        WHERE extracted_skills IS NOT NULL AND extracted_skills != ''
        ORDER BY extracted_skills
    """)
    
    skills = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(skills)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 Starting Enhanced ML Dashboard...")
    print("📱 Open your browser and go to: http://localhost:3001")
    print("🔄 Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=3001)
