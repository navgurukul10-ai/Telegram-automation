#!/usr/bin/env python3
"""
Test script for the advanced Telegram crawler
"""

import asyncio
import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import SIMULATION_MODE
from ml_pipeline import ml_pipeline
from simulation_mode import get_simulation_stats
from dashboard import get_stats, generate_report

def test_ml_pipeline():
    """Test the ML pipeline"""
    print("Testing ML Pipeline...")
    
    # Test job classification
    test_messages = [
        "We are hiring a Python developer for our startup. Contact: 9876543210",
        "Looking for React developer with 2+ years experience",
        "Just sharing some random thoughts about technology",
        "Happy birthday to everyone!"
    ]
    
    for msg in test_messages:
        result = ml_pipeline.classify_message({"text": msg})
        print(f"Message: {msg[:50]}...")
        print(f"Job Score: {result['job_score']:.2f}")
        print(f"Is Job Post: {result['is_job_post']}")
        print(f"Phone Numbers: {result['phone_numbers']}")
        print(f"Technologies: {result['technologies']}")
        print(f"Location: {result['location']}")
        print(f"Remote: {result['remote']}")
        print(f"Fresher Friendly: {result['fresher_friendly']}")
        print("-" * 50)

def test_simulation_mode():
    """Test simulation mode"""
    print("Testing Simulation Mode...")
    
    if SIMULATION_MODE:
        stats = get_simulation_stats()
        print(f"Simulation Stats: {stats}")
    else:
        print("Simulation mode is disabled")

def test_dashboard():
    """Test dashboard functionality"""
    print("Testing Dashboard...")
    
    try:
        stats = get_stats()
        print(f"Dashboard Stats: {stats}")
        
        # Generate report
        report_file = generate_report()
        print(f"Report generated: {report_file}")
        
    except Exception as e:
        print(f"Dashboard test failed: {e}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("Advanced Telegram Crawler - Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print(f"Simulation Mode: {SIMULATION_MODE}")
    print()
    
    try:
        test_ml_pipeline()
        print()
        test_simulation_mode()
        print()
        test_dashboard()
        print()
        
        print("=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
