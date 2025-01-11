import subprocess
import modules.twitch as twitch

ffmpeg_process = None

def start(duration):
    global ffmpeg_process

    ffmpeg_command = f'''ffmpeg -loop 1 -re -i images/stream.png \
    -vf "scale=1280:720,format=yuv420p,fps=30" \
    -t {duration} \
    -c:v libx264 -preset veryfast -b:v 3000k -pix_fmt yuv420p \
    -f flv rtmp://live.twitch.tv/app/{twitch.get_stream_key()}'''

    ffmpeg_process = subprocess.Popen(
        ffmpeg_command,
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print('Stream started.')
    return True

def stop():
    global ffmpeg_process
    if ffmpeg_process and ffmpeg_process.poll() is None:
        ffmpeg_process.terminate()  # Terminate the process
        print('Stream stopped.')
        ffmpeg_process = None
        return True
    
    print('No stream running.')
    return False