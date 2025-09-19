import asyncio
import random
import time
from datetime import datetime
import logging
from config import MIN_DELAY, MAX_DELAY, MESSAGE_DELAY, GROUP_JOIN_DELAY

class RateLimiter:
    """Human-like rate limiting to avoid getting banned"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.last_group_join = 0
        self.last_message_read = 0
        self.last_request = 0
    
    async def wait_for_group_join(self):
        """Wait before joining a group"""
        now = time.time()
        if self.last_group_join > 0:
            elapsed = now - self.last_group_join
            if elapsed < GROUP_JOIN_DELAY:
                wait_time = GROUP_JOIN_DELAY - elapsed
                self.logger.debug(f"Waiting {wait_time:.1f}s before next group join")
                await asyncio.sleep(wait_time)
        
        # Add random human-like variation
        random_delay = random.uniform(0.5, 2.0)
        await asyncio.sleep(random_delay)
        
        self.last_group_join = time.time()
    
    async def wait_for_message_read(self):
        """Wait before reading messages"""
        now = time.time()
        if self.last_message_read > 0:
            elapsed = now - self.last_message_read
            if elapsed < MESSAGE_DELAY:
                wait_time = MESSAGE_DELAY - elapsed
                await asyncio.sleep(wait_time)
        
        # Add random human-like variation
        random_delay = random.uniform(0.1, 0.5)
        await asyncio.sleep(random_delay)
        
        self.last_message_read = time.time()
    
    async def wait_for_general_request(self):
        """Wait before making any API request"""
        now = time.time()
        if self.last_request > 0:
            elapsed = now - self.last_request
            min_delay = random.uniform(MIN_DELAY, MAX_DELAY)
            if elapsed < min_delay:
                wait_time = min_delay - elapsed
                await asyncio.sleep(wait_time)
        
        self.last_request = time.time()

# Global rate limiter instance
rate_limiter = RateLimiter()
