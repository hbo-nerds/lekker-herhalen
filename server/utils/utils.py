import datetime

def convert_duration(seconds):
    minutes = seconds // 60
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f'{hours}:{remaining_minutes:02d}:00'

def create_post_text(stream_data, twitch_id):
    title = stream_data.get('title') or stream_data['titles'][0]
    youtube_id = stream_data['platforms'].get('youtube', {}).get('id')

    text = f'## {title}\n\n'
    text += f'Nu "LIVE" op **[Lekker Herhalen](https://lekkerherhalen.nl)**!\n\n'
    text += f'* **Game:** {stream_data["activities"][0]["title"]}\n* **Lengte:** {convert_duration(stream_data["platforms"].get("twitch").get("duration") or 0)}\n\
* **Datum:** {datetime.datetime.strptime(stream_data["date"], "%Y-%m-%d").strftime("%d/%m/%Y")}\n\n'
    text += f'[Twitch](<https://twitch.tv/videos/{twitch_id}>)'

    if youtube_id:
        text += f' | [YouTube](<https://youtube.com/watch?v={youtube_id}>)'

    text += f' | [Lekker Speuren](<https://lekkerspeuren.nl/item/{stream_data["id"]}>)'
    return text
