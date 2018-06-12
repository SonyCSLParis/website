function getFormData($form){
    var unindexed_array = $form.serializeArray();
    var indexed_array = {};

    $.map(unindexed_array, function(n, i){
        value = $.trim(n['value']);
        indexed_array[n['name']] = value;
    });

    param_exists_for_val = function(string){
        var ret = String(string);
        ret = ret.replace('val-','');
        ret = 'param-' + ret;
        return ret in indexed_array;

    };

    $('input[type="checkbox"]:not(:checked)').each(function() {
            if(param_exists_for_val(this.name)){
                indexed_array[this.name] = 'false'
            }
        }
    );

    $('input[type=checkbox]:checked').each(function () {
                if(param_exists_for_val(this.name)) {
                    indexed_array[this.name] = 'true'
                }
            }
        );

    return indexed_array;
}


function run_form(form_id, pipe_id) {


    $("#form"+pipe_id).parsley({trigger: "change"}).on('field:validated', function() {
            var ok = $('.parsley-error').length === 0;
            $('.bs-callout-info').toggleClass('hidden', !ok);
            $('.bs-callout-warning').toggleClass('hidden', ok);
    });

    $(document).ready(function () {
            var $myForm = $('#' + form_id);
            $myForm.submit(function (event) {
                event.preventDefault();

                try {
                    $myForm.parsley().validate();
                }
                catch (e) {
                    console.log('form validation error' + e)
                }

                if ($myForm.parsley().isValid()) {
                    let formData = getFormData($(this));

                    $.ajax({
                        // using put here so we can get the body of the
                        // request. Some middleware is removing the data from post requests.
                        method: "PUT",
                        url: 'run',
                        dataType: "json",
                        dataContent: "json",
                        data: JSON.stringify(formData),
                        success: load_output,
                        error: run_error
                    });
                }
            });

            function run_error(json) {
                console.log('server side validation error');
                console.log(json.responseJSON);
                let errors = json.responseJSON['errors'];

                $('#input' + pipe_id).load('input/' + pipe_id, function(){
                    // only load form errors after refreshing input or they will be overwritten
                    Object.keys(errors).forEach(function (key) {
                                       if(key === 'general'){
                                           $('.invalid-form-error-message-'+pipe_id)
                                               .html(errors[key])
                                               .toggleClass('filled', true);
                                       } else {
                                           // join messages in order
                                           $('#' + key).parsley().addError('error-1', {message: errors[key].join("<br />")});
                                       }
                                   });
                    $('#output' + pipe_id).load('output/' + pipe_id);
                });
            }

            function load_output(response) {

                $('#input' + pipe_id).load('input/' + pipe_id);
                $('#output' + pipe_id).load('output/' + pipe_id);
            }
        }
    )
}