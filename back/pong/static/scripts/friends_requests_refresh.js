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
	console.log('Recu par le JS suite au Send_invite:', data)
	if (data.type === 'friends_requests_update') {

		var userElement = document.getElementById('userRemove-' + data.friend_id);
		userElement.parentNode.removeChild(userElement);
		var friendElement = document.createElement('li');
		friendElement.innerHTML = `
			<div class="d-flex justify-content-between align-items-center col-10 bg-white bg-opacity-25 mb-2 rounded shadow-sm mx-auto p-3">
				<div class="d-flex align-items-center">
					<img id="status-indicator-${data.friend_id}" class="rounded-circle me-2
					{% if ${data.friend_status} == 'is_online' %}border border-2 border-success
                    {% elif ${data.friend_status} == 'is_playing' %}border border-2 border-danger
                    {% elif ${data.friend_status} == 'is_offline' %}
					{% endif %}" src="${data.friend_avatar}" alt="Friend avatar" style="width: 35px; height: 35px;">
					<div style="max-width: 7ch; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
						${data.friend_username} ${data.friend_id}
					</div>
				</div>
				<button class="btn buttonfriends btn-sm btn-dark shadow-sm" data-translate="profile" style="--bs-btn-font-size: .75rem;"
					id="profile-${data.friend_id}"
					type="button" data-bs-toggle="popover"
					title="${data.friend_username} profile"
					data-bs-custom-class="custom-popover"
					data-bs-html="true"
					data-bs-content="
					<i class='bi bi-trophy-fill'></i> Won (${data.friend_stats.tourn}) tournament(s)
					<br><i class='bi bi-joystick'></i> Played (${data.friend_stats.total}) matches:
					<br>&nbsp;&nbsp;&nbsp;&nbsp;<i class='bi bi-caret-right-fill'></i>won (${data.friend_stats.won})
					<br>&nbsp;&nbsp;&nbsp;&nbsp;<i class='bi bi-caret-right-fill'></i>lost (${data.friend_stats.lost})
					<br><i class='bi bi-calendar-check-fill'></i> Joined on ${data.friend_joined}
					">
					profile
				</button>
			</div>
			`;
		document.getElementById('friendsList').appendChild(friendElement);
		applyTranslation

		var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
		var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
			return new bootstrap.Popover(popoverTriggerEl)
})
	}
	else if (data.type == 'new_friend_request') {

		var acceptButton = document.createElement('button');
		acceptButton.innerHTML = '<i class="bi bi-check-square"></i>';
		acceptButton.classList.add('btn', 'buttonvalid', 'px-2', 'btn-sm', 'btn-primary', 'shadow-sm');
		acceptButton.style.setProperty('--bs-btn-font-size', '.75rem');
		acceptButton.addEventListener('click', function() {
			handleInvite(data.friend_username, 'accepted');
		});

		var rejectButton = document.createElement('button');
		rejectButton.innerHTML = '<i class="bi bi-x-square"></i>';
		rejectButton.classList.add('btn', 'buttonvalid', 'px-2', 'btn-sm', 'btn-danger', 'shadow-sm');
		rejectButton.style.setProperty('--bs-btn-font-size', '.75rem');
		rejectButton.addEventListener('click', function() {
			handleInvite(data.friend_username, 'rejected');
		});

		newRequestElement.innerHTML = `
		<div id="userRemove-${data.friend_id}" class="d-flex justify-content-between align-items-center col-10 bg-white bg-opacity-25 p-3 mb-2 rounded shadow-sm mx-auto">
			<div class="d-flex align-items-center">
				<img class="rounded-circle me-2" src="${data.friend_avatar}" alt="" style="width: 35px; height: 35px;">
				<div style="max-width: 7ch; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
				${data.friend_username}
				</div>
			</div>
		</div>
		`;
		newRequestElement.appendChild(acceptButton);
		newRequestElement.appendChild(rejectButton);
		document.getElementById('usersList').appendChild(newRequestElement);
	}

	function handleInvite(inviteUsername, friendStatus) {
		fetch('/handle_invite', {
			method: 'POST',
			body: JSON.stringify({
				invite: inviteUsername,
				friend_status: friendStatus
			}),
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': getCookie('csrftoken')
			}
		}).then(response => response.json())
		  .then(data => {
			if (data.status === 'success') {
				window.location.href = '/';
			} else {
				alert(data.message);
			}
		});
	}
	};

	socket.onclose = function(e) {
	// console.log("Connection WS REFRESH FRIENDS closed");
	};
}

document.addEventListener('DOMContentLoaded', (event) => {
	runsocketFriends();
});
