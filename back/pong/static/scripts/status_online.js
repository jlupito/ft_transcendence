function runsocketStatus() {

    let url = `wss://${window.location.host}/ws/status/`
    const statusSock = new WebSocket(url);

    statusSock.onopen = function (event) {
        console.log('Online WS connected.');
    };

    statusSock.onmessage = function(event) {

        let data = JSON.parse(event.data)
        if (data.type == 'status_update') {
            var statusIndicator = document.getElementById('status-indicator-' + data.user_id);
            if (data.status == 'online') {
                statusIndicator.style.backgroundColor = 'rgb(46, 206, 86)'; // Vert
            }
            else if (data.status == 'offline') {
                statusIndicator.style.backgroundColor = 'rgb(255, 0, 0)'; // Rouge
            }
            else if (data.status == 'is_playing') {
                statusIndicator.style.backgroundColor = 'rgb(255, 165, 0)'; // Orange
            }
        }
    };

    statusSock.onclose = function(event) {
        console.log('Online WS disconnected.');
    };
}

document.addEventListener('DOMContentLoaded', (event) => {
    runsocketStatus();
});
