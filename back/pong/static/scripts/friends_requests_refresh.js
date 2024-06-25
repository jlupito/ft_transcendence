
// Script principal de gestion des demandes d'amis
function runsocketFriends() {

	let url = `wss://${window.location.host}/ws/friends_requests/`
	var socketFriends = new WebSocket(url);

	function handleClick(event) {
		if (event.target.matches('.button_friends')) {
			console.log("clique sur le bouton bien detecté");
			var data= {
				sender_id: event.target.getAttribute('data-sender'),
				receiver_id: event.target.getAttribute('data-receiver'),
				type: event.target.getAttribute('data-type')
			}
			console.log("data envoyé apres click sur le add button:", data);
			socketFriends.send(JSON.stringify({
				'data': data,
			}));
		}
	}

	socketFriends.onopen = function(e) {
	console.log("Friend_Request socket is open");
	};

	socketFriends.onmessage = function(e) {
	var data = JSON.parse(e.data);

	console.log("data reçue apr le JS:", data);

	if (data.type === 'accepted') {


	}
	else if (data.type === 'rejected') {
		console.log("data_sender:", data.receiver_id)
		console.log("data_recever:", data.sender_id)
		var receiverElement = document.getElementById('userDiv-' + data.receiver_id);
		console.log("receiverElement:", receiverElement)
		if (receiverElement) {
			console.log("tu rentres ici?")
			var button = document.getElementById("f_request_pending-" + data.receiver_id);
			console.log("button:", button)	
			receiverElement.removeChild(button);
			var newButton = document.createElement('div');
			newButton.innerHTML = `
			<button id="f_request_add-${ data.sender_id }" data-type="send_f_request" data-sender="${ data.receiver_id }" data-receiver="${ data.sender_id }" class="btn buttonfriends button_friends btn-sm btn-primary shadow-sm"
            style="--bs-btn-font-size: .75rem;" data-translate="add">add friend
             </button>
			`;
			receiverElement.appendChild(newButton);
		}

		var senderElement = document.getElementById('userDiv-' + data.receiver_id);
		if (senderElement) {
			var button = document.getElementById("f_request_pending-" + data.receiver_id);
			senderElement.removeChild(button);
			var newButton = document.createElement('div');
			newButton.innerHTML = `
			<button id="f_request_add-${ data.sender_id }" data-type="send_f_request" data-sender="${ data.receiver_id }" data-receiver="${ data.sender_id }" class="btn buttonfriends button_friends btn-sm btn-primary shadow-sm"
            style="--bs-btn-font-size: .75rem;" data-translate="add">add friend
             </button>
			`;
			senderElement.appendChild(newButton);
		}
	}

	else if (data.type == 'send_f_request') {


		var divS = document.getElementById("f_request_add-" + data.sender_id);
		if (divS) {
			console.log("la divs existe bien:", divS)
			var button = divS.querySelector('button');
			divS.removeChild(button);
			console.log("button:", button)	
			var newButton = document.createElement('div');
			newButton.innerHTML = `
            <button data-type="accepted" data-sender="${ data.receiver_id }" data-receiver="${ data.sender_id }" class="btn buttonvalid px-2 button_friends btn-sm btn-primary shadow-sm"
            style="--bs-btn-font-size: .75rem;"><i class="bi bi-check-square"></i></button>
            <button data-type="rejected" data-sender="${ data.receiver_id }" data-receiver="${ data.sender_id }" class="px-2 buttonvalid button_friends btn btn-sm btn-danger shadow-sm"
            style="--bs-btn-font-size: .75rem;"><i class="bi bi-x-square"></i></button>
			`;
			console.log("le newbutton1 dans la divS:", newButton)
			divS.appendChild(newButton);
			console.log(document.querySelector('.button_friends'))
			document.body.addEventListener('click', handleClick);

		}

		var divR = document.getElementById("f_request_add-" + data.receiver_id);
		if (divR) {
			console.log("la divR existe bien:", divR)
			var button = divR.querySelector('button');
			divR.removeChild(button);
			var newButton = document.createElement('div');
			newButton.innerHTML = `
			<button id="f_request_pending-${ data.sender_id }" class="btn buttonfriends btn-sm btn-primary shadow-sm" disabled
            style="--bs-btn-font-size: .75rem;" data-translate="pending">pending
			</button>
			`;
			console.log("le new button dans la divR:", newButton)
			divR.appendChild(newButton);
			console.log(document.querySelector('.button_friends'))
			document.body.addEventListener('click', handleClick);
		}
	}
	};

	// applyTranslation(language);
	socketFriends.onclose = function(e) {
		console.log("Friend_Request socket is close", e.code, e.reason);
	};
	document.body.addEventListener('click', handleClick);
}

runsocketFriends();