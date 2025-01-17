import requests
import os

discord_webhook_url = f'https://discord.com/api/webhooks/{os.getenv("DISCORD_WEBHOOK_ID")}'

def post_to_discord(text):
    data = {
            'content': text + "\n<@&1317946865471324190>",
            'username': 'Lekker Herhalen',
            'avatar_url': os.getenv('DISCORD_AVATAR_URL')
        }

    response = requests.post(discord_webhook_url, json=data)
    
    if response.status_code == 204:
        print('Posted to Discord successfully!')
    else:
        print(f'Failed to post to Discord. Status code: {response.status_code}, Response: {response.text}')
        