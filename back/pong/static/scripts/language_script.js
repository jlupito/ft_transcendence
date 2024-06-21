// script pour les traductions

function runSocketLanguage() {
    let url = `wss://${window.location.host}/ws/language/`
    const languageSock = new WebSocket(url);
    
    var translations = {
        "english": {
            "welcome": "Welcome",
            "edit": "Edit profile",
            "update": "Update profile",
            "username": "Username",
            "picture": "Profile picture",
            "save": "Save",
            "close": "Close",
            "language": "Language",
            "author": "Authors",
            "game": "Game",
            "play": "Play a:",
            "tournament": "Tournament",
            "won": "Win(s)",
            "lost": "Defeat(s)",
            "tourn": "Tournament(s) won",
            "1v1": "Play a 1v1 match:",
            "online": "Online",
            "users": "Users",
            "profile": "profile",
            "pending": "pending",
            "add": "add friend",
            "playpong": "Pong",
            "account": "No account yet?",
            "signin": "Sign in",
            "here": "Sign up here",
            "or": "or",
            "42login": "Log in with",
            "signup": "Sign up",
            "email": "Email adress",
            "password": "Password",
            "submit": "Submit",
        },
        "français": {
            "welcome": "Bienvenue",
            "edit": "Modifier profil",
            "update": "Mise à jour du profil",
            "username": "Nom d'utilisateur",
            "picture": "Photo de profil",
            "save": "Enregistrer",
            "close": "Fermer",
            "language": "Langue",
            "author": "Auteurs",
            "game": "Jeu",
            "play": "Démarrer un :",
            "tournament": "Tournoi",
            "won": "Victoire(s)",
            "lost": "Défaite(s)",
            "tourn": "Tournoi(s) gagné(s)",
            "1v1": "Jouer un match 1v1 :",
            "online": "En ligne",
            "users": "Utilisateurs",
            "profile": "profil",
            "pending": "attente",
            "add": "ajouter",
            "playpong": "Pong",
            "account": "Pas de compte?",
            "signin": "Se connecter",
            "here": "Inscris-toi ici.",
            "or": "ou",
            "42login": "Se connecter avec",
            "signup": "S'enregistrer",
            "email": "Adresse email",
            "password": "Mot de passe",
            "submit": "Confirmer",
        },
        "español": {
            "welcome": "Bienvenido",
            "edit": "Editar perfil",
            "update": "Actualización del perfil",
            "username": "Nombre de usuario",
            "picture": "Foto de perfil",
            "save": "Guardar",
            "close": "Cerrar",
            "language": "Idioma",
            "author": "Autores",
            "game": "Juego",
            "play": "Iniciar un :",
            "tournament": "Torneo",
            "won": "Exitos",
            "lost": "Derrotas",
            "tourn": "Torneo(s) ganado(s)",
            "1v1": "Jugar un partido 1v1 :",
            "online": "En línea",
            "users": "Usuarios",
            "profile": "perfil",
            "pending": "pendiente",
            "add": "añadir",
            "playpong": "Pong",
            "account": "No cuenta?",
            "signin": "Iniciar sesión",
            "here": "Registrate acqui.",
            "or": "o",
            "42login": "Iniciar sesión con",
            "signup": "Registrarse",
            "email": "Correo electrónico",
            "password": "Contraseña",
            "submit": "Confirmar",
        }
    };

    function applyTranslation(language) {
        console.log("appel de la focntion traduction:", language)
        var elements = document.querySelectorAll('[data-translate]');
        elements.forEach(function(element) {
            var translation = translations[language][element.getAttribute('data-translate')];
            if (translation) {
                element.textContent = translation;
            }
        });
    }

    var buttons = document.querySelectorAll('.chooseLanguage');
    buttons.forEach(function(button) {
    button.addEventListener('click', function() {
        var language = this.textContent.trim().toLowerCase();
        applyTranslation(language);
        var message = {
            action: 'set_language',
            language: language
        };
        // console.log("message envoyé du js:", message)
        languageSock.send(JSON.stringify(message));
        });
    });

    languageSock.onopen = function() {
        var message = {
            action: 'get_language'
        };
        languageSock.send(JSON.stringify(message));
    };

    languageSock.onmessage = function(event) {
        var message = JSON.parse(event.data);
        if (message.action === 'get_language') {
            var language = message.language;
            // console.log("message recu dans js language received:", language)
            applyTranslation(language);
            // document.querySelector('button[data-translate="language"]').textContent = language;
            // document.querySelector('.chooseLanguage.active').classList.remove('active');
            // document.querySelector('.chooseLanguage:contains("' + language + '")').classList.add('active');
        }
    };

}
runSocketLanguage();