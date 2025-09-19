import re
import numpy as np
from typing import Dict, List, Optional
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from config import JOB_KEYWORDS, TECH_KEYWORDS, MIN_CONFIDENCE_SCORE

class JobClassificationPipeline:
    """ML pipeline for classifying job posts"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.job_classifier = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize ML model with training data"""
        # Sample training data
        job_texts = [
            "We are hiring a Python developer for our startup",
            "Looking for React developer with 2+ years experience",
            "Job opening for fresher software engineer",
            "Remote work opportunity for full-stack developer",
            "Hiring frontend developer with HTML CSS JavaScript",
            "Career opportunity for DevOps engineer",
            "Internship position available for computer science students",
            "Full-time position for backend developer",
            "Part-time work from home opportunity",
            "Just sharing some random thoughts about technology",
            "Check out this cool article about AI",
            "Anyone know good restaurants in the area?",
            "Weather is really nice today",
            "Happy birthday to everyone!",
            "This group is getting too noisy"
        ]
        
        job_labels = [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
        
        # Train classifier
        self.job_classifier = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english')),
            ('classifier', LogisticRegression(random_state=42))
        ])
        
        self.job_classifier.fit(job_texts, job_labels)
        self.logger.info("Job classification model trained")
    
    def extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        phone_patterns = [
            r'\b\d{10}\b',  # 10 digits
            r'\b\+91\s?\d{10}\b',  # +91 prefix
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # formatted numbers
        ]
        
        phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)
        
        # Clean and normalize
        cleaned_phones = []
        for phone in phones:
            cleaned = re.sub(r'[^\d+]', '', phone)
            if len(cleaned) >= 10:
                cleaned_phones.append(cleaned)
        
        return list(set(cleaned_phones))
    
    def extract_technologies(self, text: str) -> List[str]:
        """Extract technology keywords from text"""
        text_lower = text.lower()
        found_tech = []
        
        for tech in TECH_KEYWORDS:
            if tech.lower() in text_lower:
                found_tech.append(tech)
        
        return found_tech
    
    def is_fresher_friendly(self, text: str) -> bool:
        """Check if job post is fresher friendly"""
        fresher_keywords = [
            'fresher', 'freshers', 'entry level', 'junior', 'intern', 'internship',
            'no experience', '0-1 years', '0-2 years', 'trainee', 'graduate'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in fresher_keywords)
    
    def is_remote_job(self, text: str) -> bool:
        """Check if job is remote"""
        remote_keywords = [
            'remote', 'work from home', 'wfh', 'distributed', 'virtual',
            'online', 'telecommute', 'anywhere'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in remote_keywords)
    
    def extract_location(self, text: str) -> Optional[str]:
        """Extract job location from text"""
        cities = [
            'mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'pune',
            'kolkata', 'ahmedabad', 'jaipur', 'surat', 'lucknow', 'kanpur',
            'nagpur', 'indore', 'thane', 'bhopal', 'visakhapatnam'
        ]
        
        text_lower = text.lower()
        for city in cities:
            if city in text_lower:
                return city.title()
        
        return None
    
    def calculate_job_score(self, text: str) -> float:
        """Calculate job relevance score for a message"""
        if not text or len(text.strip()) < 10:
            return 0.0
        
        try:
            # ML prediction
            prediction = self.job_classifier.predict_proba([text])[0]
            ml_score = prediction[1]  # Probability of being a job post
            
            # Keyword-based scoring
            keyword_score = 0.0
            text_lower = text.lower()
            
            # Job-related keywords
            for keyword in JOB_KEYWORDS:
                if keyword.lower() in text_lower:
                    keyword_score += 0.1
            
            # Technology keywords
            tech_count = len(self.extract_technologies(text))
            tech_score = min(tech_count * 0.05, 0.3)
            
            # Phone number presence
            phone_score = 0.1 if self.extract_phone_numbers(text) else 0.0
            
            # Length bonus
            length_score = min(len(text) / 1000, 0.2)
            
            # Combine scores
            total_score = (ml_score * 0.4 + keyword_score * 0.3 + 
                          tech_score * 0.2 + phone_score * 0.05 + length_score * 0.05)
            
            return min(total_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating job score: {e}")
            return 0.0
    
    def classify_message(self, message_data: Dict) -> Dict:
        """Classify a message and extract relevant information"""
        text = message_data.get('text', '')
        
        # Calculate job score
        job_score = self.calculate_job_score(text)
        
        # Extract information
        phones = self.extract_phone_numbers(text)
        technologies = self.extract_technologies(text)
        is_fresher = self.is_fresher_friendly(text)
        is_remote = self.is_remote_job(text)
        location = self.extract_location(text)
        
        return {
            'job_score': job_score,
            'is_job_post': job_score >= MIN_CONFIDENCE_SCORE,
            'phone_numbers': phones,
            'technologies': technologies,
            'fresher_friendly': is_fresher,
            'remote': is_remote,
            'location': location,
            'processed': True
        }
    
    def calculate_group_score(self, messages: List[Dict]) -> float:
        """Calculate job discovery score for a group"""
        if not messages:
            return 0.0
        
        # Take last 100 messages
        recent_messages = messages[-100:]
        
        # Calculate average job score
        job_scores = [self.calculate_job_score(msg.get('text', '')) for msg in recent_messages]
        avg_job_score = np.mean(job_scores) if job_scores else 0.0
        
        # Count high-quality job posts
        high_quality_posts = sum(1 for score in job_scores if score >= MIN_CONFIDENCE_SCORE)
        quality_ratio = high_quality_posts / len(recent_messages) if recent_messages else 0.0
        
        # Calculate final score
        group_score = (avg_job_score * 0.6 + quality_ratio * 0.4)
        
        return min(group_score, 1.0)

# Global ML pipeline instance
ml_pipeline = JobClassificationPipeline()
