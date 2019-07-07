$( document ).ready(function() {
    if (location.pathname == "/"){
        $('#tn_kit_configuration').addClass('active');
    } else if (location.pathname == "/help"){
        $('#tn_help').addClass('active');
    } else if (location.pathname == "/kickstart"){
        $('#tn_kickstart').addClass('active');
    } else if (location.pathname == "/kit_configuration"){
        $('#tn_kit_configuration').addClass('active');
    } else if (location.pathname.startsWith("/OJCCTM")){
        $('#tn_capabilities_by_category_softwareortools').addClass('active');
    } else if (location.pathname.startsWith("/THISISCVAH")){        
        $('#tn_system_design').addClass('active');
    }
});