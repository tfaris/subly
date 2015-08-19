/**
 * Get the value of the cookie with the specified name.
 * @param name
 */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Return true if the HTTP method type does not need CSRF.
 * @param method
 */
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

// Setup Ajax calls to add a CSRF token when needed.
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        }
    }
});

/**
 * Update the specified filter.
 * @param filter
 */
function submitFilterChange(filter){
    return $.ajax({
        type: "POST",
        url: "filter/update/",
        data: filter,
        dataType: "json"
    });
}

/**
 * Delete the specified filter.
 * @param filter
 */
function deleteFilter(filter){
    return $.ajax({
        type: "POST",
        url: "filter/delete/",
        data: filter,
        dataType: "json"
    });
}

/**
 * Add a filter to the playlist with the specified id
 * and request HTML for editing that filter.
 * @param playlistId
 * @returns {*}
 */
function newFilterHtml(playlistId){
    return $.ajax({
        type: "GET",
        url: "filter/new/",
        data: {playlistId: playlistId},
        dataType: "json"
    });
}

var VideoFilter = function(options){
    if (!options){
        options = {};
    }
    var vf = {};
    /* These are defined here mostly to provide an expected interface for VideoFilter instances... */
    vf.id = options.id;
    vf.string = options.string;
    vf.channel_title = options.channel_title;
    vf.ignore_case = options.ignore_case;
    vf.field = options.field;
    vf.is_regex = options.is_regex;
    vf.exact = options.exact;
    vf.exclusion = options.exclusion;
    return vf;
};