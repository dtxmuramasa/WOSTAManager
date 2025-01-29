import redis
import redis_settings
import logging
import json

class TADatabase:
    def __init__(self, logger: logging.Logger):
        self.redis_cli = redis.Redis(
            host = redis_settings.HOST,
            port = redis_settings.PORT,
            db = redis_settings.DB_ID
        )
        self.logger = logger
        self.redis_cli.rpush('generated_taids', 0)
    
    def set(self, key, value):
        self.redis_cli.set(key, value)
        self.logger.info(f'[TADatabase.set] key: {key}, value: {value}')
        
    def get(self, key):
        value = self.redis_cli.get(key)
        self.logger.info(f'[TADatabase.get] key: {key}, value: {value}')
        return value
    
    def MakePrefix(self, server_id: str, channel_id: str, user_id: int):
        return f'sv:{server_id},ch:{channel_id},uid:{user_id}'
    
    def GetUserIdFromKey(self, key: str):
        return key.split(',')[2].split(':')[1].strip()
    
    def IsExistTA(self, ta_id: int):
        return self.redis_cli.exists(f'ta:{ta_id}')
    
    def CreateTA(self, server_id: str, channel_id: str, user_id: int, time: int):
        new_taid = int(self.redis_cli.rpop('generated_taids')) + 1
        self.redis_cli.rpush('generated_taids', new_taid)
        self.logger.info(f'[TADatabase.CreateTA] New TAID: {new_taid}')
        self.JoinTA(new_taid, server_id, channel_id, user_id, time)
        return new_taid
        
    def JoinTA(self, ta_id: int, server_id: str, channel_id: str, user_id: int, time: int):
        key = self.MakePrefix(server_id, channel_id, user_id)
        self.redis_cli.hset(f'ta:{ta_id}', key, time)
        self.logger.info(f'[TADatabase.JoinTA] TAID: {ta_id}, key: {key}, time: {time}')
        
    def LeaveTA(self, ta_id: int, server_id: str, channel_id: str, user_id: int):
        key = self.MakePrefix(server_id, channel_id, user_id)
        self.redis_cli.hdel(f'ta:{ta_id}', key)
        self.logger.info(f'[TADatabase.LeaveTA] TAID: {ta_id}, key: {key}')

    def CloseTA(self, ta_id: int):
        _ta_joiners = self.redis_cli.hgetall(f'ta:{ta_id}')
        ta_joiners = {}
        for key, time in _ta_joiners.items():
            user_id = int(self.GetUserIdFromKey(key.decode('utf-8')))
            ta_joiners[user_id] = int(time)
        self.redis_cli.delete(f'ta:{ta_id}')
        self.logger.info(f'[TADatabase.CloseTA] TAID: {ta_id}, joiners: {ta_joiners}')
        return ta_joiners

