// Script pour gerer la reception d'invitation par un autre joueur

document.querySelectorAll('.handle-invite-button').forEach(button => {
    button.addEventListener('click', function(event) {
        console.log('Form HANDLE INVITE submitted');
        event.preventDefault();

        var inviteUsername = event.target.nextElementSibling.nextElementSibling.value;

        console.log('inviteUsername: ', inviteUsername);
        
        fetch('/handle_invite', {
            method: 'POST',
            body: JSON.stringify({
                invite: inviteUsername,
                friend_status: 'accepted'
            }),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')  // Assuming you have a function to get the CSRF token
            }
        }).then(response => response.json())
          .then(data => {
            if (data.status === 'success') {
                // If the operation was successful, redirect to the home page
                window.location.href = '/';
            } else {
                // Otherwise, display the error message
                alert(data.message);
            }
        });
    });
});
