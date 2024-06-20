// script pour les traductions



function runSocketLanguage() {
    let url = `wss://${window.location.host}/ws/language/`
    const languageSock = new WebSocket(url);
    
    languageSock.onopen = function() {
        console.log("Language Connection WS is established");
        var message = {
            action: 'get_language'
        };
        languageSock.send(JSON.stringify(message));
    };

    languageSock.onmessage = function(event) {
        var message = JSON.parse(event.data);
        if (message.action === 'get_language') {
            var language = message.language;
            // Utilisez 'language' pour définir la langue de l'interface utilisateur
            document.querySelector('#language-select').value = language;
        }
    };

    document.querySelector('#language-select').addEventListener('change', function() {
        var message = {
            action: 'set_language',
            language: this.value
        };
        languageSock.send(JSON.stringify(message));
        // Mettez à jour la langue de l'interface utilisateur immédiatement
        // document.querySelector('#language-select').value = this.value;
    });

    document.addEventListener('DOMContentLoaded', function() {
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
                "authors": "Authors",
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
                "add": "Add friend",
    
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
                "authors": "Auteurs",
                "game": "Jeu",
                "play": "Démarrer un :",
                "tournament": "Tournoi",
                "won": "Victoires",
                "lost": "Défaites",
                "tourn": "Tournoi(s) gagné(s)",
                "1v1": "Jouer un match 1v1 :",
                "online": "En ligne",
                "users": "Utilisateurs",
                "profile": "profil",
                "pending": "attente",
                "add": "ajouter",
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
                "authors": "Autores",
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
            }
        };
        
        var buttons = document.querySelectorAll('.chooseLanguage');
        buttons.forEach(function(button) {
            button.addEventListener('click', function() {
                var language = this.textContent.trim().toLowerCase();
                var elements = document.querySelectorAll('[data-translate]');
                elements.forEach(function(element) {
                    var translation = translations[language][element.getAttribute('data-translate')];
                    if (translation) {
                        element.textContent = translation;
                    }
                });
    
                var message = {
                    action: 'set_language',
                    language: language
                };
                languageSock.send(JSON.stringify(message));
            });
        });
    });
}

runSocketLanguage();