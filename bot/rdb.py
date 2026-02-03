import json
import redis

class RedisDB:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=db)
        
    def add_ticket_messageid(self, ticket_id, chat_id, message_id):
        json_data = json.dumps({"chat_id": chat_id, "message_id": message_id})
        self.redis.sadd(f"ticket:{ticket_id}:messages", json_data)
        self.redis.expire(f"ticket:{ticket_id}:messages", 172800)
        
    def get_ticket_messageids(self, ticket_id):
        pairs = self.redis.smembers(f"ticket:{ticket_id}:messages")
        result = []
        for pair in pairs:
            result.append(json.loads(pair))
        return result