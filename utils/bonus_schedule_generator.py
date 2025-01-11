import random
import json

# Import data.json
with open('../server/data/data.json', encoding='utf8') as f:
    json_data = json.load(f)

# Filter the list to only include streams
streams = [item for item in json_data['content'] if item['type'] == 'stream' and ('twitch_id' in item) ]

# Bonus streams are streams that have the tag 'casual' (but not 'solo')
bonus_streams = [s for s in streams if "tags" in s and 'casual' in s['tags'] and not 'solo' in s['tags']]
random.shuffle(bonus_streams)
schedule = [stream['id'] for stream in bonus_streams]

with open('../server/data/schedule_bonus.json', 'w', encoding='utf8') as f:
    json.dump(schedule, f, ensure_ascii=False, indent=4)

print("schedule_bonus.json has been created.")
