import redis
from typing import Any, Optional

class RedisClient:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None
    ):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True
        )
    
    def get(self, key: str) -> Any:
        return self.client.get(key)
        
    def set(self, key: str, value: Any) -> bool:
        return self.client.set(key, value)
        
    def delete(self, key: str) -> bool:
        return self.client.delete(key) > 0