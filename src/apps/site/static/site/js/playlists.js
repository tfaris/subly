$(document).ready(function(){
    $('#addPlaylistModal').on('shown.bs.modal', function (event) {
        var modal = $(this);
        modal.find('input[name="playlist_name"]').focus();
    });
});