window.Parsley
  .addValidator('jsonlist', {
    requirementType: 'string',
    validateString: function(value) {
        try {
            var json_parse = jQuery.parseJSON(value);
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