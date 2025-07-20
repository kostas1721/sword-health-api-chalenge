import redis
import json
import asyncio
from datetime import datetime

subscriber = redis.Redis(host='redis', port=6379, decode_responses=True)
pubsub = subscriber.pubsub()
pubsub.subscribe("recommendations")

async def process_event(event):
    print(f"[WORKER] Event received: {event}")
    with open("/data/recommendation_logs.txt", "a") as f:
        f.write(json.dumps(event) + "\n")

async def main():
    print("Worker listening for recommendation events...")
    for message in pubsub.listen():
        if message['type'] == 'message':
            event = json.loads(message['data'])
            await process_event(event)

asyncio.run(main())
