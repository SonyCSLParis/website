from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
from pipeline.models import Pipe
import json
import datetime

param_prefix = 'param-'
type_prefix = 'type-'


def convert_number(val):
    return float(val)


def convert_int(val):
    return int(val)


def convert_string(val):
    """nothing to do as we already have a string"""
    return str(val)


def convert_obj(val):
    parsed_json = json.loads(val)
    return parsed_json


def convert_array(val):
    parsed_json = json.loads(val)
    if type(parsed_json) != list:
        raise Exception("Provided JSON is not a valid array.")

    return parsed_json


def convert_bool(val):

    if val.lower() in ["true", "1"]:
        return 1
    elif val.lower() in ["false", "0"]:
        return 0

    raise ValueError("Value could not be parsed into a boolean.")


converter_funcs = {
    'number': convert_number,
    'boolean': convert_bool,
    'integer': convert_int,
    'string': convert_string,
    'object': convert_obj,
    'array': convert_array
}


def convert_to_format(input_dict):

    errors = {}

    local_dict = {k: v for k, v in input_dict.items()}

    param_keys = {}

    for key, val in local_dict.items():

        if param_prefix in key:
            param_keys[key] = val

    params_converter_funcs = {}
    params_converter_types = {}

    for key, val in local_dict.items():

        if type_prefix in key:
            param_string = key.replace(type_prefix, '')
            params_converter_funcs[param_string] = converter_funcs[val]
            params_converter_types[param_string] = val

    converted_params = {}

    for key in param_keys:
        param_string = key.replace(param_prefix, '')
        value = local_dict[key]
        try:
            converted_params[param_string] = params_converter_funcs[param_string](value)
        except Exception as e:
            errors[param_string] = 'parameter error: {} could not be parsed as {} for parameter {}. ' \
                                   'Error message is {}.'.format(value,
                                                                 params_converter_types[param_string],
                                                                 key,
                                                                 e)

    return converted_params, errors


def save_parameters(pipe_id, parameters, validation_errors):

    pipe_object = Pipe.objects.get(pk=pipe_id)

    # make all values empty that had errors
    for param in validation_errors:
        parameters[param] = ''

    pipe_object.parameters = parameters

    now = datetime.datetime.now()

    if validation_errors:
        pipe_object.output = format_error_output(validation_errors)
        pipe_object.output_time = now
    else:
        pipe_object.output = ""
        pipe_object.output_time = None

    pipe_object.run_time = now

    pipe_object.save()


def format_error_output(errors):
    return "\n".join(list(errors.values()))


@api_view(['PUT'])
def external_request(request):
    if request.method == 'PUT':
        request_data = json.loads(request.body)
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        json_data = request_data['data']
        r = requests.post(request_data['url'], json=json_data, headers=headers)
        return Response({"output": json.loads(r.content)})



@api_view(['PUT'])
def save_input(request):
    if request.method == 'PUT':
        request_data = json.loads(request.body)
        mapped_params, validation_errors = convert_to_format(request_data)
        save_parameters(request_data['pipe_id'], mapped_params, validation_errors)

        return Response({"message": "success"})


@api_view(['PUT'])
def save_output(request):
    if request.method == 'PUT':
        request_data = json.loads(request.body)
        pipe_id = request_data['pipe_id']
        pipe_object = Pipe.objects.get(pk=pipe_id)
        del request_data['pipe_id']
        now = datetime.datetime.now()
        pipe_object.output = json.dumps(request_data)
        pipe_object.output_time = now
        pipe_object.save()

        return Response({"message": "success"})
