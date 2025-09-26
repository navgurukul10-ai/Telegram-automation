#!/usr/bin/env python3
"""
ML Job Classifier for Telegram Messages
Classifies messages as good jobs and filters fresher-friendly, remote jobs
"""

import re
import json
import sqlite3
import asyncio
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import os

class JobClassifier:
    def __init__(self):
        self.job_keywords = [
            # Job-related terms
            'job', 'hiring', 'career', 'position', 'opening', 'vacancy', 'opportunity',
            'fresher', 'intern', 'internship', 'full-time', 'part-time', 'contract',
            'remote', 'work from home', 'wfh', 'hybrid', 'onsite', 'offsite',
            'developer', 'engineer', 'programmer', 'analyst', 'consultant',
            'recruitment', 'talent', 'candidate', 'apply', 'application'
        ]
        
        self.skill_keywords = [
            # Web technologies
            'html', 'css', 'javascript', 'js', 'react', 'angular', 'vue', 'node',
            'python', 'java', 'php', 'ruby', 'c++', 'c#', 'go', 'rust',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
            'git', 'github', 'gitlab', 'bitbucket',
            'frontend', 'backend', 'fullstack', 'full-stack',
            'ui', 'ux', 'design', 'figma', 'adobe',
            'machine learning', 'ml', 'ai', 'data science', 'analytics'
        ]
        
        self.fresher_keywords = [
            'fresher', 'entry level', 'junior', 'trainee', 'intern', 'internship',
            '0-1 years', '0-2 years', '1-2 years', 'new graduate', 'recent graduate',
            'no experience', 'beginner', 'learning', 'training provided'
        ]
        
        self.experience_patterns = [
            r'(\d+)\s*[-–]\s*(\d+)\s*years?',
            r'(\d+)\+\s*years?',
            r'minimum\s+(\d+)\s*years?',
            r'at\s+least\s+(\d+)\s*years?',
            r'(\d+)\s*to\s*(\d+)\s*years?'
        ]
        
        self.salary_patterns = [
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|lac|cr|k|thousand)',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|lac|cr|k|thousand)\s*₹',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lpa|lakh per annum)',
            r'salary[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'stipend[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d+)?)'
        ]
        
        self.contact_patterns = [
            r'@\w+',  # Telegram usernames
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\+?\d{10,15}',  # Phone numbers
            r'https?://[^\s]+',  # URLs
            r'www\.[^\s]+'  # www URLs
        ]

    def extract_features(self, text: str) -> Dict:
        """Extract features from message text"""
        text_lower = text.lower()
        
        features = {
            'has_job_keywords': sum(1 for keyword in self.job_keywords if keyword in text_lower),
            'has_skill_keywords': sum(1 for skill in self.skill_keywords if skill in text_lower),
            'has_fresher_keywords': any(keyword in text_lower for keyword in self.fresher_keywords),
            'has_contact_info': any(re.search(pattern, text, re.IGNORECASE) for pattern in self.contact_patterns),
            'has_salary_info': any(re.search(pattern, text, re.IGNORECASE) for pattern in self.salary_patterns),
            'text_length': len(text),
            'word_count': len(text.split()),
            'has_remote_keywords': any(keyword in text_lower for keyword in ['remote', 'work from home', 'wfh', 'hybrid']),
            'has_location_info': bool(re.search(r'\b(?:delhi|mumbai|bangalore|chennai|hyderabad|pune|kolkata|gurgaon|noida|india|usa|us|uk|canada|australia)\b', text_lower))
        }
        
        return features

    def extract_structured_data(self, text: str) -> Dict:
        """Extract structured data from message text"""
        extracted = {
            'skills': [],
            'salary': None,
            'location': None,
            'company': None,
            'contact': None,
            'experience': None
        }
        
        text_lower = text.lower()
        
        # Extract skills
        for skill in self.skill_keywords:
            if skill in text_lower:
                extracted['skills'].append(skill)
        
        # Extract salary
        for pattern in self.salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted['salary'] = match.group(0)
                break
        
        # Extract experience
        for pattern in self.experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted['experience'] = match.group(0)
                break
        
        # Extract contact info
        for pattern in self.contact_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted['contact'] = match.group(0)
                break
        
        # Extract location (simple approach)
        location_keywords = ['delhi', 'mumbai', 'bangalore', 'chennai', 'hyderabad', 'pune', 'kolkata', 'gurgaon', 'noida', 'india', 'usa', 'us', 'uk', 'canada', 'australia', 'remote', 'work from home', 'wfh']
        for location in location_keywords:
            if location in text_lower:
                extracted['location'] = location
                break
        
        return extracted

    def calculate_job_score(self, features: Dict, extracted_data: Dict) -> float:
        """Calculate job quality score (0-100)"""
        score = 0
        
        # Job keywords (20 points max)
        score += min(features['has_job_keywords'] * 2, 20)
        
        # Skill keywords (20 points max)
        score += min(features['has_skill_keywords'] * 3, 20)
        
        # Contact information (15 points)
        if features['has_contact_info']:
            score += 15
        
        # Salary information (15 points)
        if features['has_salary_info']:
            score += 15
        
        # Location information (10 points)
        if features['has_location_info']:
            score += 10
        
        # Text quality (10 points)
        if 50 <= features['word_count'] <= 500:  # Good length
            score += 10
        elif features['word_count'] > 500:  # Too long
            score += 5
        
        # Remote-friendly bonus (10 points)
        if features['has_remote_keywords']:
            score += 10
        
        return min(score, 100)

    def is_fresher_friendly(self, features: Dict, extracted_data: Dict) -> bool:
        """Determine if job is fresher-friendly"""
        # Check for fresher keywords
        if features['has_fresher_keywords']:
            return True
        
        # Check experience requirements
        if extracted_data['experience']:
            exp_text = extracted_data['experience'].lower()
            # Look for low experience requirements
            if any(term in exp_text for term in ['0-1', '0-2', '1-2', 'entry', 'junior', 'trainee']):
                return True
        
        # Check for specific skills that are fresher-friendly
        fresher_skills = ['html', 'css', 'javascript', 'python', 'react', 'node']
        if any(skill in extracted_data['skills'] for skill in fresher_skills):
            return True
        
        return False

    def is_remote_friendly(self, features: Dict, extracted_data: Dict) -> bool:
        """Determine if job is remote-friendly"""
        return features['has_remote_keywords']

    def classify_message(self, text: str) -> Dict:
        """Classify a message and return results"""
        features = self.extract_features(text)
        extracted_data = self.extract_structured_data(text)
        
        job_score = self.calculate_job_score(features, extracted_data)
        is_good_job = job_score >= 40  # Threshold for good jobs
        is_fresher_friendly = self.is_fresher_friendly(features, extracted_data)
        is_remote_friendly = self.is_remote_friendly(features, extracted_data)
        
        return {
            'job_score': job_score,
            'is_good_job': is_good_job,
            'is_fresher_friendly': is_fresher_friendly,
            'is_remote_friendly': is_remote_friendly,
            'extracted_skills': ', '.join(extracted_data['skills']),
            'extracted_salary': extracted_data['salary'],
            'extracted_location': extracted_data['location'],
            'extracted_company': extracted_data['company'],
            'extracted_contact': extracted_data['contact'],
            'extracted_experience': extracted_data['experience'],
            'confidence_score': job_score / 100.0
        }

class MLJobPipeline:
    def __init__(self):
        self.classifier = JobClassifier()
        self.db_path = "data/app.db"
    
    def get_db_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def process_all_messages(self):
        """Process all messages and classify them"""
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        # Get all messages that haven't been processed yet
        cur.execute("""
            SELECT m.id, m.group_link, m.text, m.date
            FROM messages m
            LEFT JOIN filtered_jobs fj ON m.id = fj.original_message_id AND m.group_link = fj.group_link
            WHERE fj.id IS NULL AND m.text IS NOT NULL AND m.text != ''
            ORDER BY m.date DESC
        """)
        
        messages = cur.fetchall()
        print(f"📊 Processing {len(messages)} messages for job classification...")
        
        processed_count = 0
        good_jobs_count = 0
        fresher_jobs_count = 0
        remote_jobs_count = 0
        
        for msg_id, group_link, text, date in messages:
            try:
                # Classify the message
                result = self.classifier.classify_message(text)
                
                # Insert into filtered_jobs table
                cur.execute("""
                    INSERT INTO filtered_jobs (
                        original_message_id, group_link, message_text, job_score,
                        is_good_job, is_fresher_friendly, is_remote_friendly,
                        extracted_skills, extracted_salary, extracted_location,
                        extracted_company, extracted_contact, extracted_experience,
                        confidence_score, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    msg_id, group_link, text, result['job_score'],
                    int(result['is_good_job']), int(result['is_fresher_friendly']),
                    int(result['is_remote_friendly']), result['extracted_skills'],
                    result['extracted_salary'], result['extracted_location'],
                    result['extracted_company'], result['extracted_contact'],
                    result['extracted_experience'], result['confidence_score'],
                    datetime.now().isoformat()
                ))
                
                processed_count += 1
                if result['is_good_job']:
                    good_jobs_count += 1
                if result['is_fresher_friendly']:
                    fresher_jobs_count += 1
                if result['is_remote_friendly']:
                    remote_jobs_count += 1
                
                if processed_count % 100 == 0:
                    print(f"   📥 Processed {processed_count} messages...")
                    
            except Exception as e:
                print(f"   ⚠️ Error processing message {msg_id}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ ML Pipeline Results:")
        print(f"   📊 Total processed: {processed_count}")
        print(f"   🎯 Good jobs found: {good_jobs_count}")
        print(f"   👶 Fresher-friendly jobs: {fresher_jobs_count}")
        print(f"   🏠 Remote-friendly jobs: {remote_jobs_count}")
        
        return {
            'processed': processed_count,
            'good_jobs': good_jobs_count,
            'fresher_jobs': fresher_jobs_count,
            'remote_jobs': remote_jobs_count
        }
    
    def export_to_csv(self):
        """Export filtered jobs to CSV"""
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        # Get all filtered jobs
        cur.execute("""
            SELECT fj.*, m.date as message_date
            FROM filtered_jobs fj
            JOIN messages m ON fj.original_message_id = m.id AND fj.group_link = m.group_link
            ORDER BY fj.job_score DESC, fj.created_at DESC
        """)
        
        jobs = cur.fetchall()
        conn.close()
        
        # Create CSV
        import csv
        os.makedirs("data", exist_ok=True)
        
        csv_path = "data/filtered_jobs.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'ID', 'Original Message ID', 'Group Link', 'Message Text', 'Job Score',
                'Is Good Job', 'Is Fresher Friendly', 'Is Remote Friendly',
                'Extracted Skills', 'Extracted Salary', 'Extracted Location',
                'Extracted Company', 'Extracted Contact', 'Extracted Experience',
                'Confidence Score', 'Created At', 'Message Date'
            ])
            
            # Data rows
            for job in jobs:
                writer.writerow(job)
        
        print(f"📁 Exported {len(jobs)} filtered jobs to {csv_path}")
        return csv_path

if __name__ == "__main__":
    pipeline = MLJobPipeline()
    
    print("🤖 Starting ML Job Classification Pipeline...")
    print("=" * 60)
    
    # Process all messages
    results = pipeline.process_all_messages()
    
    # Export to CSV
    csv_path = pipeline.export_to_csv()
    
    print("\n🎉 ML Pipeline completed successfully!")
    print(f"📊 Check results in: {csv_path}")
