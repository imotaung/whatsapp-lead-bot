import time
from collections import defaultdict
from app.config import logger, RATE_LIMIT_REQUESTS, RATE_LIMIT_PERIOD_SECONDS

class RateLimiter:
    def __init__(self):
        self.max_requests = RATE_LIMIT_REQUESTS
        self.period = RATE_LIMIT_PERIOD_SECONDS
        self.requests = defaultdict(list)
    
    def is_allowed(self, phone: str) -> bool:
        now = time.time()
        self.requests[phone] = [t for t in self.requests[phone] if now - t < self.period]
        if len(self.requests[phone]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for {phone}")
            return False
        self.requests[phone].append(now)
        return True

rate_limiter = RateLimiter()