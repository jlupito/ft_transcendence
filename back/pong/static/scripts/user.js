//function getCookie(name) {
//    let cookieValue = null;
//    if (document.cookie && document.cookie !== '') {
//        const cookies = document.cookie.split(';');
//        for (let i = 0; i < cookies.length; i++) {
//            const cookie = cookies[i].trim();
//            if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                break;
//            }
//        }
//    }
//    return cookieValue;
//}

//document.addEventListener('DOMContentLoaded', function() {
//    var loginForm = document.getElementById('loginForm');
//    if (loginForm) {
//        loginForm.addEventListener('submit', function(event) {
//            console.log('ds user.js loginForm'); 
//			event.preventDefault(); // Empêche le formulaire de soumettre normalement
			
//			var formData = new FormData(this);
//			console.log('formData', formData);
//			fetch('/login', {
//				method: 'POST',
//				body: formData,
//				headers: {'X-CSRFToken': getCookie('csrftoken')}
//			})
//			.then(response => {
//				//console.log('response');
//				return response.json();
//			})
//			.then(data => {
//				console.log(data);
//				//try{
//					if (data.status === 'success') {
//						window.location.href = '/verify';
//					}
//					else{
//						window.location.href = '';
//						//messages.error(request, 'Invalid username or password')
//					}
//				//}catch(e){
//					//console.log('Login failed '), e;
//				//}
//			})
//			//.catch(function(error) {
//			//	messages.error(request, 'Invalid username or password')
//			//	//console.error('Error:', error);
//			//});
//		});
//    }

//    var verifyForm = document.getElementById('verifyForm');
//    if (verifyForm) {
//        verifyForm.addEventListener('submit', function(event) {
//			id = request.session.get('id')
//			console.log('ds user.js verifyForm', id);
//			event.preventDefault();
			
//			var formData = new FormData(this);
//			console.log('formData', formData);
//			fetch('/verify', {
//				method: 'POST',
//				body: formData,
//				headers: {'X-CSRFToken': getCookie('csrftoken')}
//			}).then(response => {
//				console.log('response');
//				return response.json();
//			}).then(data => {
//				try{
//					if (data.status === 'success') {
//						console.log("ds js user.js verifyForm success")
//						//window.location.href = 'https://localhost:8001/home/';
//						//window.location.href = '';
//					}
//				}catch(e){
//					console.e('Login failed '), e;
//				}
//			}).catch(function(error) {
//				console.error('Error:', error);
//			});
//        });
//    }
	
//	var registerForm = document.getElementById('registerForm');
//    if (registerForm) {
//        registerForm.addEventListener('submit', function(event) {
//			console.log('ds user.js registerForm');
//			event.preventDefault();
			
//			var formData = new FormData(this);
//			console.log('avant fetch');
//			fetch('/register', {
//				method: 'POST',
//				body: formData,
//				headers: {'X-CSRFToken': getCookie('csrftoken')}
//				//headers: {	'X-CSRFToken': document.getElementById('csrf_token').value }
//			})
//			.then(response => {
//				console.log('response');
//				return response.json();
//			})
//			.then(data => {
//				//try{
//					if (data.status === 'success') {
//						console.log("ds js user.js registerForm success")
//						//window.location.href = '';
//					}
//				//}catch(e){
//					//console.e('Login failed '), e;
//				//}
//			})
//			.catch(function(error) {
//				console.error('Error:', error);
//			});
//        });
//    }
//});

////document.getElementById('loginForm').addEventListener('submit', function(event) {
////	console.log('ds user.js loginForm'); 
////	event.preventDefault(); // Empêche le formulaire de soumettre normalement
	
////	var formData = new FormData(this);
////	//console.log('formData', formData);
////	fetch('/login', {
////		method: 'POST',
////		body: formData,
////		//headers: {	'X-CSRFToken': document.getElementById('csrf_token').value }
////		headers: {	'X-CSRFToken': data.token.token }
////	})
////	//.then(response => {
////	//	console.log('response', response);
////	//	return response.json();
////	//})
////	.then(data => {
////		console.log(data);
////		try{
////			//$('#loginModal').modal('hide');
////			if (data.status === 'success') {
////				console.log("ds js user.js loginForm success")
////				window.location.href = '/verify';
////			}
////			//else{
////			//	window.location.href = 'https://localhost:8001/home/';
////			//}
////		}catch(e){
////			//window.location.href = 'https://localhost:8001/home/';
////			log("ICI ds user.js loginForm catch")
////			console.e('Login failed '), e;
////		}
////	}).catch(function(error) {
////		console.error('Error:', error);
////	});
////});

////document.getElementById('verifyForm').addEventListener('submit', function(event) {
////	event.preventDefault(); 
	
////	var formData = new FormData(this);

////	fetch('/verify', {
////		method: 'POST',
////		body: formData,
////		headers: {	'X-CSRFToken': document.getElementById('csrf_token').value }
////	}).then(response => {
////		return response.json();
////	}).then(data => {
////		try{
////			if (data.status === 'success') {
////				window.location.href = '';
////			}
////		}catch(e){
////			console.e('Login failed '), e;
////		}
////	}).catch(function(error) {
////		console.error('Error:', error);
////	});
////});

////document.getElementById('registerForm').addEventListener('submit', function(event) {
//	//console.log('ds user.js registerForm');
//	//event.preventDefault();
	
//	//var formData = new FormData(this);
//	//console.log('avant fetch');
//	//fetch('/register', {
//	//	method: 'POST',
//	//	body: formData,
//	//	headers: {	'X-CSRFToken': document.getElementById('csrf_token').value }
//	//}).then(response => {
//	//	console.log('response');
//	//	return response.json();
//	//}).then(data => {
//	//	try{
//	//		if (data.status === 'success') {
//	//			console.log("ds js user.js registerForm success")
//	//			window.location.href = '';
//	//		}
//	//	}catch(e){
//	//		console.e('Login failed '), e;
//	//	}
//	//}).catch(function(error) {
//	//	console.error('Error:', error);
//	//});
////});