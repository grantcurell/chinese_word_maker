$('.leftnavbar2').scroll(function() {
    sessionStorage.scrollTop = $(this).scrollTop();
});  

$( document ).ready(function() {    
    var pos = window.location.href.lastIndexOf("/");
    var element_id = "a_" + window.location.href.substring(pos + 1);
    
    $('#' + element_id).addClass('active2');
    if (sessionStorage.scrollTop != "undefined") {
        $('.leftnavbar2').scrollTop(sessionStorage.scrollTop);
    }    
});