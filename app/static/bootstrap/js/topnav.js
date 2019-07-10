$( document ).ready(function() {
    if (location.pathname == "/"){
        $('#tn_character').addClass('active');
    } else if (location.pathname == "/help"){
        $('#tn_help').addClass('active');
    } else if (location.pathname == "/character"){
        $('#tn_character').addClass('active');
    }
});