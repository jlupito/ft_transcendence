var initialContent = document.getElementById('playDiv').innerHTML;
function attachEvent() {
    document.getElementById('playSingle').addEventListener('click', function() {
        document.getElementById('playDiv').innerHTML = `
        <div class="mt-2 mb-3 text-center text-light">
            <button id="backArrow" style="cursor: pointer; background: none; border: none;">
                <i class="bi bi-arrow-left-square-fill text-light me-1"></i>
            </button>Play 1v1 match:
        </div>
        <div class="mb-3 text-center">
            <button type="" class="btn btn-dark btn-sm shadow-sm text-light col-6 mb-2" data-bs-toggle="modal" data-bs-target="#localmatchModal">local
            </button>
            <button type="" class="btn btn-primary btn-sm shadow-sm text-light col-6" data-bs-toggle="modal" data-bs-target="#matchModal">online
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
        <div class="mt-2 mb-3 text-center text-light">
            <button id="backArrow" style="cursor: pointer; background: none; border: none;">
                <i class="bi bi-arrow-left-square-fill text-light me-1"></i>
            </button>Play a tournament:
        </div>
        <div class="mb-3 text-center">
            <button type="" class="btn btn-dark btn-sm shadow-sm text-light col-6 mb-2" data-bs-toggle="modal" data-bs-target="#localTournament">local
            </button>
            <button type="" class="btn btn-primary btn-sm shadow-sm text-light col-6" data-bs-toggle="modal" data-bs-target="#onlineTournament">online
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