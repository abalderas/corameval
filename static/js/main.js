$(document).ready(function() {

    var modified;

    $(function () {
        $('[data-toggle="popover"]').popover()

        $(document).on('click', function(){
            $('[data-toggle="popover"]').popover('hide');
        });
      
        $('[data-toggle="popover"]').click(function(){
            $('[data-toggle="popover"]').not(this).popover('hide');
            return false;
        });
    });

    $("input, select").change(function () {   
		modified = true;  
	});

    $('#university').on('change', function(event) {
 
        listing_areas();
        $('#titulo').empty();
        $('#nivel1').empty();
        $('#nivel2').empty();
        $('#asignatura').empty();
        $('#modalidad').val('');
        $('#credits').val('');
        $('#type').val('');

    });

   $('#area').on('change click', function(event) {

        listing_degrees();
        $('#nivel1').empty();
        $('#nivel2').empty();
        $('#asignatura').empty();
        $('#modalidad').val('');
        $('#credits').val('');
        $('#type').val('');
    
   });

   $('#titulo').on('change click', function(event) {

        listing_niveles1();
        $('#nivel2').empty();
        $('#asignatura').empty();
        $('#modalidad').val('');
        $('#credits').val('');
        $('#type').val('');
    
   });

   $('#nivel1').on('change click', function(event) {

        listing_niveles2();
        $('#asignatura').empty();
        $('#modalidad').val('');
        $('#credits').val('');
        $('#type').val('');
    
   });

   $('#nivel2').on('change click', function(event) {

        listing_courses();
        $('#modalidad').val('');
        $('#credits').val('');
        $('#type').val('');
    
   });

   $('#asignatura').on('change click', function(event) {

        listing_details();
    
   });


    $('#universityCompara').on('change', function(event) {        
        listing_areas("comparar");
        $('#tituloCompara').empty();
        $('#tituloCompara').append('<option value="0">(en blanco)</option>');

    });

    $('#areaCompara').on('change click', function(event) {

        listing_degrees("comparar");

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
        $('#modalidad').val(data.modalidad);
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
        $('#asignatura').append('<option value="">(selecciona asignatura)</option>');
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
        $('#nivel2').append('<option value="">(selecciona materia)</option>');
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
        $('#nivel1').append('<option value="">(selecciona módulo)</option>');
        for (var i=0; i<data.length; i++)
            $('#nivel1').append('<option value="' + data[i] + '">' + data[i] + '</option>');
    });
}

function listing_degrees(element = "no comparar")
{
    if (element != "comparar")
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
            $('#titulo').append('<option value="0">(selecciona curso)</option>');
            for (var i=0; i<data.length; i++)
                $('#titulo').append('<option value="' + data[i] + '">' + data[i] + '</option>');
        });
    }
    else
    {
        $.ajax({
            data : {
                universidad : $('#universityCompara').val(),
                area : $('#areaCompara').val()
            },
            type : 'POST',
            url : '/listing_degrees'
        })
        .done(function(data) {

            $('#tituloCompara').empty();
            $('#tituloCompara').append('<option value="0">(selecciona curso)</option>');
            for (var i=0; i<data.length; i++)
                $('#tituloCompara').append('<option value="' + data[i] + '">' + data[i] + '</option>');
        });
    }
}


function listing_areas(element = "no comparar")
{
    if (element != "comparar")
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
            $('#area').append('<option value="0">(selecciona área)</option>');
            for (var i=0; i<data.length; i++)
                $('#area').append('<option value="' + data[i] + '">' + data[i] + '</option>');

        });
    }
    else
    {
        $.ajax({
            data : {
                universidad : $('#universityCompara').val()
            },
            type : 'POST',
            url : '/listing_areas'
        })
        .done(function(data) {

            $('#areaCompara').empty();
            $('#areaCompara').append('<option value="0">(selecciona área)</option>');
            for (var i=0; i<data.length; i++)
                $('#areaCompara').append('<option value="' + data[i] + '">' + data[i] + '</option>');

        });
    }
}