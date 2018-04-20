function apply_form_field_error(fieldname, error) {
    var input = $("#id_" + fieldname),
        container = $("#div_id_" + fieldname),
        error_msg = $("<span />").addClass("help-inline ajax-error").text(error[0]);

    container.addClass("error");
    error_msg.insertAfter(input);
}

function clear_form_field_errors(form) {
    $(".ajax-error", $(form)).remove();
    $(".error", $(form)).removeClass("error");
}

$(document).on("submit", "#pony_form", function(e) {
    e.preventDefault();
    var self = $(this),
        url = self.attr("action"),
        ajax_req = $.ajax({
            url: url,
            type: "POST",
            data: {
                name: self.find("#id_name").val()
            },
            success: function(data, textStatus, jqXHR) {
                django_message("Pony saved successfully.", "success");
            },
            error: functior(data, textStatus, jqXHR) {
                var errors = $.parseJSON(data.responseText);
                $.each(errors, function(index, value) {
                    if (index === "__all__") {
                        django_message(value[0], "error");
                    } else {
                        apply_form_field_error(index, value);
                    }
                });
            }
        });
});