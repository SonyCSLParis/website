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
parameter_fields = ['type', 'name', 'default', 'example', 'description', 'enum', 'required', 'nested']


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


def extract_schema(request_params, swagger_spec):

    schema = request_params['schema']

    def extract(inner_schema):

        if '$ref' in inner_schema:
            return extract(get_def(inner_schema, swagger_spec))
        else:

            parameters = []

            for request_name, params in inner_schema['properties'].items():

                # params defined in definitions
                if '$ref' in params:
                    extracted_nested_schema = extract(params)
                    is_required = request_name in inner_schema.get('required', [])
                    params['required'] = is_required
                    params['name'] = request_name
                    params['type'] = 'object'
                    params['nested'] = extracted_nested_schema
                    param_dict = get_if_present_else_none(parameter_fields, params)
                    parameters.append(param_dict)
                    continue
                else:

                    is_required = request_name in inner_schema.get('required', [])
                    params['required'] = is_required
                    params['name'] = request_name
                    param_dict = get_if_present_else_none(parameter_fields, params)
                    parameters.append(param_dict)

            return parameters

    extracted_schema = extract(schema)

    return extracted_schema


def extract_requests(swagger_spec):

    requests = []

    for path in swagger_spec['paths']:
        path_requests = swagger_spec['paths'][path]
        for request_type in path_requests:
            request_info = path_requests[request_type]
            if 'penelope' in request_info['tags'] and 'application/json' in request_info['consumes'] and 'application/json' in request_info['produces']:
                summary = request_info.get('summary', None)
                description = request_info.get('description', None)
                # this is whether arguments need to be sent or not
                name = path.split('/')[-1]

                if request_type == 'get':
                    if 'parameters' in request_info:
                        parameters = request_info['parameters']

                        extracted_parameters = extract_schema_get(parameters)

                        requests.append({'path': path,
                                         'name': name,
                                         'type': request_type.upper(),
                                         'parameters': extracted_parameters,
                                         'description': description})

                # possible to have get request without params
                if request_type == 'post':
                    if 'parameters' in request_info:
                        for request_params in request_info['parameters']:

                            if request_params['in'] == 'body':
                                extracted_parameters = extract_schema(request_params, swagger_spec)
                                requests.append({'path': path,
                                                 'name': name,
                                                 'type': request_type.upper(),
                                                 'parameters': extracted_parameters,
                                                 'description': description})

    return requests


def upload_swagger(swagger_spec):

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

    component_dict = get_if_present_else_none(component_fields, spec_props)
    component_dict['requests'] = extract_requests(swagger_spec)

    return component_dict
