function getFormData($form){
    var unindexed_array = $form.serializeArray();
    var indexed_array = {};

    $.map(unindexed_array, function(n, i){
        indexed_array[n['name']] = n['value'];
    });

    return indexed_array;
}

function run_form(form_id, pipe_id, rest_url, request_url, input_url, output_url) {
    $(document).ready(function () {
        var $myForm = $('#'+form_id);
        $myForm.submit(function (event) {
            event.preventDefault();
            var $formData = getFormData($(this));
            console.log('input pipe id ' + pipe_id);
            console.log(JSON.stringify($formData));
            $.ajax({
                    // using put here so we can get the body of the
                    // request. Some middleware
                    method: "PUT",
                    url: rest_url+'save_input',
                    dataType: "json",
                    dataContent:"json",
                    data:JSON.stringify($formData),
                    success: make_request,
                    error: function(response){
                        console.log('could not save input');
                        console.log(response);
                    }
                });
        });

        function make_request(data) {

            console.log('saved input');
            data['request_url'] = request_url;
            console.log('making request to ' + request_url);
            $('#input'+pipe_id).load(input_url + '/' + pipe_id);

            $.ajax({
                    // using put here so we can get the body of the
                    // request. Some middleware
                    method: "PUT",
                    url: rest_url,
                    dataType: "json",
                    dataContent:"json",
                    data:JSON.stringify(data),
                    success: handleRequestSuccess,
                    error: handleRequestFailure
                    });


            function handleRequestSuccess(response){

                console.log('request success');
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

                function handle_output_save_success(data){
                    console.log('saved output')
                    $('#output'+pipe_id).load(output_url + '/' + pipe_id);
                    console.log('updated html')
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
    })
}