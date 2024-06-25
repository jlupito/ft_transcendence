// Script pour gerer l'envoi d'invitation à un autre joueur

document.querySelectorAll('.add-friend-button').forEach(button => {
    button.addEventListener('click', function(event) {
        console.log('Send INVITE submitted'); //ok
        event.preventDefault();

        var receiverUsername = event.target.previousElementSibling.value;
        console.log('receiverUsername: ' + receiverUsername); //ok
        fetch('/send_invite', {
            method: 'POST',
            body: JSON.stringify({
                receiver: receiverUsername
            }),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')  // Assuming you have a function to get the CSRF token
            }
        }).then(response => response.json())
          .then(data => {
            console.log(data);
            if (data.status === 'success') {
                event.target.remove();
            } else {
                alert(data.message);
            }
        });
    });
});
