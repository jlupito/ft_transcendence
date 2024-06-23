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
	console.log("Friend_Request socket is open");
	};

	socket.onmessage = function(e) {
	var data = JSON.parse(e.data);
	console.log("request type:", data.type);
	if (data.type === 'accept_f_request') {

		var userElement = document.getElementById('userRemove-' + data.friend_id);
		userElement.parentNode.removeChild(userElement);
		var friendElement = document.createElement('li');
		friendElement.innerHTML = `
			<div class="d-flex justify-content-between align-items-center col-10 bg-white bg-opacity-25 mb-2 rounded shadow-sm mx-auto p-3">
				<div class="d-flex align-items-center">
					<img id="status-indicator-${data.friend_id}" class="rounded-circle me-2 {% if ${data.friend_is_online} %}border border-2 border-success{% endif %}" src="${data.friend_avatar}" alt="Friend avatar" style="width: 35px; height: 35px;">
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
	else if (data.type == 'send_f_request') {

		// Suppression de l'ancien élément de demande d'ami s'il existe
		console.log("data_sender:", data.friend_sender)
		console.log("data_recever:", data.friend_receiver)
		var oldReceiverElement = document.getElementById('userDiv-' + data.friend_receiver.id);
		if (oldReceiverElement) {
			oldReceiverElement.remove();
		}
		var newReceiverElement = document.createElement('li');
		newReceiverElement.innerHTML = `
		<div id="userProfile-${data.friend_receiver.id}" class="d-flex justify-content-between align-items-center col-10 bg-white bg-opacity-25 p-3 mb-2 rounded shadow-sm mx-auto">
			<div class="d-flex align-items-center">
                <img class="rounded-circle me-2" src="${data.friend_receiver.avatar}" alt="" style="width: 35px; height: 35px;">
                <div style="max-width: 7ch; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                ${data.friend_receiver.username}
                </div>
			</div>
			<button class="btn buttonfriends btn-sm btn-primary shadow-sm" disabled
            style="--bs-btn-font-size: .75rem;" data-translate="pending">pending</button>
		</div>
		`;
		document.getElementById('usersList').appendChild(newRequestElement);

		// Suppression de l'ancien élément de demande d'ami s'il existe
		var oldSenderElement = document.getElementById('userDiv-' + data.friend_sender.id);
		if (oldSenderElement) {
			oldSenderElement.remove();
		}
		// Creation du nouvel élément de demande d'ami avec accept ou reject
		var newSenderElement = document.createElement('li');
		newSenderElement.innerHTML = `
		<div id="userProfile-${data.friend_sender.id}" class="d-flex justify-content-between align-items-center col-10 bg-white bg-opacity-25 p-3 mb-2 rounded shadow-sm mx-auto">
			<div class="d-flex align-items-center">
                <img class="rounded-circle me-2" src="${data.friend_sender.avatar}" alt="" style="width: 35px; height: 35px;">
                <div style="max-width: 7ch; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                ${data.friend_sender.username}
                </div>
			</div>
			<form action="handle_invite" method="POST">
				<input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                <input type="hidden" name="invite" value="${data.friend_sender.username}">
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
		console.log("Friend_Request socket is close", e.code, e.reason);
	};
}

runsocketFriends();