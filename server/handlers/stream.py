import json
import datetime
import os
import random
import asyncio

from modules.redis import redis, REDIS_KEYS
from utils.utils import create_post_text
import modules.data as data_utils
import modules.discord as discord
import modules.streamer as streamer
import modules.twitch as twitch
import modules.reddit as reddit

event_queue = None

async def start_stream(schedule_file, stream_type, manual):
    print("Starting stream of type", stream_type)
    global event_queue
    with open(schedule_file, 'r') as file:
        schedule = json.load(file)

    with open('data/index.json', 'r') as file:
        index_data = json.load(file)

    index = index_data[stream_type]
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    stream_data = None

    if stream_type == 'main':
        if schedule[index]['planned_date'] == current_date:
            stream_data = data_utils.find_by_id(schedule[index]['content_id'])
        else:
            for i, stream in enumerate(schedule):
                if stream['planned_date'] == current_date:
                    stream_data = data_utils.find_by_id(stream['content_id'])
                    index = i
                    break
    elif stream_type == 'bonus':
        stream_data = data_utils.find_by_id(schedule[index])

    if not stream_data:
        print(f'No scheduled stream found for {current_date}.')
        return {'message': 'No scheduled stream found for today.'}

    duration = stream_data['platforms']['twitch']['duration']
    id = stream_data['id']
    twitch_id = stream_data['platforms']['twitch']['id']

    if not event_queue:
        from handlers.event import event_queue

    await redis.hset(REDIS_KEYS['stream'], mapping={
        'id': id,
        'vod_id': twitch_id,
        'duration': duration,
        'start_time': int(datetime.datetime.now().timestamp()),
    })

    await redis.expire(REDIS_KEYS['stream'], duration)

    index = (index + 1) % len(schedule)
    index_data[stream_type] = index
    with open('data/index.json', 'w') as file:
        json.dump(index_data, file)

    text = create_post_text(stream_data, twitch_id)
    twitch.refresh_access_token(True)
    game_id = twitch.get_game_id(stream_data['activities'][0]['title'])
    twitch.update_channel(stream_data['titles'][0], game_id)
    discord.post_to_discord(text)
    streamer.start(duration)

    if stream_type == 'main' and not manual:
        title = stream_data['titles'][0]
        post = await reddit.post_to_reddit(title, text)
        await redis.hset(REDIS_KEYS['stream'], 'reddit_id', post.id)

    # Start the stream
    await event_queue.put('stream-start')

    asyncio.ensure_future(handle_ls_live())

    return {'message': 'Stream started!'}

async def start_stream_main(manual=False):
    return await start_stream('data/schedule_main.json', 'main', manual)

async def start_stream_bonus(manual=False):
    if not manual:
        day_count = int(os.getenv('BONUS_DAY_COUNT'))
        week_chance = float(os.getenv('BONUS_WEEK_CHANCE'))
        chance = week_chance / day_count

        if random.random() > chance:
            return {'message': 'No stream today'}

    return await start_stream('data/schedule_bonus.json', 'bonus', manual)

async def stop_stream():
    global event_queue
    await redis.delete(REDIS_KEYS['stream'])
    streamer.stop()
    if not event_queue:
        from handlers.event import event_queue

    await event_queue.put('stream-stop')

    return {'message': 'Stream stopped!'}


async def is_stream_running():
    stream_data = await redis.keys(REDIS_KEYS['stream'])
    return len(stream_data) > 0

# Check if Lekker Spelen is live every 5 minutes
async def handle_ls_live():
    while True:
        await asyncio.sleep(300)
        if twitch.is_ls_live():
            await stop_stream()
            break


async def set_ls_going_live(live):
    if live:
        await redis.set(REDIS_KEYS['ls_going_live'], '1', ex=int(60 * 60 * 12))
        return
    
    await redis.delete(REDIS_KEYS['ls_going_live'])

async def is_ls_going_live():
    return await redis.get(REDIS_KEYS['ls_going_live'])

async def can_stream_start():
    stream_data = await redis.keys(REDIS_KEYS['stream'])
    if stream_data:
        return 'A stream is already running'
    
    ls_live = twitch.is_ls_live()
    if ls_live:
        return 'Lekker Spelen is live at the moment'
    
    ls_value = await is_ls_going_live()
    if ls_value:
        return 'Lekker Spelen is about to go live'

    return None