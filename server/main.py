from dotenv import load_dotenv
load_dotenv()

import os
import json

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict

from handlers.event import events
import handlers.stream as stream_handler
import modules.data as data
import modules.twitch as twitch

class DefaultPayload(BaseModel):
    password: str

class StartStreamPayload(DefaultPayload):
    type: str
    manual: bool

class LSGoingLivePayload(DefaultPayload):
    is_going_live: bool

class SchedulePayload(DefaultPayload):
    schedule: List[Dict]


app = FastAPI()

ALLOWED_IPS = ['127.0.0.1', '::1']
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv('FRONTEND_URL')],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

def validate(request: Request, payload: DefaultPayload):
    client_host = request.client.host
    if client_host not in ALLOWED_IPS:
        if payload.password != ADMIN_PASSWORD:
            raise HTTPException(status_code=403, detail='Access Denied')

@app.get('/connect')
async def connect():
    return StreamingResponse(events(), media_type='text/event-stream')

@app.post('/start-stream')
async def start_stream(request: Request, payload: StartStreamPayload):
    validate(request, payload)

    reason = await stream_handler.can_stream_start() 
    if reason:
        raise HTTPException(status_code=400, detail=reason)
    
    if payload.type == 'main':
        response = await stream_handler.start_stream_main(payload.manual)
    elif payload.type == 'bonus':
        response = await stream_handler.start_stream_bonus(payload.manual)
    else:
        raise HTTPException(status_code=400, detail='Invalid stream type')

    return response

@app.post('/stop-stream')
async def stop_stream(request: Request, payload: DefaultPayload):
    validate(request, payload)

    running = await stream_handler.is_stream_running() 
    if not running:
        raise HTTPException(status_code=400, detail='Stream is not running')
    
    return await stream_handler.stop_stream()

@app.get('/ls-live')
async def is_ls_live():
    return {'is_ls_live': twitch.is_ls_live()}

@app.get('/ls-going-live')
async def is_ls_going_live():
    return {'is_going_live': await stream_handler.is_ls_going_live()}

@app.post('/ls-going-live')
async def set_ls_going_live(request: Request, payload: LSGoingLivePayload):
    validate(request, payload)

    is_going_live = payload.is_going_live

    if is_going_live is None:
        raise HTTPException(status_code=400, detail='Invalid request')
    
    return await stream_handler.set_ls_going_live(is_going_live)

@app.get('/schedule')
async def get_schedule():
    return data.get_schedule()

@app.post('/schedule')
async def set_schedule(request: Request, payload: SchedulePayload):
    validate(request, payload)

    schedule = payload.schedule
    
    if not schedule:
        raise HTTPException(status_code=400, detail='Invalid schedule')
    
    if not all([item.get('content_id') and item.get('planned_date') for item in schedule]):
        raise HTTPException(status_code=400, detail='Invalid schedule')

    with open('data/schedule_main.json', 'w') as file:
        json.dump(schedule, file, indent=4)

    return {'success': True}