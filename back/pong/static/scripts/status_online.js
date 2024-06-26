function runsocket() {

    let url = `wss://${window.location.host}/ws/status/`
    const chatSocket = new WebSocket(url);

    chatSocket.onopen = function (event) {
        console.log('Player connected.');
    };

    let data = NULL;
    chatSocket.onmessage = function(event){

        console.log('Received message:', event.data); // Debugging

        data = JSON.parse(event.data)
        if (data.type == 'status_update') {
            var statusIndicator = document.getElementById('status-indicator-' + data.user_id);
            console.log('user id ds le js:', data.user_id);
            console.log('statusIndicator:', statusIndicator); // Debugging
            console.log('status:', data.status); // Debugging
            if (data.status == 'online') {
                statusIndicator.classList.add('border', 'border-2', 'border-success');
            }
            else {
                statusIndicator.classList.remove('border', 'border-2', 'border-success');
            }
        }
    };

    chatSocket.onclose = function(event) {
        console.log('WebSocket disconnected.');
    };

    //ici tu peux lancer une boucle qui demande des updates toutes les 10 secondes.
}

document.addEventListener('DOMContentLoaded', (event) => {
    runsocket();
});

