function runsocketUsersListUpdate() {

    let url = `wss://${window.location.host}/ws/userslist_update/`
    const usersListUpdateSock = new WebSocket(url);

    usersListUpdateSock.onopen = function (event) {
        console.log('UsersListUpdate WS - Player connected.');
    };

    usersListUpdateSock.onmessage = function (event) {

        let data = JSON.parse(event.data)
        if (data.type == 'userslist_update') {
            let parentElement = document.getElementById(`usersList`);
            if (parentElement) {
                // modification de data.new_user.new_user_id en data.new_user_id suite modif AsbtractUser
                if (!document.getElementById(`userRemove-${data.new_user_id}`)) {

                    if (data.new_user.friend_status != 'accepted') {

                        let childElement = document.createElement('li');
                        childElement.innerHTML = `
                            <div id="userRemove-${data.new_user_id}" class="d-flex justify-content-between align-items-center col-10 bg-white bg-opacity-25 p-3 mb-2 rounded shadow-sm mx-auto">
                                <div class="d-flex align-items-center">
                                    <img class="rounded-circle me-2" src="${data.avatar}" alt="" style="width: 35px; height: 35px;">
                                    <div style="max-width: 7ch; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                                        ${data.username}
                                    </div>
                                </div>
                                <form action="send_invite" method="POST">
                                    ${formHTML.replace('<input type="hidden" name="receiver" value="">', `<input type="hidden" name="receiver" value="${data.username}">`)}
                                </form>
                            </div>
                        `;
                        parentElement.appendChild(childElement);
                    }
                }
            }
        }
    }

    usersListUpdateSock.onclose = function (event) {
        console.log('UsersListUpdate WS - Player connected.');
    };
}

document.addEventListener('DOMContentLoaded', (event) => {
    runsocketUsersListUpdate();
});
