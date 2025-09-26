#!/usr/bin/env python3
"""
Job Viewer - Command Line Interface for ML Filtered Jobs
"""

import sqlite3
import sys

class JobViewer:
    def __init__(self):
        self.db_path = "data/app.db"
    
    def get_db_connection(self):
        return sqlite3.connect(self.db_path)
    
    def show_stats(self):
        """Show ML pipeline statistics"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM filtered_jobs')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM filtered_jobs WHERE is_good_job = 1')
        good = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM filtered_jobs WHERE is_fresher_friendly = 1')
        fresher = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM filtered_jobs WHERE is_remote_friendly = 1')
        remote = cursor.fetchone()[0]
        
        conn.close()
        
        print("🤖 ML PIPELINE STATISTICS")
        print("=" * 40)
        print(f"📊 Total Jobs Processed: {total:,}")
        print(f"🎯 Good Jobs Found: {good:,} ({good/total*100:.1f}%)")
        print(f"👶 Fresher-Friendly Jobs: {fresher:,} ({fresher/total*100:.1f}%)")
        print(f"🏠 Remote-Friendly Jobs: {remote:,} ({remote/total*100:.1f}%)")
        print()
    
    def show_top_jobs(self, limit=10, fresher_only=False, remote_only=False):
        """Show top jobs with filters"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT job_score, extracted_skills, extracted_salary, extracted_location,
                   is_fresher_friendly, is_remote_friendly, message_text, group_link
            FROM filtered_jobs 
            WHERE is_good_job = 1
        """
        
        if fresher_only:
            query += " AND is_fresher_friendly = 1"
        if remote_only:
            query += " AND is_remote_friendly = 1"
        
        query += " ORDER BY job_score DESC LIMIT ?"
        
        cursor.execute(query, [limit])
        jobs = cursor.fetchall()
        conn.close()
        
        print(f"🏆 TOP {len(jobs)} JOBS")
        print("=" * 60)
        
        for i, job in enumerate(jobs, 1):
            score, skills, salary, location, fresher, remote, text, group_link = job
            group_name = group_link.replace("https://t.me/", "")
            
            print(f"{i:2d}. Score: {score:2.0f} | Group: {group_name}")
            print(f"    Skills: {skills or 'None'}")
            print(f"    Salary: {salary or 'Not specified'}")
            print(f"    Location: {location or 'Not specified'}")
            print(f"    Fresher: {'✅' if fresher else '❌'} | Remote: {'✅' if remote else '❌'}")
            print(f"    Text: {text[:120]}...")
            print()
    
    def search_jobs(self, skill=None, location=None):
        """Search jobs by skill or location"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT job_score, extracted_skills, extracted_salary, extracted_location,
                   is_fresher_friendly, is_remote_friendly, message_text, group_link
            FROM filtered_jobs 
            WHERE is_good_job = 1
        """
        params = []
        
        if skill:
            query += " AND extracted_skills LIKE ?"
            params.append(f"%{skill.lower()}%")
        
        if location:
            query += " AND extracted_location LIKE ?"
            params.append(f"%{location.lower()}%")
        
        query += " ORDER BY job_score DESC LIMIT 20"
        
        cursor.execute(query, params)
        jobs = cursor.fetchall()
        conn.close()
        
        print(f"🔍 SEARCH RESULTS ({len(jobs)} jobs found)")
        print("=" * 60)
        
        for i, job in enumerate(jobs, 1):
            score, skills, salary, location, fresher, remote, text, group_link = job
            group_name = group_link.replace("https://t.me/", "")
            
            print(f"{i:2d}. Score: {score:2.0f} | Group: {group_name}")
            print(f"    Skills: {skills or 'None'}")
            print(f"    Salary: {salary or 'Not specified'}")
            print(f"    Location: {location or 'Not specified'}")
            print(f"    Fresher: {'✅' if fresher else '❌'} | Remote: {'✅' if remote else '❌'}")
            print(f"    Text: {text[:100]}...")
            print()

def main():
    viewer = JobViewer()
    
    if len(sys.argv) < 2:
        print("🤖 JOB VIEWER - ML Pipeline Results")
        print("=" * 50)
        print("Usage:")
        print("  python3 job_viewer.py stats                    - Show statistics")
        print("  python3 job_viewer.py top [limit]              - Show top jobs")
        print("  python3 job_viewer.py fresher [limit]          - Show fresher jobs")
        print("  python3 job_viewer.py remote [limit]           - Show remote jobs")
        print("  python3 job_viewer.py search <skill> [location] - Search jobs")
        print()
        print("Examples:")
        print("  python3 job_viewer.py stats")
        print("  python3 job_viewer.py top 20")
        print("  python3 job_viewer.py fresher 10")
        print("  python3 job_viewer.py search python")
        print("  python3 job_viewer.py search javascript remote")
        return
    
    command = sys.argv[1].lower()
    
    if command == "stats":
        viewer.show_stats()
    
    elif command == "top":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        viewer.show_top_jobs(limit=limit)
    
    elif command == "fresher":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 15
        viewer.show_top_jobs(limit=limit, fresher_only=True)
    
    elif command == "remote":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 15
        viewer.show_top_jobs(limit=limit, remote_only=True)
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("❌ Please specify a skill to search for")
            return
        
        skill = sys.argv[2]
        location = sys.argv[3] if len(sys.argv) > 3 else None
        viewer.search_jobs(skill=skill, location=location)
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
