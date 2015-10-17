$(document).ready(function(){
    $('#addPlaylistModal').on('shown.bs.modal', function (event) {
        var modal = $(this);
        modal.find('input[name="playlist_name"]').focus();
    });
    // Submit the playlist creation form on enter key press.
    $('#id_playlist_name').keypress(function (e) {
        var key = e.which;
        if(key == 13)  // Enter key
        {
            $(this).parents("form").first().submit()
        }
    });
});