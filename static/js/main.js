$(document).ready(function() {

    $(function () {
        $('[data-toggle="popover"]').popover()
      });

    $('#university').on('change', function(event) {
 
        listing_areas();
        $('#titulo').empty();
        $('#nivel1').empty();
        $('#nivel2').empty();
        $('#asignatura').empty();
        $('#credits').val('');
        $('#type').val('');

    });

   $('#area').on('change click', function(event) {

        listing_degrees();
        $('#nivel1').empty();
        $('#nivel2').empty();
        $('#asignatura').empty();
        $('#credits').val('');
        $('#type').val('');
    
   });

   $('#titulo').on('change click', function(event) {

        listing_niveles1();
        $('#nivel2').empty();
        $('#asignatura').empty();
        $('#credits').val('');
        $('#type').val('');
    
   });

   $('#nivel1').on('change click', function(event) {

        listing_niveles2();
        $('#asignatura').empty();
        $('#credits').val('');
        $('#type').val('');
    
   });

   $('#nivel2').on('change click', function(event) {

        listing_courses();
        $('#credits').val('');
        $('#type').val('');
    
   });

   $('#asignatura').on('change click', function(event) {

        listing_details();
    
   });

});

function listing_details()
{
    $.ajax({
        data : {
            universidad : $('#university').val(),
            area : $('#area').val(),
            degree : $('#titulo').val(),
            nivel1 : $('#nivel1').val(),
            nivel2 : $('#nivel2').val(),
            course : $('#asignatura').val(),
        },
        type : 'POST',
        url : '/listing_details'
    })
    .done(function(data) {

        $('#credits').val(data.creditos)
        $('#type').val(data.tipo)
    });
}

function listing_courses()
{
    $.ajax({
        data : {
            universidad : $('#university').val(),
            area : $('#area').val(),
            degree : $('#titulo').val(),
            nivel1 : $('#nivel1').val(),
            nivel2 : $('#nivel2').val(),
        },
        type : 'POST',
        url : '/listing_courses'
    })
    .done(function(data) {

        $('#asignatura').empty();
        for (var i=0; i<data.length; i++)
            $('#asignatura').append('<option value="' + data[i] + '">' + data[i] + '</option>');
    });
}

function listing_niveles2()
{
    $.ajax({
        data : {
            universidad : $('#university').val(),
            area : $('#area').val(),
            degree : $('#titulo').val(),
            nivel1 : $('#nivel1').val(),
        },
        type : 'POST',
        url : '/listing_niveles2'
    })
    .done(function(data) {

        $('#nivel2').empty();
        for (var i=0; i<data.length; i++)
            $('#nivel2').append('<option value="' + data[i] + '">' + data[i] + '</option>');
    });
}

function listing_niveles1()
{
    $.ajax({
        data : {
            universidad : $('#university').val(),
            area : $('#area').val(),
            degree : $('#titulo').val(),
        },
        type : 'POST',
        url : '/listing_niveles1'
    })
    .done(function(data) {

        $('#nivel1').empty();
        for (var i=0; i<data.length; i++)
            $('#nivel1').append('<option value="' + data[i] + '">' + data[i] + '</option>');
    });
}

function listing_degrees()
{
    $.ajax({
        data : {
            universidad : $('#university').val(),
            area : $('#area').val()
        },
        type : 'POST',
        url : '/listing_degrees'
    })
    .done(function(data) {

        $('#titulo').empty();
        for (var i=0; i<data.length; i++)
            $('#titulo').append('<option value="' + data[i] + '">' + data[i] + '</option>');
    });
}


function listing_areas()
{
    $.ajax({
        data : {
            universidad : $('#university').val()
        },
        type : 'POST',
        url : '/listing_areas'
    })
    .done(function(data) {

        $('#area').empty();
        for (var i=0; i<data.length; i++)
            $('#area').append('<option value="' + data[i] + '">' + data[i] + '</option>');

    });
}