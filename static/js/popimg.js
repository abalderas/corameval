$(document).ready(function(){
    $('[data-toggle="popover"]').popover({         
         html: true,
         fallbackPlacement : ['left', 'right', 'top', 'bottom'],
         content: function () {
               return '<img class="img-fluid" src="'+$(this).data('img') + '" />';
         }
   }) 
});