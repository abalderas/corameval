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

$("#username").change(function(){ //triggers change in all input fields including text type
    unsaved = false;
});

$("#password").change(function(){ //triggers change in all input fields including text type
    unsaved = false;
});

$(':submit').click(function() {
    unsaved = false;
});

$("#correccion").change(function(){ //correccion medios
    if ($(this).val() == 0)
    {
        $('#autenticidad').prop('disabled', true);
        $('#observaciones').prop('disabled', true);
        $('#verificabilidad').prop('disabled', true);
        $('#cognitivo').prop('disabled', true);
        $('#factual').prop('disabled', true);
        $('#procedimental').prop('disabled', true);
        $('#conceptual').prop('disabled', true);
        $('#metacognitivo').prop('disabled', true);
        $('#estructura').prop('disabled', true);
        $('#afectivo').prop('disabled', true);
        $('#tecnologico').prop('disabled', true);
        $('#colaborativo').prop('disabled', true);
    }
    else
    {
        $('#autenticidad').prop('disabled', false);
        $('#observaciones').prop('disabled', false);
        $('#verificabilidad').prop('disabled', false);
        $('#cognitivo').prop('disabled', false);
        $('#factual').prop('disabled', false);
        $('#procedimental').prop('disabled', false);
        $('#conceptual').prop('disabled', false);
        $('#metacognitivo').prop('disabled', false);
        $('#estructura').prop('disabled', false);
        $('#afectivo').prop('disabled', false);
        $('#tecnologico').prop('disabled', false);
        $('#colaborativo').prop('disabled', false);
        $('#aplicar').prop('disabled', false);
    }
});

function unloadPage(){ 
    if(unsaved){
        return "You have unsaved changes on this page. Do you want to leave this page and discard your changes or stay on this page?";
    }
}

window.onbeforeunload = unloadPage;