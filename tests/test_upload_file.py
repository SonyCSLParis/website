from unittest import TestCase
from core import parse_open_api
import json
from bravado_core.spec import Spec


def all_paths_but(spec, path):
    spec = dict(spec)  # duplicate
    path_spec = spec['paths'][path]
    spec['paths'] = {path: path_spec}
    return spec


def param_from_list(name, param_list):

    for param in param_list:

        if param['name'] == name:
            return param

    return None


def response_from_list(name, response_list):

    for response in response_list:

        if response['status_code'] == name:
            return response

    return None

def empty_paths(spec):
    spec = dict(spec)  # duplicate
    spec['paths'] = {}
    return spec

class TestExtractSwagger(TestCase):

    def test_spec_meta(self):

        spec = parse_open_api.load_spec('resolved.json')

        spec_meta = empty_paths(spec)
        parse, errors = parse_open_api.extract_swagger(spec_meta)

        self.assertIn('title', parse)
        self.assertIn('version', parse)
        self.assertIn('host', parse)
        self.assertIn('base_path', parse)
        self.assertIn('openapi_version', parse)

    def test_extract_in_body_array(self):

        spec = parse_open_api.load_spec('resolved.json')

        simple_get_spec = all_paths_but(spec, path='/array_post')
        parse, errors = parse_open_api.extract_swagger(simple_get_spec, strict=False)
        simple_post = parse['requests'][0]
        self.assertEqual('POST', simple_post['type'])
        self.assertIn('parameters', simple_post)
        top_level_object = simple_post['parameters'][0]

        self.assertEqual(top_level_object,
                         {'type': 'array', 'name': 'param1', 'required': False, 'items': [{'type': 'string'}],
                          'in': 'body'}
                         )

    def test_extract_in_body_array_dict(self):
        spec = parse_open_api.load_spec('resolved.json')

        simple_get_spec = all_paths_but(spec, path='/array_dict_post')
        parse, errors = parse_open_api.extract_swagger(simple_get_spec, strict=False)
        simple_post = parse['requests'][0]
        self.assertEqual('POST', simple_post['type'])
        self.assertIn('parameters', simple_post)
        top_level_object = simple_post['parameters'][0]

        self.assertEqual(top_level_object, {'type': 'array',
                                            'name': 'param1',
                                            'required': False,
                                            'items': [{'type': 'object',
                                                      'properties': [
                                                          {'type': 'string',
                                                           'name': 'prop1',
                                                           'required': True},
                                                          {'type': 'string',
                                                           'name': 'prop2',
                                                           'required': True}]}],
                                            'in': 'body'})

    def test_extract_in_body_array_dict_array(self):
        spec = parse_open_api.load_spec('resolved.json')

        simple_get_spec = all_paths_but(spec, path='/array_dict_array_post')
        parse, errors = parse_open_api.extract_swagger(simple_get_spec, strict=False)
        simple_post = parse['requests'][0]
        self.assertEqual('POST', simple_post['type'])
        self.assertIn('parameters', simple_post)
        top_level_object = simple_post['parameters'][0]

        self.assertEqual(top_level_object,
                         {'type': 'array', 'name': 'param1', 'description': 'Inventory item to add', 'required': False,
                          'items': [{'type': 'object', 'properties': [
                              {'type': 'array', 'name': 'prop1', 'required': True, 'items': [{'type': 'string'}]},
                              {'type': 'array', 'name': 'prop2', 'required': False, 'items': [{'type': 'string'}]}]}],
                          'in': 'body'}
                         )

    def test_extract_in_body_dict_post(self):
        spec = parse_open_api.load_spec('resolved.json')

        simple_get_spec = all_paths_but(spec, path='/dict_post')
        parse, errors = parse_open_api.extract_swagger(simple_get_spec, strict=False)
        simple_post = parse['requests'][0]
        self.assertEqual('POST', simple_post['type'])
        self.assertIn('parameters', simple_post)
        top_level_object = simple_post['parameters'][0]

        self.assertEqual(top_level_object,
                         {'type': 'object', 'name': 'param1', 'required': False, 'properties': [
                             {'type': 'string', 'name': 'name', 'example': 'example string', 'required': False},
                             {'type': 'string', 'name': 'release_date', 'example': 'an example', 'required': True}],
                          'in': 'body'}
        )

    def test_extract_in_body_dict_dict_post(self):
        spec = parse_open_api.load_spec('resolved.json')

        simple_get_spec = all_paths_but(spec, path='/dict_dict_post')
        parse, errors = parse_open_api.extract_swagger(simple_get_spec, strict=False)
        simple_post = parse['requests'][0]
        self.assertEqual('POST', simple_post['type'])
        self.assertIn('parameters', simple_post)

        top_level_object = simple_post['parameters'][0]

        self.assertEqual(top_level_object,
                         {'type': 'object', 'name': 'param1', 'required': False,
                          'properties': [{'type': 'string', 'name': 'prop1', 'example': 'a string', 'required': True},
                                         {'type': 'object',
                                          'name': 'nestedprop',
                                          'properties': [
                                             {'type': 'string', 'name': 'prop1', 'example': 'prop1 string',
                                              'required': True},
                                             {'type': 'string', 'name': 'prop2', 'example': 'prop2 string',
                                              'required': True}]}], 'in': 'body'}
                         )

    def test_extract_in_body_post(self):

        spec = parse_open_api.load_spec('resolved.json')

        simple_get_spec = all_paths_but(spec, path='/simple_post')
        parse, errors = parse_open_api.extract_swagger(simple_get_spec, strict=False)
        simple_post = parse['requests'][0]
        self.assertEqual('POST', simple_post['type'])
        self.assertIn('parameters', simple_post)

        params = simple_post['parameters']
        self.assertEqual(1, len(params))

        # First check that all

        # expect generic param information is extracted
        self.assertEqual(params[0], {'type': 'number',
                                    'name': 'param',
                                    'default': 1,
                                    'example': '1',
                                    'required': False, 'in': 'body'}
                         )


        # now test the responses
        responses = simple_post['responses']

        response_200 = response_from_list('200', responses)
        self.assertEqual(response_200,
                         {'status_code': '200', 'description': '200 description'})

    def test_extract_in_query_get(self):

        spec = parse_open_api.load_spec('resolved.json')

        simple_get_spec = all_paths_but(spec, path='/simple_get')
        parse, errors = parse_open_api.extract_swagger(simple_get_spec, strict=False)
        simple_get_request = parse['requests'][0]

        self.assertEqual('/simple_get', simple_get_request['path'])
        self.assertEqual('simple_get', simple_get_request['name'])
        self.assertEqual('GET', simple_get_request['type'])
        self.assertEqual('description text', simple_get_request['description'])
        self.assertIn('parameters', simple_get_request)

        params = simple_get_request['parameters']
        self.assertEqual(8, len(params))

        # First check that all

        # expect generic param information is extracted
        param = param_from_list('stringparam', params)
        self.assertEqual(param, {'type': 'string',
                                 'name': 'stringparam',
                                 'description': 'stringparam description text',
                                 'required': False,
                                 'in': 'query'})

        param = param_from_list('stringenumparam', params)
        self.assertEqual(param['enum'], ['val1', 'val2', 'val3'])

        param = param_from_list('stringparamrequired', params)
        self.assertEqual(param['required'], True)

        # when required not supplied should default to false
        param = param_from_list('stringparamnorequired', params)
        self.assertEqual(param['required'], False)

        param = param_from_list('intparam', params)
        self.assertEqual(param['type'], 'integer')
        self.assertEqual(param['maximum'], 100)
        self.assertEqual(param['minimum'], 1)

        param = param_from_list('numparam', params)
        self.assertEqual(param['type'], 'number')
        self.assertEqual(param['maximum'], 100.0)
        self.assertEqual(param['minimum'], 1.0)

        param = param_from_list('boolparam', params)
        self.assertEqual(param['type'], 'boolean')
        self.assertEqual(param['default'], True)

        # now test the responses
        responses = simple_get_request['responses']

        response_200 = response_from_list('200', responses)
        self.assertEqual(response_200['schema'][0],
                         {'type': 'string',
                          'default': 'default string',
                          'example': 'some string',
                          'description': 'simple string'})
        response_201 = response_from_list('201', responses)
        self.assertEqual(response_201['schema'][0],
                         {'type': 'integer',
                          'default': 1,
                          'example': '101',
                          'description': 'simple integer'})
        response_202 = response_from_list('202', responses)
        self.assertEqual(response_202['schema'][0],
                         {'type': 'number',
                          'default': 1,
                          'example': '1',
                          'description': 'simple number'})
        response_203 = response_from_list('203', responses)
        self.assertEqual(response_203['schema'][0],
                         {'type': 'string',
                          'default': 'default string',
                          'example': 'some string',
                          'description': 'simple string enum',
                          'enum': ['val1', 'val2', 'val3']}
                         )

    def test_tags(self):

        spec = parse_open_api.load_spec('resolved.json')
        # shouldn't load this request as it isn't tagged with penelope
        simple_get_spec = all_paths_but(spec, path='/simple_post_not_for_penelope')
        parse, errors = parse_open_api.extract_swagger(simple_get_spec, strict=False)

        self.assertFalse(parse['requests'])

    # todo add support for path params
