import os
from bravado_core.spec import Spec
import json
import requests

from collections import namedtuple
import yaml
# TODO these fields should mimic those in the DJANGO models. There is an issue with importing the model
# fields via Model._meta.fields as Django isn't yet loaded when running this script in isolation otherwise
# I would recommend using these fields to define the named tuples.

request_fields = ['path', 'name', 'type', 'parameters', 'description']
component_fields = ['title', 'host', 'base_path', 'description', 'summary',
                                     'version', 'openapi_version', 'requests']
parameter_fields = ['type', 'name', 'default', 'example', 'description',
                    'enum', 'required', 'properties', 'items', 'in', 'maximum', 'minimum']


def parse_spec_from_dict(swagger_dict):

    swagger_spec = Spec.from_dict(swagger_dict,
                                  config={'validate_requests': False,
                                          'use_models': False,
                                          'default_type_to_object': True,
                                          'internally_dereference_refs': True
                                          }
                                  )

    return swagger_spec.deref_flattened_spec


def load_spec(path):
    with open(path, 'r') as f:
        data = f.read()
        swagger_json = json.loads(data)

    swagger_spec = Spec.from_dict(swagger_json,
                                  config={'validate_requests': False,
                                          'use_models': False,
                                          'default_type_to_object': True,
                                          'internally_dereference_refs': True
                                          }
                                  )

    return swagger_spec.deref_flattened_spec


def get_def(inner_schema, swagger_spec):

    definition = inner_schema['$ref']
    definition_last = definition.split('/')[-1]
    return swagger_spec['definitions'][definition_last]


def get_if_present_else_none(keys, dict):
    return {key: dict[key] for key in keys if key in dict}


def extract_schema_get(parameters):
    extracted_parameters = []

    for parameter_features in parameters:

        extracted_param_features = get_if_present_else_none(parameter_fields, parameter_features)
        extracted_parameters.append(extracted_param_features)

    return extracted_parameters


def extract_schema(request_params):

    def extract(outer):

        if 'schema' in outer:
            inner = outer['schema']
            del outer['schema']
            outer.update(extract(inner))
            return get_if_present_else_none(parameter_fields, outer)

        if 'items' in outer and type(outer['items']) is dict:
            outer['items'] = [extract(outer['items'])]

        if 'properties' in outer and type(outer['properties']) is dict:
            outer['type'] = 'object'
            inner = outer['properties']
            outer_required = outer.get('required', [])
            outer_example = outer.get('example', [])

            if outer_required:
                del outer['required']

            if outer_example:
                del outer['example']

            # It is possible params were specified higher up in the
            # hierarchy. use these values if none present at this level
            # but prioritise this level

            required_field = 'required'
            example_field = 'example'

            # set required and example on sub parameters
            # if is leaf values were already set from level above

            for param_name, param_values in inner.items():

                value_is_obj = 'properties' in param_values

                if value_is_obj:
                    inner_object = extract(param_values)
                    param_values.clear()
                    param_values.update(inner_object)
                    continue

                if 'required' not in param_values:
                    if param_name in outer_required:
                        param_values[required_field] = True
                    else:
                        param_values[required_field] = False

                if 'example' not in param_values:
                    if param_name in outer_example and 'example' not in param_values:
                        param_values[example_field] = outer_example[param_name]

                param_values['name'] = param_name
            outer['properties'] = [extract(val) for key, val in inner.items()]

        return get_if_present_else_none(parameter_fields, outer)

    return [extract(param_dict) for param_dict in request_params]


def strict_is_true(bool_val, is_strict):

    # any value is fine
    if is_strict is False:
        return True

    # must be true if strict is true
    if bool_val and is_strict is True:
        return True

    return False


error_messages = {
    'produces_and_consumes_json': '{path} tagged with penelope but it does not consume and produce json. Add consumes '
                                  'and produces application/json to your specification. Penelope relies on json as a '
                                  'standard data exchange format.'
}


def extract_requests(swagger_spec, errors, strict=False):

    requests = []

    for path in swagger_spec['paths']:
        path_requests = swagger_spec['paths'][path]
        for request_type in path_requests:
            request_info = path_requests[request_type]
            consumes_and_produces_json = 'application/json' in request_info.get('consumes', []) and \
                                         'application/json' in request_info.get('produces', [])

            tagged_for_penelope = 'penelope' in request_info['tags']

            if not strict_is_true(consumes_and_produces_json, strict):
                errors.append(error_messages['produces_and_consumes_json'].format(path))
                continue

            if tagged_for_penelope and strict_is_true(consumes_and_produces_json, strict):

                summary = request_info.get('summary', None)
                description = request_info.get('description', None)
                responses = request_info.get('responses', None)
                # this is whether arguments need to be sent or not
                name = path.split('/')[-1]

                parsed_responses = []

                for status, info in responses.items():
                    response_description = info.get('description', '')
                    if 'schema' in info:
                        schema = extract_schema([info])
                        parsed_responses.append({'status_code': status,
                                                 'description': response_description,
                                                 'schema': schema})
                    else:
                        parsed_responses.append({'status_code': status,
                                                 'description': response_description})

                if request_type == 'get':
                    if 'parameters' in request_info:
                        parameters = request_info['parameters']
                        extracted_parameters = extract_schema_get(parameters)
                        requests.append({'path': path,
                                         'name': name,
                                         'type': request_type.upper(),
                                         'parameters': extracted_parameters,
                                         'description': description,
                                         'summary': summary,
                                         'responses': parsed_responses})

                # possible to have get request without params
                if request_type == 'post':
                    if 'parameters' in request_info:
                        parameters = request_info['parameters']
                        extracted_parameters = extract_schema(parameters)
                        requests.append({'path': path,
                                         'name': name,
                                         'type': request_type.upper(),
                                         'parameters': extracted_parameters,
                                         'description': description,
                                         'responses': parsed_responses,
                                         'summary': summary})

    return requests


def extract_swagger(swagger_spec, strict=False):

    errors = []

    if 'schemes' in swagger_spec:
        schemes = swagger_spec['schemes']
        if len(schemes) != 1 or 'https' not in schemes:
            print('Penelope only accepts https scheme and no other schemes')

    info = swagger_spec['info']

    spec_props = {'description': info['description'],
                  'openapi_version': swagger_spec['swagger'],
                  'version': info['version'],
                  'title': info['title'],
                  'host': swagger_spec['host'],
                  'base_path': swagger_spec['basePath']}

    swagger_spec = parse_spec_from_dict(swagger_spec)

    component_dict = get_if_present_else_none(component_fields, spec_props)
    component_dict['requests'] = extract_requests(swagger_spec, errors, strict=strict)

    return component_dict, errors
