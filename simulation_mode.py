import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
from config import SIMULATION_MODE, SIMULATION_SPEED_MULTIPLIER

class SimulationMode:
    """Simulation mode for testing without real Telegram API calls"""
    
    def __init__(self):
        self.enabled = SIMULATION_MODE
        self.speed_multiplier = SIMULATION_SPEED_MULTIPLIER
        self.logger = logging.getLogger(__name__)
        self.api_call_count = 0
        self.start_time = time.time()
        
        # Mock data for simulation
        self.mock_messages = [
            "We are hiring a Python developer for our startup in Bangalore. Contact: 9876543210",
            "Looking for React developer with 2+ years experience. Remote work available.",
            "Job opening for fresher software engineer. No experience required. Apply now!",
            "Hiring frontend developer with HTML, CSS, JavaScript skills. Mumbai location.",
            "Career opportunity for DevOps engineer. AWS experience preferred.",
            "Internship position available for computer science students. 6 months duration.",
            "Full-time position for backend developer. Node.js and MongoDB required.",
            "Part-time work from home opportunity. Flexible hours. Contact for details.",
            "Just sharing some random thoughts about technology trends",
            "Check out this cool article about AI and machine learning",
            "Anyone know good restaurants in the area?",
            "Weather is really nice today, perfect for a walk",
            "Happy birthday to everyone in the group!",
            "This group is getting too noisy with all the spam",
            "We need to moderate this group better"
        ]
    
    async def simulate_delay(self, base_delay: float) -> None:
        """Simulate human-like delay with speed multiplier"""
        if not self.enabled:
            return
        
        # Apply speed multiplier (faster in simulation)
        actual_delay = base_delay / self.speed_multiplier
        await asyncio.sleep(actual_delay)
    
    async def simulate_group_join(self, group_link: str) -> Dict[str, Any]:
        """Simulate joining a group"""
        if not self.enabled:
            return {"success": True, "group_info": None}
        
        self.api_call_count += 1
        
        # Simulate delay
        await self.simulate_delay(random.uniform(2, 5))
        
        # Simulate success/failure
        success = random.random() > 0.1  # 90% success rate
        
        if success:
            group_info = {
                "link": group_link, 
                "name": "Mock Group", 
                "members": random.randint(100, 5000)
            }
            
            self.logger.info(f"[SIMULATION] Joined group: {group_link}")
            return {"success": True, "group_info": group_info}
        else:
            self.logger.warning(f"[SIMULATION] Failed to join group: {group_link}")
            return {"success": False, "error": "Simulated join failure"}
    
    async def simulate_message_scraping(self, group_link: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Simulate scraping messages from a group"""
        if not self.enabled:
            return []
        
        self.api_call_count += 1
        
        # Simulate delay
        await self.simulate_delay(random.uniform(1, 3))
        
        # Generate mock messages
        messages = []
        message_count = min(limit, random.randint(50, 100))
        
        for i in range(message_count):
            message_text = random.choice(self.mock_messages)
            messages.append({
                "id": i + 1,
                "date": (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat(),
                "sender_id": random.randint(100000000, 999999999),
                "text": message_text
            })
        
        self.logger.info(f"[SIMULATION] Scraped {len(messages)} messages from {group_link}")
        return messages
    
    async def simulate_authentication(self, phone: str) -> Dict[str, Any]:
        """Simulate authentication process"""
        if not self.enabled:
            return {"success": True, "session_valid": True}
        
        self.api_call_count += 1
        
        # Simulate delay
        await self.simulate_delay(random.uniform(1, 2))
        
        # Simulate auth success/failure
        success = random.random() > 0.05  # 95% success rate
        session_valid = random.random() > 0.1  # 90% session valid
        
        if success:
            self.logger.info(f"[SIMULATION] Authenticated: {phone}")
        else:
            self.logger.warning(f"[SIMULATION] Auth failed: {phone}")
        
        return {
            "success": success,
            "session_valid": session_valid,
            "error": "Simulated auth failure" if not success else None
        }
    
    def get_simulation_stats(self) -> Dict[str, Any]:
        """Get simulation statistics"""
        if not self.enabled:
            return {}
        
        elapsed_time = time.time() - self.start_time
        calls_per_minute = (self.api_call_count / elapsed_time) * 60 if elapsed_time > 0 else 0
        
        return {
            "enabled": self.enabled,
            "speed_multiplier": self.speed_multiplier,
            "api_calls_made": self.api_call_count,
            "elapsed_time_seconds": elapsed_time,
            "calls_per_minute": calls_per_minute,
            "estimated_real_time_hours": elapsed_time / self.speed_multiplier / 3600
        }
    
    def log_simulation_summary(self):
        """Log simulation summary"""
        if not self.enabled:
            return
        
        stats = self.get_simulation_stats()
        
        self.logger.info(f"Simulation completed: {stats['api_calls_made']} API calls in {stats['elapsed_time_seconds']:.1f}s")
        self.logger.info(f"Estimated real-time equivalent: {stats['estimated_real_time_hours']:.2f} hours")
        self.logger.info(f"Average rate: {stats['calls_per_minute']:.1f} calls/minute")

# Global simulation mode instance
simulation_mode = SimulationMode()

# Convenience functions
async def simulate_delay(base_delay: float) -> None:
    await simulation_mode.simulate_delay(base_delay)

async def simulate_group_join(group_link: str) -> Dict[str, Any]:
    return await simulation_mode.simulate_group_join(group_link)

async def simulate_message_scraping(group_link: str, limit: int = 100) -> List[Dict[str, Any]]:
    return await simulation_mode.simulate_message_scraping(group_link, limit)

async def simulate_authentication(phone: str) -> Dict[str, Any]:
    return await simulation_mode.simulate_authentication(phone)

def get_simulation_stats() -> Dict[str, Any]:
    return simulation_mode.get_simulation_stats()

def log_simulation_summary():
    simulation_mode.log_simulation_summary()
