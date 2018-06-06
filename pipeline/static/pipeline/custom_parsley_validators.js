function is_expression(value){

        // if string has expression markup
        if(value.length >= 3 && value.slice(0,2) === ">>"){
            let expression_string = value.slice(2,value.length);
            target_pipe_id_regex = /\d+/i;

            // ensure it specifies a target
            if(!target_pipe_id_regex.test(expression_string)){
                return $.Deferred().reject('Output not identified. E.g. for output 10 use >>10}}.');
            }
            return true
        }

    return false

}

window.Parsley
  .addValidator('jsonlist', {
    requirementType: 'string',
    validateString: function(value) {

        // if it is valid jsonata skip validation as we don't have evaluation value yet
        let val = is_expression(value);

        if(typeof(val) === typeof(true)){
            if(val) {
                return true
            }
        }else{
            return val
        }

        try {
            let json_parse = jQuery.parseJSON(value);
            return json_parse.constructor === Array
        } catch(e) {
            return false
        }

    },
    messages: {
      en: 'Not a valid json list.',
      fr: 'Pas une liste valide.'
    }
  });

window.Parsley
  .addValidator('evaluation', {
    requirementType: 'string',
    validateString: function(value) {
        val = is_expression(value);

        {if(typeof(val) === typeof(true)){
            if(val) {
                return true
            }
        }else{
            return val
        }

        return true
    }}}
    );
