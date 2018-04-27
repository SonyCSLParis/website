function add_pipe(pipe_id, pipeline_id, request_id, create_pipe_url, input_output_url) {
    jQuery('#add-after-'+pipe_id).click(function (e) {
        //do something
        e.preventDefault();
        console.log('clicked on ' + 'add-pipe-{{pipe.id}}');
        var request_data = {'pipe_id': pipe_id,
                            'pipeline_id': pipeline_id,
                            'request_id':request_id
                            };

        $.ajax({
            method: "PUT",
            url: create_pipe_url,
            dataType: "json",
            dataContent: "json",
            data: JSON.stringify(request_data),
            success: handle_create_pipe_success,
            error: handle_create_pipe_failure
        });
    });

    function handle_create_pipe_failure(response) {
        console.log('failed to created pipe');
        console.log(response);
    }

    function handle_create_pipe_success(data) {
        console.log('created pipe');
        console.log(data);
        created_pipe = data['created_pipe'];
        pipe_origin = created_pipe['pipe_origin'];
        new_pipe_id = created_pipe['pk'];
        fields = created_pipe['fields'];
        console.log(fields);
        console.log(new_pipe_id);
        $.ajax({
            type: "GET",
            url: input_output_url + '/'+ pipeline_id +'/' +new_pipe_id,
            success: handle_fetched_new_pipe_success
        });
    }

    function handle_fetched_new_pipe_success(response) {
        console.log('fetched html');
        console.log('adding after #pipe' + pipe_origin);
        $('#pipe' + pipe_origin).after(response);
    }

    function handle_fetched_new_pipe_failure(response) {
        console.log('could not fetched html');
        console.log(response);
    }
}

function delete_pipe(pipe_id, rest_url) {

    jQuery("#delete_pipe_" + pipe_id).click(function (e) {
        e.preventDefault();
        var request_data = {};
        request_data['pipe_id'] = pipe_id;
        $.ajax({
            method: "PUT",
            url: rest_url + 'delete_pipe',
            dataType: "json",
            dataContent: "json",
            data: JSON.stringify(request_data),
            success: function (response) {
                $("#pipe" + response['deleted_pipe']).remove();
            },
            error: function (response) {
                console.log('failed to remove pipe' + response['deleted_pipe'])
            }
        });
    });
}