var initialContent = document.getElementById('playDiv').innerHTML;
function attachEvent() {
    document.getElementById('playSingle').addEventListener('click', function() {
        document.getElementById('playDiv').innerHTML = `
        <div class="mt-3 mb-3 text-center text-light">
            <span id="backArrow" style="cursor: pointer;">
                <i class="bi bi-arrow-left text-light me-1"></i>
            </span>Play 1v1 match:
        </div>
        <div class="mb-3 text-center">
            <button class="btn btn-dark btn-sm shadow-sm text-light col-6 mb-2" data-bs-toggle="modal" data-bs-target="#localMatchModal">local
            </button>
            <button class="btn btn-primary btn-sm shadow-sm text-light col-6 mb-3" data-bs-toggle="modal" data-bs-target="#onlineMatchModal">online
            </button>
        </div>
        `;
        document.getElementById('backArrow').addEventListener('click', function() {
            document.getElementById('playDiv').innerHTML = initialContent;
            attachEvent();	
            });
    });
    document.getElementById('playTournament').addEventListener('click', function() {
        document.getElementById('playDiv').innerHTML = `
        <div class="mt-3 mb-3 text-center text-light">
            <span id="backArrow" style="cursor: pointer;">
                <i class="bi bi-arrow-left text-light me-1"></i>
            </span>Play a tournament:
        </div>
        <div class="mb-3 text-center">
            <button class="btn btn-dark btn-sm shadow-sm text-light col-6 mb-2" data-bs-toggle="modal" data-bs-target="#localTournament">local
            </button>
            <button class="btn btn-primary btn-sm shadow-sm text-light col-6 mb-3" data-bs-toggle="modal" data-bs-target="#onlineTournament">online
            </button>
        </div>
        `;
        document.getElementById('backArrow').addEventListener('click', function() {
            document.getElementById('playDiv').innerHTML = initialContent;
            attachEvent();
            });
    });

}

attachEvent();