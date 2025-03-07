import redis

class RedisClient:
    def __init__(self, host="localhost", port=6379, db=0, password=None):
        self.client = redis.Redis(
            host=host,
            port=int(port),
            db=int(db),
            password=password,
            decode_responses=True
        )
    
    def set(self, key, value):
        return self.client.set(key, value)
    
    def get(self, key):
        return self.client.get(key)