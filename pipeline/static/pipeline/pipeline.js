function add_pipe(pipe_id, request_id) {

    $('#add-after-'+pipe_id+'-'+request_id).click(function (e) {
        console.log('jquery called');
        //do something
        e.preventDefault();

        console.log('clicked on ' + 'add-pipe-{{pipe.id}}');
        var request_data = {'pipe_id': pipe_id,
                            'request_id':request_id
                            };

        $.ajax({
            method: "PUT",
            url: 'create_pipe',
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
            url: 'input_output/' + new_pipe_id,
            success: handle_fetched_new_pipe_success
        });
    }

    function handle_fetched_new_pipe_success(response) {
        console.log('fetched html');
        console.log('adding after #pipe-' + pipe_origin);
        $('#pipe-' + pipe_origin).after(response);
        if(pipe_origin === 'empty') {
            $("#pipe-empty").remove();
        }
    }

    function handle_fetched_new_pipe_failure(response) {
        console.log('could not fetched html');
        console.log(response);
    }
}

function delete_pipe(pipe_id) {

    $("#delete_pipe_" + pipe_id).click(function (e) {
        e.preventDefault();
        var request_data = {};
        request_data['pipe_id'] = pipe_id;
        $.ajax({
            method: "PUT",
            url: 'delete_pipe',
            dataType: "json",
            dataContent: "json",
            data: JSON.stringify(request_data),
            success: function (response) {
                $("#pipe-" + response['deleted_pipe']).remove();
                // check whther deletion of this would result in no more pipes
                if (!$(".pipe")[0]){
                    $.ajax({
                        type: "GET",
                        url: 'empty_pipe',
                        success: function(response){
                            console.log('adding empty pipe options');
                            $('#pipeline-details').after(response);}
                    });
                }
            },
            error: function (response) {
                console.log('failed to remove pipe' + response['deleted_pipe'])
            }
        });
    });
}


function move_up_pipe(pipe_id) {

    $("#move_up_pipe_" + pipe_id).click(function (e) {
        e.preventDefault();
        var request_data = {};
        request_data['pipe_id'] = pipe_id;
        console.log('moving up pipe ' + pipe_id);
        console.log(request_data);
        $.ajax({
            method: "PUT",
            url: 'move_up_pipe',
            dataType: "json",
            dataContent: "json",
            data: JSON.stringify(request_data),
            success: function (response) {
                console.log('moved up pipe');
                console.log(response);
                pipe_origin_id = response['pipe_origin_id'];
                pipe_swap_id = response['pipe_swap_id'];
                console.log("#pipe-" +pipe_origin_id)
                console.log("#pipe-"+pipe_swap_id)

                $("#pipe-" +pipe_origin_id).after($("#pipe-"+pipe_swap_id));
               // $("#pipe" + response['deleted_pipe']).remove();$("#element1").before($("#element2"));
            },
            error: function (response) {
                console.log('failed to remove pipe' + response['deleted_pipe'])
            }
        });
    });
}


function move_down_pipe(pipe_id) {

    $("#move_down_pipe_" + pipe_id).click(function (e) {
        e.preventDefault();
        var request_data = {};
        request_data['pipe_id'] = pipe_id;
        console.log('moving up pipe ' + pipe_id);
        console.log(request_data);
        $.ajax({
            method: "PUT",
            url: 'move_down_pipe',
            dataType: "json",
            dataContent: "json",
            data: JSON.stringify(request_data),
            success: function (response) {
                console.log('moved down pipe');
                console.log(response);
                pipe_origin_id = response['pipe_origin_id'];
                pipe_swap_id = response['pipe_swap_id'];
                console.log("#pipe-" +pipe_origin_id)
                console.log("#pipe-"+pipe_swap_id)

                $("#pipe-" +pipe_swap_id).after($("#pipe-"+pipe_origin_id));
            },
            error: function (response) {
                console.log('failed to remove pipe' + response['deleted_pipe'])
            }
        });
    });
}

function decodeHtml(html) {
    let txt = document.createElement("textarea");
    txt.innerHTML = html;
    return txt.value;
}

function toggle_expression(id, expression, value) {
    let param_input = document.getElementById('val-'+id);
    let button = $('#expression-'+id);

    if (button.attr("aria-pressed") === "false") {
        param_input.value = decodeHtml(expression);
        button.attr("aria-pressed", "true");
        button.addClass('active');
    } else{
        param_input.value = decodeHtml(value);
        button.attr("aria-pressed", "false");
        button.removeClass('active');
    }
}
