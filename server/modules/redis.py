import redis.asyncio as redis_async

_REDIS_KEY = 'HERHALEN:'

REDIS_KEYS = {
    'stream': f'{_REDIS_KEY}stream_data',
    'ls_going_live': f'{_REDIS_KEY}ls_going_live'
}

redis = redis_async.Redis(host='localhost', port=6379, decode_responses=True)