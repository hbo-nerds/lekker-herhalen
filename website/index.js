let start_time;
let vod_id;
let vod_duration;

let syncing = false;
let chatState = 0;
let player;

const syncButtons = document.getElementsByClassName('btn-sync');
const chatButtons = document.getElementsByClassName('btn-chat');
const speurenButtons = document.getElementsByClassName('btn-speuren');
const redditButtons = document.getElementsByClassName('btn-reddit');
const vodContainer = document.querySelector('#twitch-vod');
const chatContainer = document.querySelector('#twitch-chat');
const chatFrame = document.querySelector('#twitch-chat iframe');

const getElapsedTime = () => {
    const now = new Date();
    const elapsed = now - start_time;
    return Math.floor(elapsed / 1000);
};

const checkSync = () => {
    if (syncing) return;
    const playerTime = player.getCurrentTime();
    const elapsedTime = getElapsedTime();
    const timeDifference = Math.abs(playerTime - elapsedTime);

    if (timeDifference > 3) {
        for (const syncButton of syncButtons) {
            syncButton.classList.add('desynced');
        }
    } else {
        for (const syncButton of syncButtons) {
            syncButton.classList.remove('desynced');
        }
    }
};

const syncVideo = () => {
    if (!player) return;
    syncing = true;
    const elapsedTime = getElapsedTime();
    const delay = 1000 - (elapsedTime % 1000);

    setTimeout(() => {
        player.seek(getElapsedTime());

        for (const syncButton of syncButtons) {
            syncButton.classList.remove('desynced');
        }

        setTimeout(() => {
            syncing = false;
        }, 1000);
    }, delay);
};

const toggleChat = () => {
    chatState = (chatState + 1) % 3;
    if (chatState == 0) {
        vodContainer.classList.remove('hide');
        chatContainer.classList.remove('hide');
        vodContainer.classList.remove('fullscreen');
        chatContainer.classList.remove('fullscreen');
    } else if (chatState == 1) {
        vodContainer.classList.add('hide');
        vodContainer.classList.remove('fullscreen');
        chatContainer.classList.add('fullscreen');
        chatContainer.classList.remove('hide');
        chat.style.removeProperty('height');
    } else {
        vodContainer.classList.remove('hide');
        vodContainer.classList.add('fullscreen');
        chatContainer.classList.remove('fullscreen');
        chatContainer.classList.add('hide');
    }
};

const setupPlayer = () => {
    const elapsed = getElapsedTime();
    if (elapsed < vod_duration) {
        player = new Twitch.Player("twitch-vod", {
            width: 1920,
            height: 1080,
            video: vod_id,
        });

        player.addEventListener(Twitch.Player.READY, () => {
            syncVideo();
            setInterval(checkSync, 1000);
        });
    }
};

const setupChat = () => {
    chatFrame.setAttribute('src', `https://www.twitch.tv/embed/lekkerherhalen/chat?darkpopout&parent=${window.location.hostname}`);
};

const setupFullscreenToggle = () => {
    const buttons = document.getElementsByClassName('btn-fullscreen');
    for (const btn of buttons) {
        btn.addEventListener('click', () => {
            const app = document.getElementById('app');
            app.classList.toggle('fullscreen');
        });
    }
};

const setupLightingToggle = () => {
    const lightingButtons = document.getElementsByClassName('btn-lighting');
    for (const lightingButton of lightingButtons) {
        lightingButton.addEventListener('click', () => {
            document.body.classList.toggle('light-mode');

            if (document.body.classList.contains('light-mode')) {
                lightingButton.innerHTML = '<i class="fas fa-sun"></i> Licht';
                chatFrame.src = chatFrame.src.replace('dark', 'light');
            } else {
                lightingButton.innerHTML = '<i class="fas fa-moon"></i> Donker';
                chatFrame.src = chatFrame.src.replace('light', 'dark');
            }
        });
    }
};

const setupModals = () => {
    const modals = ["info", "calender"];
    for (const modal of modals) {
        const modalElement = document.getElementById(`modal-${modal}`);
        const buttonsElement = document.getElementsByClassName(`btn-${modal}`);
        const closeElement = document.querySelector(`#modal-${modal} .btn-close-modal`);

        for (const buttonElement of buttonsElement) {
            buttonElement.addEventListener('click', () => {
                modalElement.style.display = "flex";
                modalElement.style['z-index'] = 10000;
            });

            window.addEventListener('click', (event) => {
                if (event.target == modalElement) {
                    modalElement.style.display = "none";
                    modalElement.style['z-index'] = 0;
                }
            });

            closeElement.addEventListener('click', () => {
                modalElement.style.display = "none";
                modalElement.style['z-index'] = 0;
            });
        }
    }
};

const setupSyncButton = () => {
    for (const syncButton of syncButtons) {
        syncButton.addEventListener('click', syncVideo);
    }
}

const setupChatButton = () => {
    for (const chatButton of chatButtons) {
        chatButton.addEventListener('click', toggleChat);
    }
}

const setupMiniMenu = () => {
    document.getElementById('hamburger').addEventListener('click', function () {
        var menu = document.getElementById('menu');
        if (menu.classList.contains('show')) {
            menu.classList.remove('show');
        } else {
            menu.classList.add('show');
        }
    });
}

const eventStreamStart = (data) => {
    if (vod_id != null) {
        return;
    }

    vod_id = data.vod_id;
    vod_duration = Number(data.duration);
    start_time = new Date(Number(data.start_time * 1000));

    for (const speurenButton of speurenButtons) {
        speurenButton.parentElement.setAttribute('href', `https://lekkerspeuren.nl/item/${data.id}`);
    }

    if (data.reddit_id) {
        for (const redditButton of redditButtons) {
            redditButton.parentElement.setAttribute('href', `https://www.reddit.com/r/lekkerspelen/comments/${data.reddit_id}`);
        }
    }

    setupPlayer();
}

const eventStreamStop = (data) => {
    vod_id = null;
    player.destroy();
}

let scheduleCache = null;

const setupSchedule = async () => {
    const buttons = document.getElementsByClassName('btn-calender')
    for (const button of buttons) {
        button.addEventListener('click', async () => {
            if (!scheduleCache) {
                const schedule = await fetchSchedule();
                updateModalContent(schedule);
            }
        });
    }
}

async function fetchSchedule() {
    if (scheduleCache) {
        return scheduleCache;
    }

    const response = await fetch('/api/schedule');
    const data = await response.json();
    scheduleCache = data;
    return data;
}

function updateModalContent(schedule) {
    const modalContent = document.querySelector('#calender');
    modalContent.innerHTML = `
    <div class="schedule-container">
        <div class="schedule-header">
            <div>Maandag</div>
            <div>Woensdag</div>
        </div>
        <div class="schedule-body" id="schedule-body">
        </div>
    </div>
    `;

    const scheduleBody = document.getElementById('schedule-body');
    let first = true;
    let scheduleWeek;

    schedule.forEach(item => {
        const title = item.chronological ? item.title : 'Een willekeurige VOD';
        const plannedDate = item.planned_date;

        const formattedDate = new Date(plannedDate).toLocaleDateString('nl-NL', {
            day: 'numeric',
            month: 'long'
        });

        const day = new Date(plannedDate).getDay();
        let content;

        if (day == 1 || first) {
            scheduleWeek = document.createElement('div');
            scheduleWeek.classList.add('schedule-week');
            scheduleBody.appendChild(scheduleWeek);

            if (day != 1) {
                first = false;
                content = `<div class="schedule-item">
                </div>`;
                scheduleWeek.innerHTML += content;
            }
        }

        first = false;

        content = `
            <div class="schedule-item ${item.chronological ? '' : 'random-vod'}">
                ${item.chronological ? `<a href="https://lekkerspeuren.nl/item/${item.id}">${title}</a>` : title}
                <span>${formattedDate}</span>
            </div>
        `;

        scheduleWeek.innerHTML += content;
    });
}

document.addEventListener("DOMContentLoaded", async function () {
    const eventSource = new EventSource("/api/connect");

    eventSource.onmessage = (event) => {
        const payload = JSON.parse(event.data);
        const { event: eventType, data } = payload;
        switch (eventType) {
            case "stream-start":
                eventStreamStart(data)
                break;
            case "stream-stop":
                eventStreamStop(data)
                break;
        }
    };

    setupChat();
    setupFullscreenToggle();
    setupLightingToggle();
    setupModals();
    setupSyncButton();
    setupChatButton();
    setupMiniMenu();
    setupSchedule();
});
