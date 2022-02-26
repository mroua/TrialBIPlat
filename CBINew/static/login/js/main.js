
(function ($) {
    "use strict";


    /*==================================================================
    [ Focus Contact2 ]*/
    $('.input100').each(function(){
        $(this).on('blur', function(){
            if($(this).val().trim() != "") {
                $(this).addClass('has-val');
            }
            else {
                $(this).removeClass('has-val');
            }
        })    
    });
  
  
    /*==================================================================
    [ Validate ]*/
    var input = $('.validate-input .input100');

    $('.validate-form').on('submit',function(e){
        var check = true;

        for(var i=0; i<input.length; i++) {
            if(validate(input[i]) == false){
                showValidate(input[i]);
                check=false;
            }

        }
        if(check != false){
            $loadingpage.css('display', 'block');
            try{
                $.ajax({
                    type:'POST',
                    url :'connexion',
                    data : {
                        identifiant:input[0].value,
                        password: input[1].value,
                        csrfmiddlewaretoken:$('input[name= csrfmiddlewaretoken]').val()
                    },
                    success : function(resultat){
                        if(resultat === "Error"){
                            $loadingpage.css('display', 'none');
                            $('.MessageErreur').html('');
                            $('.MessageErreur').append('<div class="alert alert-danger alert-dismissible fade show" role="alert">'+
                                                '<strong>Vos identifiants sont incorrectes!</strong>'+
                                                '<button type="button" class="close" data-dismiss="alert" aria-label="Close">'+
                                                '<span aria-hidden="true">&times;</span>'+
                                                '</button>'+
                                                '</div>')
                        }
                        else {
                            if (lienpage === '') {
                                window.location.href = window.document.location.origin + '/cbi';
                            } else {
                                if (isNumber(lienpage)) {
                                    window.location.href = window.document.location.origin + "/cbi/rapport/" + parseInt(lienpage);
                                } else {
                                    window.location.href = window.document.location.origin + "/cbi/page/" + lienpage;
                                }
                            }
                        }
                    }
                });
            }
            catch (e) {
                $loadingpage.css('display', 'none');
                $('.MessageErreur').html('');
                $('.MessageErreur').append('<div class="alert alert-danger alert-dismissible fade show" role="alert">'+
                    '<strong>Vos identifiants sont incorrectes!</strong>'+
                    '<button type="button" class="close" data-dismiss="alert" aria-label="Close">'+
                    '<span aria-hidden="true">&times;</span>'+
                    '</button>'+
                    '</div>')

            }
            e.preventDefault();

        }
        else return check;


    });


    $('.validate-form .input100').each(function(){
        $(this).focus(function(){
           hideValidate(this);
        });

    });

    function validate (input) {

            if($(input).val().trim() == ''){
                return false;
            }

    }

    function showValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).addClass('alert-validate');
    }

    function hideValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).removeClass('alert-validate');
    }
    

})(jQuery);