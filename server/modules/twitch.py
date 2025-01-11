from dotenv import find_dotenv, set_key
import os
import requests

# Load tokens and keys from .env
TWITCH_STREAM_KEY = os.getenv('TWITCH_STREAM_KEY')
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
TWITCH_AUTH_CODE = os.getenv('TWITCH_AUTH_CODE')
TWITCH_ACCESS_TOKEN = os.getenv('TWITCH_ACCESS_TOKEN')
TWITCH_REFRESH_TOKEN = os.getenv('TWITCH_REFRESH_TOKEN')
TWITCH_USER_ID = os.getenv('TWITCH_USER_ID')
TWITCH_LS_ID = os.getenv('TWITCH_LS_ID')

def get_stream_key():
    return TWITCH_STREAM_KEY

# Function to get a new access token when it's not available
def get_new_access_token():
    REDIRECT_URI = 'https://localhost'

    token_url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': TWITCH_CLIENT_ID,
        'client_secret': TWITCH_CLIENT_SECRET,
        'code': TWITCH_AUTH_CODE,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }

    response = requests.post(token_url, params=params)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        refresh_token = token_data['refresh_token']

        # Update .env with the new tokens
        env_path = find_dotenv()

        # Update the .env file with the new tokens
        set_key(env_path, 'TWITCH_ACCESS_TOKEN', access_token)
        if refresh_token:
            set_key(env_path, 'TWITCH_REFRESH_TOKEN', refresh_token)

# Function to refresh the Twitch access token
def refresh_access_token():
    token_url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': TWITCH_CLIENT_ID,
        'client_secret': TWITCH_CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': TWITCH_REFRESH_TOKEN
    }

    response = requests.post(token_url, params=params)
    if response.status_code == 200:
        new_token_data = response.json()
        new_access_token = new_token_data['access_token']
        new_refresh_token = new_token_data.get('refresh_token')

        # Update .env with the new tokens
        env_path = find_dotenv()

        # Update the .env file with the new tokens
        set_key(env_path, 'TWITCH_ACCESS_TOKEN', new_access_token)
        if new_refresh_token:
            set_key(env_path, 'TWITCH_REFRESH_TOKEN', new_refresh_token)

        return new_access_token
    else:
        print(f'Failed to refresh token: {response.status_code} - {response.text}')
        exit()

# Function to validate the current access token
def validate_access_token(access_token):
    validation_url = 'https://id.twitch.tv/oauth2/validate'
    headers = {
        'Authorization': f'OAuth {access_token}'
    }

    response = requests.get(validation_url, headers=headers)
    
    # Debugging information
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")

    return response.status_code == 200

# Validate access token, refresh if necessary
if not TWITCH_ACCESS_TOKEN:
    print('Access token not found, getting a new one...')
    TWITCH_ACCESS_TOKEN = get_new_access_token()
elif not validate_access_token(TWITCH_ACCESS_TOKEN):
    print('Access token is invalid or expired, refreshing...')
    TWITCH_ACCESS_TOKEN = refresh_access_token()

# API request URL to update stream info
base_url = 'https://api.twitch.tv/helix/'

# Headers for the request
headers = {
    'Authorization': f'Bearer {TWITCH_ACCESS_TOKEN}',
    'Client-Id': TWITCH_CLIENT_ID
}

def get_game_id(name):
    global TWITCH_ACCESS_TOKEN
    if not validate_access_token(TWITCH_ACCESS_TOKEN):
        print('Access token is invalid or expired, refreshing...')
        TWITCH_ACCESS_TOKEN = refresh_access_token()

    response = requests.get(f'{base_url}games', headers=headers, params={
        'name': name
    })

    if response.status_code == 200:
        data = response.json()
        if data['data']:
            return data['data'][0]['id']

    print(f'Failed to get game ID for {name}: {response.status_code} - {response.text}')
    return '509663' # Special Events

def is_channel_live():
    response = requests.get(f'{base_url}streams', headers=headers, params={
        'user_id': TWITCH_USER_ID
    })

    if response.status_code == 200:
        data = response.json()
        if data['data']:
            return True

    return False

def is_ls_live():
    response = requests.get(f'{base_url}streams', headers=headers, params={
        'user_id': TWITCH_LS_ID
    })

    if response.status_code == 200:
        data = response.json()
        if data['data']:
            return True

    return False

def update_channel(title, game_id):
    response = requests.patch(f'{base_url}channels', headers=headers, json={
        'broadcaster_id': TWITCH_USER_ID,
        'title':  title,
        'game_id': game_id
    })

    if response.status_code == 204:
        print('Channel info updated successfully!')
        return True

    print(f'Failed to update channel info: {response.status_code} - {response.text}')
    return False