import redis
import redis_settings
import logging
import json

import os
from dotenv import load_dotenv

class TADatabase:
    def __init__(self, logger: logging.Logger):
        self.redis_cli = redis.Redis(
            host = redis_settings.HOST,
            port = redis_settings.PORT,
            db = redis_settings.DB_ID
        )
        self.logger = logger
        load_dotenv('.env')
        self.TA_EXPIRE_TIME = int(os.environ.get('REDIS_TA_EXPIRE_TIME'))
    
    def set(self, key, value):
        self.redis_cli.set(key, value)
        self.logger.info(f'[TADatabase.set] key: {key}, value: {value}')
        
    def get(self, key):
        value = self.redis_cli.get(key)
        self.logger.info(f'[TADatabase.get] key: {key}, value: {value}')
        return value
    
    def GetLatestTAID(self, server_id: str):
        key_prefix = self.MakePrefix(server_id)
        if not self.redis_cli.exists(key_prefix):
            self.redis_cli.hset(key_prefix, "latest_taid", 0)
        return int(self.redis_cli.hget(key_prefix, "latest_taid"))
    
    def MakePrefixWithTAID(self, server_id: str, ta_id: int):
        return f'{self.MakePrefix(server_id)},taid:{ta_id}'
    
    def MakePrefix(self, server_id: str):
        return f'sv:{server_id}'
    
    def IsExistsMarchingData(self, server_id: str, ta_id: int, user_id: int):
        return True if self.GetMarchingData(server_id, ta_id, user_id) else False
    
    def GetMarchingData(self, server_id: str, ta_id: int, user_id: int):
        key_prefix = self.MakePrefixWithTAID(server_id, ta_id)
        return self.redis_cli.hget(key_prefix, user_id)
    
    def IsExistTA(self, ta_id: int, server_id: str):
        return self.redis_cli.exists(self.MakePrefixWithTAID(server_id, ta_id))
    
    def CreateTA(self, server_id: str, user_id: int, time: int):
        key_prefix = self.MakePrefix(server_id)
        new_taid = self.GetLatestTAID(server_id) + 1
        self.redis_cli.hset(key_prefix, "latest_taid", new_taid)
        self.redis_cli.expire(key_prefix, self.TA_EXPIRE_TIME)
        self.logger.info(f'[TADatabase.CreateTA] New TAID: {new_taid} (expire: {self.TA_EXPIRE_TIME})')
        self.JoinTA(new_taid, server_id, user_id, time)
        return new_taid
        
    def JoinTA(self, ta_id: int, server_id: str, user_id: int, time: int):
        key_prefix = self.MakePrefixWithTAID(server_id, ta_id)
        self.redis_cli.hset(key_prefix, user_id, time)
        self.redis_cli.expire(key_prefix, self.TA_EXPIRE_TIME)
        self.logger.info(f'[TADatabase.JoinTA] AddMarchingData key: {key_prefix}, user_id: {user_id}, time: {time} (expire: {self.TA_EXPIRE_TIME})')
        
    def LeaveTA(self, ta_id: int, server_id: str, user_id: int):
        key_prefix = self.MakePrefixWithTAID(server_id, ta_id)
        if self.IsExistsMarchingData(server_id, ta_id, user_id):
            self.redis_cli.hdel(key_prefix, user_id)
            self.logger.info(f'[TADatabase.LeaveTA] RemoveMarchingData key: {key_prefix}, user_id: {user_id}')
            return True
        else:
            self.logger.info(f'[TADatabase.LeaveTA] Not found user_id: {user_id} in TAID: {ta_id}')
            return False
        
    def GetTAJoiners(self, ta_id: int, server_id: str):
        key_prefix = self.MakePrefixWithTAID(server_id, ta_id)
        _ta_joiners = self.redis_cli.hgetall(key_prefix)
        ta_joiners = {}
        for user_id, time in _ta_joiners.items():
            user_id = int(user_id)
            ta_joiners[user_id] = int(time)
        self.logger.info(f'[TADatabase.GetTAJoiners] TAID: {ta_id}, joiners: {ta_joiners}')
        return ta_joiners

    def CloseTA(self, ta_id: int, server_id: str):
        key_prefix = self.MakePrefixWithTAID(server_id, ta_id)
        ta_joiners = self.GetTAJoiners(ta_id, server_id)
        self.redis_cli.delete(key_prefix)
        self.logger.info(f'[TADatabase.CloseTA] TAID: {ta_id}, server_id: {server_id} joiners: {ta_joiners}')
        return ta_joiners

