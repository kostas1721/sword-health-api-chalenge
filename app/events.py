import redis
import json

publisher = redis.Redis(host='redis', port=6379, decode_responses=True)

def publish_event(event: dict):
    publisher.publish("recommendations", json.dumps(event))
