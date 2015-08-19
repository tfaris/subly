$(document).ready(function(){
    var filterTable = $("#filters");
    filterTable.on('change', 'input,select', function(){
        filterChanged($(this));
    });
    //filterTable.find("input,select").change(function(){filterChanged($(this))});
    $("#advanced-controls").change(function(){
        showAdvancedControls(this.checked);
    });
    showAdvancedControls(false);
    filterTable.on("click", '.delete-control .close', function(){
        filterDelete($(this));
    });
    $(".btn-add-filter").click(addNewFilter);
});

/**
 * Returns whether advanced controls are being shown or not.
 */
function getAdvancedControlsShown(){
    return $("#advanced-controls").prop("checked");
}

/**
 * Show or hide advanced controls.
 * @param show
 */
function showAdvancedControls(show){
    var filterTable = $("#filters");
    $(".advanced-controls-col").each(function(){
        var colNumber = $(this).index() + 1,
            attrFltr = "nth-child(" + colNumber + ")",
            el = filterTable.find("td:" + attrFltr + ",th:" + attrFltr);
        if (show) {
            el.show();
        }
        else{
            el.hide();
        }
    });
}

/**
 * Get a useful error message from the specified ajax result.
 * @param data
 * @returns {*}
 */
function getAjaxError(data){
    if (data.responseJSON) {
        return data.responseJSON.error;
    }
    else{
        return data.status + " " + data.statusText;
    }
}

/**
 * Display the specified error message to the user (non-blocking).
 * @param msg
 */
function addErrorMessage(msg){
    $("<div class='alert alert-warning alert-warning alert-dismissable' role='alert'>" +
        "<button type='button' class='close' data-dismiss='alert' aria-label='Close'><span aria-hidden='true'>&times;</span></button>"+
        msg +"</div>").insertBefore(".filter-table-controls");
}

/**
 * Get the jQuery selector that can be used to select all
 * elements related to the filter with the specified id.
 * @param filterId
 * @returns {jQuery|HTMLElement}
 */
function getFilterSelector(filterId){
    return $("[data-id="+ filterId +"]");
}

/**
 * Get a VideoFilter object from the element, which should have a "data-id"
 * attribute.
 * @param el
 */
function getFilterFromElement(el){
    var filterId = el.data("id"),
        filterOpts = {id: filterId};
    getFilterSelector(filterId).map(function(){
        var dataObj = $(this),
            dataType = dataObj.attr("type") || dataObj.prop("tagName"),
            val;
        switch (dataType.toLowerCase()){
            case "checkbox":
            case "radio":
                val = dataObj.prop("checked");
                break;
            default:
                val = dataObj.val();
                break;
        }
        return {
            key: dataObj.data("field"),
            val: val
        };
    }).each(function(){
        filterOpts[this.key] = this.val;
    });
    return VideoFilter(filterOpts);
}

/**
 * Update the filter.
 * @param el
 */
function filterChanged(el){
    submitFilterChange(getFilterFromElement(el)).fail(function(data){
        addErrorMessage(getAjaxError(data));
    });
}

/**
 * Delete the filter.
 * @param el
 */
function filterDelete(el){
    var filter = getFilterFromElement(el);
    deleteFilter(filter).fail(function(data){
        addErrorMessage(getAjaxError(data));
    }).success(function(){
        getFilterSelector(filter.id).parents('tr').remove();
    });
}

/**
 * Create a new VideoFilter and add controls to edit it.
 */
function addNewFilter(){
    var playlistId = $("input[name='playlist-id']").val();
    newFilterHtml(playlistId).fail(function(data){
        addErrorMessage(getAjaxError(data));
    }).success(function(data){
        $(data.content).insertBefore("#filters tbody tr:eq(0)").find("input:eq(0)").focus();
        showAdvancedControls(getAdvancedControlsShown());
    });
}