from django import forms
from bravado.client import SwaggerClient
import yaml
import json
from bravado_core.spec import Spec
from core import parse_open_api


class UploadFileForm(forms.Form):
    file = forms.FileField()
    name = forms.TextInput()


    def is_valid(self):
        # run the parent validation first
        valid = super(UploadFileForm, self).is_valid()

        file = None
        try:
            file = self.files['file'].read().decode('utf-8')
        except Exception:

            self.add_error('file', "Could not load file.")
            return False

        self.spec_dict = {}
        name = self.files['file'].name

        is_json = name.split('.')[-1] == 'json'
        is_yaml = name.split('.')[-1] == 'yaml'

        if not (json or yaml):
            self.add_error(None, 'File is not in .json or .yaml format.')
            return False

        if is_yaml:
            try:
                spec_dict = yaml.safe_load(file)
                spec_dict = json.loads(json.dumps(spec_dict))
                self.spec_dict, errors = parse_open_api.extract_swagger(spec_dict)

                if errors:
                    for error in errors:
                        self.add_error(field=None, error=error)
                    return False
                else:
                    return True
            except Exception as e:
                self.add_error(None, "Could not parse specification from yaml file.")
                return False

        if is_json:
            try:
                spec_dict = json.loads(file)
                self.spec_dict, errors = parse_open_api.extract_swagger(spec_dict)

                if errors:
                    for error in errors:
                        self.add_error(field=None, error=error)
                    return False
                else:
                    return True
            except Exception as e:
                self.add_error(None, "Could not parse specification from json file.")
                return False

        return valid





