import asyncio
import json
import handlers.stream as stream_handler
from modules.redis import redis, REDIS_KEYS

event_queue = asyncio.Queue()

async def events():
    # New connection. Is there a stream going on?
    if await stream_handler.is_stream_running():
        payload = { 'event': 'stream-start' }
        yield await event_stream_start(payload)
    elif await stream_handler.is_ls_going_live():
        payload = { 'event': 'ls-status', 'data': { 'ls_live': True } }
        yield f'data: {json.dumps(payload)}\n\n'

    while True:
        event = await event_queue.get()
        payload = { 'event': event, 'data': {} }
    
        if event == 'stream-start':
            yield await event_stream_start(payload)
            continue

        if event == 'stream-stop':
            payload = { 'event': 'stream-stop', 'data': { 'ls_live': await stream_handler.is_ls_going_live()  } }

        yield f'data: {json.dumps(payload)}\n\n'
        continue

async def event_stream_start(payload):
    data = await redis.hgetall(REDIS_KEYS['stream'])
    payload['data'] = data
    return f'data: {json.dumps(payload)}\n\n'
