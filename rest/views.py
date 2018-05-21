from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
from django.core import serializers
from browser.models import PathRequest, ComponentSpecification, Parameter, PathResponse
from pipeline.models import Pipe, Pipeline
import json
import datetime
from django.db import transaction
from core.pipeline import populate_pipes_params, get_request_params

param_prefix = 'param-'
val_prefix = 'val-'


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

    try:
        parsed_json = json.loads(val)
    except Exception as e:
        raise Exception('Could not parse json array from {}'.format(val))

    if type(parsed_json) != list:
        raise Exception("Provided JSON is not a valid array.")

    return parsed_json


def convert_bool(val):

    if val.lower() in ["true", "1", 'on']:
        return 1
    elif val.lower() in ["false", "0", 'off']:
        return 0

    raise ValueError("Value could not be parsed into a boolean.")


json_converter_funcs = {
    'number': convert_number,
    'boolean': convert_bool,
    'integer': convert_int,
    'string': convert_string,
    'object': convert_obj,
    'array': convert_array
}

from collections import namedtuple

NamedParam = namedtuple('NamedParam', ['name', 'id', 'type', 'value', 'converter'])


def convert_to_format(input_dict):

    errors = {}
    params = []

    local_dict = {k: v for k, v in input_dict.items()}

    for prefix_name, param_info in local_dict.items():
        if param_prefix in prefix_name:
            name, id, type = param_info.split()
            value = local_dict.get(val_prefix+name)
            params.append(NamedParam(name, id, type, value, json_converter_funcs[type]))

    # now check if parameters are valid json
    for param in params:
        value = param.value
        converter = param.converter
        try:
            converted_value = converter(value)

        except Exception as e:
            errors[param.name] = 'Parameter error: {} could not be parsed as {} for parameter {}.'\
                                  .format(value, converter, param.name)
            break

    # remove errors that are due to required parameters
    for param in params:
        param_obj = Parameter.objects.get(pk=param.id)
        is_required = convert_bool(param_obj.required)

        if is_required and param.value == '':
            errors[param.name] = 'Param {} is required but is empty'.format(param.name)
        elif param.value == '':
            # suppress any errors as val was not required so it being empty doesn't matter
            # this shouldn't be neccesary if converters don't create an error from an empty string
            if param.name in errors:
                del errors[param.name]

    return params, errors


def save_parameters(pipe_id, parameters, validation_errors):

    pipe_object = Pipe.objects.get(pk=pipe_id)

    for param in parameters:
        param_obj = Parameter.objects.get(pk=param.id)
        param_obj.value = param.value
        param_obj.save()

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
        data = json.loads(request.body)

        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        # we require all external requests use https
        r = requests.post('https://'+data['request_url'], json=data['request_data'], headers=headers)

        if r.status_code == 200:
            return Response({"output": json.loads(r.content)})
        else:
            return Response({"output": r.status_code})



@api_view(['PUT'])
def save_input(request):
    if request.method == 'PUT':
        request_data = json.loads(request.body)
        source_params, validation_errors = convert_to_format(request_data)

        # we save the input the user put in as is
        save_parameters(request_data['pipe_id'], source_params, validation_errors)

        if not validation_errors:
            pipe = Pipe.objects.get(pk=request_data['pipe_id'])
            request_data = get_request_params(pipe)

        return Response({"request_data": request_data,
                         "errors": validation_errors})


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

        request = PathRequest.objects.get(pk=request_id)
        parameters = request.parameters.filter(sub_param=None)
        # duplicate parameter from the request specification for the pipe.
        def duplicate_parameters(internal_parameters):
            for parameter in internal_parameters:

                nested = parameter.nested.all()
                if nested:
                    duplicate_parameters(nested)

                # clearing pk and saving will clone the object
                parameter.pk = None
                parameter.save()

                # give nested params
                if nested:
                    for nested_param in nested:
                        parameter.nested.add(nested_param)


        duplicate_parameters(parameters)

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
@transaction.atomic
def save_component(request):
    if request.method == 'PUT':
        component_spec = json.loads(request.body)
        requests = component_spec['requests']
        del component_spec['requests']

        component = ComponentSpecification.objects.create(**component_spec)
        component.save()

        for request in requests:

            request_params = request['parameters']
            request_responses = request['responses']
            del request['parameters']
            del request['responses']

            request['component'] = component

            request_inst = PathRequest.objects.create(**request)
            request_inst.component = component
            request_inst.save()

            def json_dump_val(param_dict):
                return {key: json.dumps(val) for key, val in param_dict.items()}

            def add_params(request_params, inst, parent_param=None):

                for parameter in request_params:

                    nested_params = None

                    if 'properties' in parameter or 'items' in parameter:

                        field_name = 'properties' if 'properties' in parameter else 'items'
                        nested_params = parameter[field_name]
                        del parameter[field_name]

                    if 'in' in parameter:
                        parameter['location'] = parameter['in']
                        del parameter['in']

                    # we want to represent all values as json strings so we can deserialise them as objects later
                    json_val_param = json_dump_val(parameter)
                    param_instance = Parameter.objects.create(**json_val_param)
                    inst.parameters.add(param_instance)

                    if parent_param:
                        parent_param.nested.add(param_instance)

                    if nested_params:
                        add_params(nested_params, inst, param_instance)

            def add_responses(responses, request_inst):

                for response in responses:

                    response_inst = PathResponse()
                    response_inst.request = request_inst
                    response_inst.status_code = response['status_code']
                    response_inst.save()
                    request_inst.responses.add(response_inst)

                    if 'description' in response:
                        response_inst.description = response['description']

                    if 'schema' in response:
                        print('schema', response['schema'])
                        add_params(response['schema'], response_inst)

                    response_inst.save()

            add_params(request_params, request_inst) # add params to request
            add_responses(request_responses, request_inst) # add responses to request

        return Response({"message": "success"})

