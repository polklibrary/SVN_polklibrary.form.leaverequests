$(document).ready(function(){
    
    // Form setup
    $('#form-widgets-workflow_status').attr('disabled','true');
    
    if ($.trim($('#form-widgets-title').val()) == '') {
        var name = $('#travel-request-injection').attr('data-name');
        $('#form-widgets-title').val(name);
    }
    if ($.trim($('#form-widgets-email').val()) == '') {
        var email = $('#travel-request-injection').attr('data-email');
        $('#form-widgets-email').val(email);
    }
    
    
    
    $('#form').prepend('<ul id="travel-info"></ul>');
    
    $('#travel-info').append('<li>Professional travel is encouraged in the UWO Libraries. Travel must be relevant to current job duties.</li>');
    $('#travel-info').append('<li>Travel funding is dependent on the budget. </li>');
    $('#travel-info').append('<li>Academic staff may request full reimbursement for travel.</li>');
    $('#travel-info').append('<li>University staff may request up to $500 per fiscal year for travel.</li>');
    $('#travel-info').append('<li>All employees must be employed for at least one year prior to requesting funding.</li>');
    $('#travel-info').append('<li>Some travel may be eligible for <a target="_blank" href="https://uwosh.edu/uss/awards-and-grants/university-staff-grant/">university staff</a> or <a target="_blank" href="https://uwosh.edu/sas/aspdf/">academic staff</a> professional development grants from the campus. Please pursue these options, when possible, to reduce the cost to the library.</li>');
    
    
    
    $('#form-widgets-workflow_status_comments').attr('readonly',true);
    
    
    
    
    
    
    
    
});