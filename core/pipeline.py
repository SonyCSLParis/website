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

    if val.lower() in ["true", "1", 'on']:
        return True
    elif val.lower() in ["false", "0", 'off']:
        return False

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


def extract_fields(dictionary):

        parameters = {}

        for k, v in dictionary.items():
            k = k if k != 'enum' else 'options'

            # need to strip values that are strings
            if isinstance(v, str):
                v = v.strip("\"")

            if k not in ['_state'] and v is not None:

                # we are only converting enums to python data types
                if k not in ['options']:
                    parameters[k] = v
                    continue

                try:
                    json_str = '{{"key": {}}}'.format(v)
                    parse = json.loads(json_str)
                    parameters[k] = parse['key']
                except Exception as e:
                    parameters[k] = v
        return parameters


def extract_parameters(objects, is_nested=False):

    internal_parameters = []

    for obj in objects:

        nested_params = obj.nested.all()
        if nested_params:
            nested_params = extract_parameters(nested_params, True)

        param_dict = obj.__dict__
        if nested_params:
            param_dict['nested'] = nested_params

        internal_parameters.append(extract_fields(param_dict))

    return internal_parameters


def populate_pipes_params(sorted_pipe_objs):

    pipes = []

    for pipe in sorted_pipe_objs:
        pipes.append(populate_pipe_params(pipe))
    return pipes


def populate_pipe_params(pipe):

    parent_parameters = pipe.parameters.filter(sub_param=None)
    param_dict = extract_parameters(parent_parameters)
    request_dict = extract_fields(pipe.request.__dict__)
    request_dict['component'] = pipe.request.component.__dict__
    pipe_dict = extract_fields(pipe.__dict__)
    pipe_dict['parameters'] = param_dict
    pipe_dict['request'] = request_dict

    return pipe_dict


def get_request_params(pipe):

    parent_parameters = pipe.parameters.filter(sub_param=None)
    params = extract_parameters(parent_parameters)

    def param_list_to_dict(param_list):

        param_dict = {}

        for param in param_list:

            nested_list = None

            if 'nested' in param:
                nested_list = param_list_to_dict(param['nested'])

            name = param['name']

            if nested_list:
                param_dict[name] = nested_list
            else:
                if 'value' in param:
                    value = param['value']
                    converter = converter_funcs[param['type']]
                    converted_value = converter(value)
                    param_dict[name] = converted_value

        return param_dict

    request_param_dict = param_list_to_dict(params)

    return request_param_dict