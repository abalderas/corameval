var unsaved = false;

$(":input").change(function(){ //triggers change in all input fields including text type
    unsaved = true;
});

$("#university").change(function(){ //triggers change in all input fields including text type
    unsaved = false;
});

$("#area").change(function(){ //triggers change in all input fields including text type
    unsaved = false;
});

$("#titulo").change(function(){ //triggers change in all input fields including text type
    unsaved = false;
});

$("#asignatura").change(function(){ //triggers change in all input fields including text type
    unsaved = false;
});

$("#nivel1").change(function(){ //triggers change in all input fields including text type
    unsaved = false;
});

$("#nivel2").change(function(){ //triggers change in all input fields including text type
    unsaved = false;
});

$(':submit').click(function() {
    unsaved = false;
});

function unloadPage(){ 
    if(unsaved){
        return "You have unsaved changes on this page. Do you want to leave this page and discard your changes or stay on this page?";
    }
}

window.onbeforeunload = unloadPage;