$(document).ready(function(){
    $('[data-toggle="popover"]').popover({ trigger: "hover" });
    // if list_id in url, click the panel-header to un-collapse it and change the plus to minus
    if(window.location.hash) {
        var hash = window.location.hash.substring(1)
        // Only try to open panels if the hash is a number
        if(!isNaN(hash)) {
            $('#panel-heading-' + hash).click()
            setTimeout(function(){
                $('#l-' + hash + ' #new-item-name').focus();
            }, 1);
        }
    }
});
$('.edit-item-in-pantry-button').click(function(e){
    var item_id = this.dataset.itemid;
    var list_id = this.dataset.listid;
    // hide pantry button
    $('#add-item-to-pantry-button-' + item_id + '-' + list_id).hide();
    // show scan barcode button
    $('#scan-barcode-button-' + item_id + '-' + list_id).removeClass('hidden');
    // init datepicker for last_purchased
    var picker1 = new Pikaday({
        field: $('#edit-item-in-pantry-form-' + item_id + '-' + list_id + ' #datepicker-last-purchased')[0],
        format: 'MM/DD/YYYY',
    });
    $('#edit-item-in-pantry-form-' + item_id + ' #datepicker-last-purchased').val($.datepicker.formatDate('mm/dd/yy', new Date()));
    // init datepicker for expiration_date
    var picker2 = new Pikaday({
        field: $('#edit-item-in-pantry-form-' + item_id + '-' + list_id + ' #datepicker-exp-date')[0],
        format: 'MM/DD/YYYY',
    });
});
$('.edit-item-in-pantry-button').click(function() {
    var list_id = this.dataset.listid;
    var item_id = this.dataset.itemid;
    console.log("CLICKED ITEM "+item_id+" LIST "+list_id)
    $('#edit-item-in-pantry-form-' + item_id + '-' + list_id).removeClass('hidden')
});
$('.panel-heading').click(function() {
    var list_id = this.dataset.listid;
    // If collapsed, change plus to minus
    if($('#panel-body-' + list_id).hasClass('collapse')) {
        $('#' + list_id + '-collapse-indicator').removeClass('fa-plus')
        $('#' + list_id + '-collapse-indicator').addClass('fa-minus')
    }
    // change minus to plus
    else {
        $('#' + list_id + '-collapse-indicator').removeClass('fa-minus')
        $('#' + list_id + '-collapse-indicator').addClass('fa-plus')
    }
    $('#panel-body-' + list_id).toggleClass('collapse in');
});
// Show the user a confirmation form so they don't accidentally delete their lists
$('.delete-list-button').click(function() {
    var list_id = this.dataset.listid;
    // Hide the initial delete button
    $('#delete-list-' + list_id).addClass('hidden');
    // Show confirmation form
    $('#delete-list-confirmation-form-' + list_id).removeClass('hidden');
});
// Hide the confirmation form when the user presses the don't delete button
$('.delete-list-cancel-button').click(function() {
    var list_id = this.dataset.listid;
    // Hide confirmation form
    $('#delete-list-confirmation-form-' + list_id).addClass('hidden');
    // Show initial delete button
    $('#delete-list-' + list_id).removeClass('hidden');
});
