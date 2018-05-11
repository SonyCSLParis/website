from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
from django.core import serializers
from browser.models import Request, ComponentSpecification, Parameter
from pipeline.models import Pipe, Pipeline
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
    pipe_object.input_time = now

    if validation_errors:
        pipe_object.output = format_error_output(validation_errors)
        pipe_object.output_time = now
    else:
        pipe_object.output = ""
        pipe_object.output_time = None

    pipe_object.run_time = now

    pipe_object.save(force_update=True)


def format_error_output(errors):
    return "\n".join(list(errors.values()))


@api_view(['PUT'])
def external_request(request):
    if request.method == 'PUT':
        request_data = json.loads(request.body)
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        r = requests.post(request_data['request_url'], json=request_data, headers=headers)
        return Response({"output": json.loads(r.content)})


@api_view(['PUT'])
def save_input(request):
    if request.method == 'PUT':
        request_data = json.loads(request.body)
        mapped_params, validation_errors = convert_to_format(request_data)
        save_parameters(request_data['pipe_id'], mapped_params, validation_errors)

        return Response({"data_saved": mapped_params})


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
        pipe_object.save(force_update=True)

        return Response({"data_saved": request_data})


@api_view(['PUT'])
def create_pipe(request):
    if request.method == 'PUT':
        request_data = json.loads(request.body)
        pipe_id = request_data['pipe_id']  # use this to decide after which pipe to create new pipe
        request_id = request_data['request_id']
        pipeline_id = request_data['pipeline_id']

        pipeline = Pipeline.objects.get(pk=pipeline_id)
        pipeline.local_id_gen += 1
        pipeline.save()

        if pipe_id != 'empty':
            pipe = Pipe.objects.get(pk=pipe_id)
            pipe_position = pipe.position
            next_postition = pipe_position + 1  # this is the position the new pipe will occupy

            # get all pipes at this position and beyond and increment them by 1
            pipes = Pipe.objects.filter(position__gte=next_postition)

            for pipe in pipes:
                pipe.position += 1
                pipe.save()
        else:
            next_postition = 0  # start from 0

        request = Request.objects.get(pk=request_id)
        parameters = request.parameters.all()

        # duplicate parameter from the request specification for the pipe.
        for parameter in parameters:
            parameter.pk = None  # clearing pk and saving will clone the object
            parameter.save()

        new_pipe = Pipe.objects.create(pipe_line=pipeline,
                                       request=request,
                                       output='',
                                       local_id=pipeline.local_id_gen,
                                       position=next_postition)

        for parameter in parameters:
            new_pipe.parameters.add(parameter)

        new_pipe.save()
        json_new_pipe = json.loads(serializers.serialize('json', [new_pipe]))
        json_new_pipe = json_new_pipe[0]
        json_new_pipe['pipe_origin'] = pipe_id
        return Response({"created_pipe": json_new_pipe})


@api_view(['PUT'])
def delete_pipe(request):
    if request.method == 'PUT':
        request_data = json.loads(request.body)
        pipe_id = request_data['pipe_id']  # use this to decide after which pipe to create new pipe
        pipe = Pipe.objects.get(pk=pipe_id)
        pipe.delete()
        return Response({"deleted_pipe": pipe_id})


@api_view(['PUT'])
def move_up_pipe(request):
    if request.method == 'PUT':
        request_data = json.loads(request.body)
        pipe_id = request_data['pipe_id']  # use this to decide after which pipe to create new pipe
        pipeline_id = request_data['pipeline_id']  # use this to decide after which pipe to create new pipe
        current_pipe = Pipe.objects.get(pk=pipe_id)
        current_position = current_pipe.position
        try:
            pipe_after_current = Pipe.objects.filter(pipe_line=pipeline_id) \
                .get(position=current_position - 1)
            current_pipe.position = pipe_after_current.position
            pipe_after_current.position = current_position
            current_pipe.save()
            pipe_after_current.save()

            return Response({"pipe_origin_id": pipe_id,
                             "pipe_swap_id": pipe_after_current.id})
        except :

            return Response({"message": "couldn't process request"})


@api_view(['PUT'])
def move_down_pipe(request):
    if request.method == 'PUT':
        request_data = json.loads(request.body)
        pipe_id = request_data['pipe_id']  # use this to decide after which pipe to create new pipe
        pipeline_id = request_data['pipeline_id']  # use this to decide after which pipe to create new pipe
        current_pipe = Pipe.objects.get(pk=pipe_id)
        current_position = current_pipe.position
        try:
            pipe_before_current = Pipe.objects.filter(pipe_line=pipeline_id)\
                                              .get(position=current_position + 1)
            current_pipe.position = pipe_before_current.position
            pipe_before_current.position = current_position
            current_pipe.save()
            pipe_before_current.save()

            return Response({"pipe_origin_id": pipe_id,
                             "pipe_swap_id": pipe_before_current.id})
        except:

            return Response({"message": "couldn't process request"})


@api_view(['PUT'])
def save_component(request):
    if request.method == 'PUT':
        component_spec = json.loads(request.body)

        requests = component_spec['requests']
        del component_spec['requests']

        component = ComponentSpecification.objects.create(**component_spec)
        component.save()

        for request in requests:

            request_params = request['parameters']
            del request['parameters']

            request['component'] = component
            request_inst = Request.objects.create(**request)
            request_inst.component = component
            request_inst.save()

            def add_params(request_params, parent_param=None):

                for parameter in request_params:

                    if 'nested' in parameter:
                        nested_params = parameter['nested']
                        del parameter['nested']
                    else:
                        nested_params = None

                    param_instance = Parameter.objects.create(**parameter)
                    request_inst.parameters.add(param_instance)

                    if parent_param:
                        parent_param.nested.add(param_instance)

                    if nested_params:
                        add_params(nested_params, param_instance)

            add_params(request_params)

        return Response({"message": "success"})

