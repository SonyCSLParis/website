from django import forms
from bravado.client import SwaggerClient
import yaml
import json
from bravado_core.spec import Spec


class UploadFileForm(forms.Form):
    file = forms.FileField()
    name = forms.TextInput()

    def is_valid(self):
        # run the parent validation first
        valid = super(UploadFileForm, self).is_valid()

        if not valid:
            return False

        try:
            file = self.files['file'].read().decode('utf-8')
            file_is_json_or_yaml = False

            # TODO for some reason Spec.from_dict doesn't work for yaml's dict parse.
            # For this reason I'm re-encoding the dict as json and loading it again as a json dict.
            try:
                spec_dict = yaml.load(file)
                spec_dict = json.dumps(spec_dict)
                spec_dict = json.loads(spec_dict)
                file_is_json_or_yaml = True
            except Exception as e:
                self.add_error(field=None, error='Invalid yaml.')
                return False

            if not file_is_json_or_yaml:
                try:
                    spec_dict = json.loads(file)
                    file_is_json_or_yaml = True
                except Exception as e:
                    self.add_error(field=None, error='Invalid json.')
                    return False

            swagger_spec = Spec.from_dict(spec_dict,
                                          config={'validate_requests': False,
                                                  'use_models': False
                                                 }
                                          )
            self.swagger_spec = swagger_spec.spec_dict
        except Exception as e:
            self.add_error(field=None, error='Invalid OpenAPI format with error {}'.format(e))
            return False

        return valid & True





