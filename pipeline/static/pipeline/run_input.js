function getFormData($form){
    var unindexed_array = $form.serializeArray();
    var indexed_array = {};

    $.map(unindexed_array, function(n, i){
        indexed_array[n['name']] = n['value'];
    });

    return indexed_array;
}

function run_form(form_id, pipe_id, rest_url, request_data) {
    $(document).ready(function () {
        var $myForm = $(form_id);
        $myForm.submit(function (event) {
            event.preventDefault();
            var $formData = getFormData($(this));
            console.log('form submit');
            console.log(JSON.stringify(request_data));
            // $.ajax({
            //     method: "POST",
            //     url: $thisURL,
            //     data: $formData,
            //     success: handleFormSuccess,
            //     error: handleFormError
            // })
            $.ajax({
                    // using put here so we can get the body of the
                    // request. Some middleware
                    method: "PUT",
                    url: rest_url+'save_input',
                    dataType: "json",
                    dataContent:"json",
                    data:JSON.stringify($formData),
                    success: handle_save_input_success,
                    error: handle_save_input_failure
                });
        });

        function handle_save_input_success(data, textStatus, jqXHR) {

            console.log('saved input');
            request_type = request_data['type'];
            console.log(rest_url);
            delete request_data['type'];
            console.log(request_data);
            $.ajax({
                    // using put here so we can get the body of the
                    // request. Some middleware
                    method: "PUT",
                    url: rest_url,
                    dataType: "json",
                    dataContent:"json",
                    data:JSON.stringify(request_data),
                    success: handleRequestSuccess,
                    error: handleRequestFailure
                    });


            function handleRequestSuccess(response){

                console.log('request success');
                console.log(response);
                response['pipe_id'] = pipe_id;
                $.ajax({
                      // using put here so we can get the body of the
                      // request. Some middleware
                      method: "PUT",
                      url: rest_url+'save_output',
                      dataType: "json",
                      dataContent:"json",
                      data:JSON.stringify(response),
                      success: handle_output_save_success,
                      error: handle_output_save_failure
                });

                function handle_output_save_success(response){
                    console.log('output saved');
                    console.log(response);

                    $(pipe_id).load('output/' + pipe_id);
                }


                function handle_output_save_failure(response){
                    console.log('request failure');
                }

            }

            function handleRequestFailure(response){
                console.log('request failure');
                console.log(response);
           }
        }

        function handle_save_input_failure(jqXHR, textStatus, errorThrown) {

            console.log('form failure');
            console.log(jqXHR);
            console.log(textStatus);
            console.log(errorThrown);
        }
    })
}