// fonction pour recuperer les cookies avec le csrf_token
function getCookie(name) {

	let cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		const cookies = document.cookie.split(';');
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}
const csrf_token = getCookie('csrftoken');

// Script principal de gestion des demandes d'amis
function runsocketFriends() {

	let url = `wss://${window.location.host}/ws/friends_requests/`
	var socket = new WebSocket(url);

	socket.onopen = function(e) {
	console.log("Friend_Request Connection WS is established");
	};

	socket.onmessage = function(e) {
	var data = JSON.parse(e.data);

	if (data.type === 'friends_requests_update') {

		var userElement = document.getElementById('userRemove-' + data.friend_id);
		userElement.parentNode.removeChild(userElement);
		var friendElement = document.createElement('li');
		friendElement.innerHTML = `
			<div class="d-flex justify-content-between align-items-center col-10 bg-white bg-opacity-25 mb-2 rounded shadow-sm mx-auto p-3">
				<div class="d-flex align-items-center">
					<div class="position-relative">
						<img class="rounded-circle me-2" src="${data.friend_avatar}" alt="Friend avatar" style="width: 35px; height: 35px;">
						<div id="status-indicator-${data.friend_id}" class="position-absolute top-0 end-1" style="width: 10px; height: 10px; background-color: ${data.friend_is_online ? 'rgb(46, 206, 86)' : 'rgb(255, 0, 0)'}; border-radius: 50%;"></div>
					</div>
					<div style="max-width: 7ch; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
						${data.friend_username}
					</div>
				</div>
				<button class="btn buttonfriends btn-sm btn-dark shadow-sm" style="--bs-btn-font-size: .75rem;"
					data-bs-toggle="modal" data-bs-target="#friendsProfile">
					profile
				</button>
			</div>
		`;
		document.getElementById('friendsList').appendChild(friendElement);
	}
	else if (data.type == 'new_friend_request') {

		// Suppression de l'ancien élément de demande d'ami s'il existe
		var addFriendButton = document.getElementById('addFriendButton-' + data.friend_id);
		if (addFriendButton) {
			addFriendButton.remove();
		}
		// Suppression de l'ancien élément de demande d'ami s'il existe
		var oldRequestElement = document.getElementById('userRemove-' + data.friend_id);
		if (oldRequestElement) {
			oldRequestElement.remove();
		}
		// Creation du nouvel élément de demande d'ami avec accept ou reject
		var newRequestElement = document.createElement('li');
		newRequestElement.innerHTML = `
		<div id="userRemove-${data.friend_id}" class="d-flex justify-content-between align-items-center col-10 bg-white bg-opacity-25 p-3 mb-2 rounded shadow-sm mx-auto">
			<div class="d-flex align-items-center">
                <img class="rounded-circle me-2" src="${data.friend_avatar}" alt="" style="width: 35px; height: 35px;">
                <div style="max-width: 7ch; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                ${data.friend_username}
                </div>
			</div>
			<form action="handle_invite" method="POST">
				<input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                <input type="hidden" name="invite" value="${data.friend_username}">
                <button type="submit" name="friend_status" value="accepted" class="btn buttonvalid px-2 btn-sm btn-primary shadow-sm"
                style="--bs-btn-font-size: .75rem;"><i class="bi bi-check-square"></i></button>
                <button type="submit" name="friend_status" value="rejected" class="px-2 buttonvalid btn btn-sm btn-danger shadow-sm"
                style="--bs-btn-font-size: .75rem;"><i class="bi bi-x-square"></i></button>
			</form>
		</div>
		`;
		document.getElementById('usersList').appendChild(newRequestElement);
	}
	};

	socket.onclose = function(e) {
	console.log("Connection WS REFRESH FRIENDS closed");
	};
}

document.addEventListener('DOMContentLoaded', (event) => {
	runsocketFriends();
});
