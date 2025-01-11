const post = async (url, data) => {
    data = data ?? {};
    const password = document.getElementById('password').value;
    data.password = password;
    await fetch('/api/' + url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            alert('Gelukt!');
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Error: ' + error);
        });
}

const getPassword = () => {
    const password = document.getElementById('password').value;
    if (!password) {
        alert('Vul een wachtwoord in');
        return false;
    }

    return true;
}

// File upload functionality
const fileInput = document.getElementById('fileInput');
fileInput.addEventListener('change', async () => {
    if (!getPassword()) {
        return;
    }

    const file = fileInput.files[0];
    if (!file) {
        alert('Selecteer een bestand');
        return;
    }

    const reader = new FileReader();
    reader.onload = async (e) => {
        const fileContent = e.target.result;
        let data;

        // Check if it's a valid json
        try {
            data = JSON.parse(fileContent);
        } catch (error) {
            alert('Het bestand is geen geldige JSON! Ben je een komma vergeten?');
            return;
        }

        if (!data) {
            alert('Het bestand is leeg.');
            return;
        }

        await post('schedule', { schedule: data });
    };
    reader.readAsText(file);
});


// Toggle button functionality
const automatedLiveButton = document.getElementById('toggleButton');
const automatedLiveIcon = automatedLiveButton.querySelector('i');
const automatedLiveText = automatedLiveButton.querySelector('p');
let isGoingLive = false;

automatedLiveButton.addEventListener('click', async () => {
    if (!getPassword()) {
        return;
    }

    const input = prompt('Typ LIVE als Lekker Spelen binnen 12 uur LIVE gaat. Dit wordt na 12 uur automatisch uitgezet.');
    if (input != 'LIVE') {
        alert('Verkeerde input');
        return;
    }

    isGoingLive = !isGoingLive;
    automatedLiveIcon.className = isGoingLive ? 'fas fa-check' : 'fas fa-times';

    await post('ls-going-live', { is_going_live: isGoingLive });
});

const playMainButton = document.getElementById('playMainButton');
playMainButton.addEventListener('click', async () => {
    if (!getPassword()) {
        return;
    }

    const input = prompt('Typ MAIN als je een MAIN stream wilt starten.');
    if (input != 'MAIN') {
        alert('Verkeerde input');
        return;
    }

    await post('start-stream', { type: 'main', manual: true });
});

const playBonusButton = document.getElementById('playBonusButton');
playBonusButton.addEventListener('click', async () => {
    if (!getPassword()) {
        return;
    }

    const input = prompt('Typ BONUS als je een BONUS stream wilt starten.');
    if (input != 'BONUS') {
        alert('Verkeerde input');
        return;
    }

    await post('start-stream', { type: 'bonus', manual: true });
});

const stopButton = document.getElementById('stopButton');
stopButton.addEventListener('click', async () => {
    if (!getPassword()) {
        return;
    }

    const input = prompt('Typ STOP als je een stream wilt STOPPEN.');
    if (input != 'STOP') {
        alert('Verkeerde input');
        return;
    }

    await post('stop-stream');
});

document.addEventListener("DOMContentLoaded", async function () {
    uploadArea.addEventListener('dragover', (event) => {
        event.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (event) => {
        event.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = event.dataTransfer.files;
        if (files.length) {
            fileInput.files = files;
            // Trigger change event if needed
            const event = new Event('change', { bubbles: true });
            fileInput.dispatchEvent(event);
        }
    });
});