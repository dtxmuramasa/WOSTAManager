import redis
import redis_settings
import logging

class TADatabase:
    def __init__(self, logger: logging.Logger):
        self.redis_cli = redis.Redis(
            host = redis_settings.HOST,
            port = redis_settings.PORT,
            db = redis_settings.DB_ID
        )
        self.logger = logger
    
    def set(self, key, value):
        self.redis_cli.set(key, value)
        self.logger.info(f'[TADatabase.set] key: {key}, value: {value}')
        
    def get(self, key):
        value = self.redis_cli.get(key)
        self.logger.info(f'[TADatabase.get] key: {key}, value: {value}')
        return value
