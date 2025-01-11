import random
import json

# Import data.json
with open('../data/data.json', encoding='utf8') as f:
    json_data = json.load(f)

# Filter the list to only include streams
streams = [item for item in json_data['content'] if item['type'] == 'stream' and ('twitch_id' in item or 'youtube_id' in item) ]

# Solo streams are streams that have the tag 'casual' and 'solo'
solo_streams = [s for s in streams if "tags" in s and 'casual' in s['tags'] and 'solo' in s['tags']]
random.shuffle(solo_streams)
schedule = [stream['id'] for stream in solo_streams]

with open('../data/schedule_solo.json', 'w', encoding='utf8') as f:
    json.dump(schedule, f, ensure_ascii=False, indent=4)

print("schedule_solo.json has been created.")
