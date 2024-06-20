var initialContent = document.getElementById('playDiv').innerHTML;
function attachEvent() {
    document.getElementById('playSingle').addEventListener('click', function() {
        document.getElementById('playDiv').innerHTML = `
        <div class="mb-2 text-center">
            <p class="mb-2" data-translate="1v1"><span id="backArrow" style="cursor: pointer;">
                <i class="bi bi-arrow-left text-light me-1"></i>
            </span>Play 1v1 match:</p>
            <button class="btn btn-dark btn-sm shadow-sm text-light col-6 mb-2" data-bs-toggle="modal" data-bs-target="#localMatchModal">Local
            </button>
            <button class="btn btn-primary btn-sm shadow-sm text-light col-6" data-translate="online" data-bs-toggle="modal" data-bs-target="#onlineMatchModal">Online
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
        <div class="mb-2 text-center">
            <p class="mb-2" data-translate="1v1"><span id="backArrow" style="cursor: pointer;">
                <i class="bi bi-arrow-left text-light me-1"></i>
            </span>Play a tournament:</p>
            <button class="btn btn-dark btn-sm shadow-sm text-light col-6 mb-2" data-bs-toggle="modal" data-bs-target="#localTournament">Local
            </button>
            <button class="btn btn-primary btn-sm shadow-sm text-light col-6" data-translate="online" data-bs-toggle="modal" data-bs-target="#onlineTournament">Online
            </button>
        </div>
        `;
        document.getElementById('backArrow').addEventListener('click', function() {
            document.getElementById('playDiv').innerHTML = initialContent;
            attachEvent();
            });
    });

    // var canvasModal = document.getElementById('localMatchModal');
    // canvasModal.addEventListener('hidden.bs.modal', function () {
    //     document.getElementById('playDiv').innerHTML = initialContent;
    // });

}

attachEvent();