from django.views import generic
from .filters import PipelineFilter
from .models import Pipeline
from django_filters.views import FilterView
from .models import Pipe
from django.http import HttpResponseRedirect
from core.pipeline import populate_pipe_params, populate_pipes_params
from django.http import HttpResponse
import json
from . import forms
import requests
from django.core import serializers
from component_browser.models import PathRequest, Parameter
from pipeline.models import Pipe, Pipeline
import json
import datetime
from core.pipeline import populate_pipes_params, get_request_params
from django.urls import reverse
import jmespath
from django.http import JsonResponse

param_prefix = 'param-'
val_prefix = 'val-'


class PipelineFormView(generic.FormView):

    template_name = 'pipeline/new_pipeline.html'
    form_class = forms.PipelineForm

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        if form.is_valid():
            requests = form.cleaned_data['requests']
            del form.cleaned_data['requests']
            obj = Pipeline(**form.cleaned_data)
            obj.save()
            obj.owner = self.request.user

            for request in requests:
                obj.requests.add(request)
            obj.save()

            return HttpResponseRedirect(reverse('pipeline:pipeline',
                                                kwargs={'pk': obj.pk}
                                                )
                                        )
        else:
            return True

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        query_set = context['form'].fields["requests"].queryset
        context['has_requests'] = len(query_set) != 0

        return context

    def get_form_kwargs(self):
        kwargs = super(PipelineFormView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class PipelineView(generic.DetailView):
    model = Pipeline
    template_name = 'pipeline/pipeline.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        sorted_pipe_objs = [pipe for pipe in Pipe.objects.filter(pipe_line=context["pipeline"]).order_by('position')]

        populate_pipes_params(sorted_pipe_objs)
        context['pipes'] = populate_pipes_params(sorted_pipe_objs)

        return context


class PipelinesFilterView(FilterView):
    filterset_class = PipelineFilter
    template_name = 'pipeline/index.html'
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            context['pipelines'] = Pipeline.objects.filter(owner=user)
        return context


class OutputDetailView(generic.TemplateView):
    template_name = 'pipeline/output.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pipe'] = Pipe.objects.get(pk=kwargs['pk'])
        return context


def render_html(request,  *args, **kwargs):
    pipe = Pipe.objects.get(pk=kwargs['pk'])
    html_obj = json.loads(pipe.output)
    return HttpResponse(html_obj['html'])


class InputDetailView(generic.TemplateView):
    template_name = 'pipeline/input.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pipe = Pipe.objects.get(pk=kwargs['pk'])

        context['pipe'] = populate_pipe_params(pipe)
        return context


class EmptyPipeView(generic.TemplateView):
    template_name = 'pipeline/empty_pipeline.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pipeline'] = Pipeline.objects.get(pk=kwargs['pk'])
        return context


class InputOutputDetailView(generic.TemplateView):
    template_name = 'pipeline/input_output.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pipeline'] = Pipeline.objects.get(pk=kwargs['pk'])

        pipe_data = populate_pipes_params([Pipe.objects.get(pk=kwargs['pipe_pk'])])
        context['pipe'] = pipe_data[0]

        return context

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

NamedParam = namedtuple('NamedParam', ['name', 'id', 'type', 'value', 'converter', 'is_expression'])
import objectpath
import re

eval_pattern = re.compile('>>(\d+)')


def evaluate_expression(targeted_expression, param_id, param_name, errors, target_pipe):

    if targeted_expression[0:2] == '>>':

        a = eval_pattern.match(targeted_expression)

        # Always save the expression to allow for incrementally building up expresssions even if they are erroneous.
        param = Parameter.objects.get(id=param_id)
        param.expression = targeted_expression  # want to store exactly what the user used
        param.save()

        if not a:
            errors[val_prefix+param_name].append('Expression error. Could not match output identifier.')
            return '', True

        output_number = a.group(1)
        pipe = Pipe.objects.filter(pipe_line=target_pipe.pipe_line.id).get(local_id=output_number)
        output = pipe.output
        output = json.loads(output)
        expression = targeted_expression.replace('>>'+output_number, 'output')

        try:
            result = jmespath.search(expression, output)
        except jmespath.exceptions.ParseError as e:
            errors[val_prefix + param_id].append('{}'.format(e))
            return targeted_expression, True

        return json.dumps(result), True

    return targeted_expression, False


from collections import defaultdict


def convert_and_eval_params(input_dict, pipe):

    errors = defaultdict(list)
    params = {}

    local_dict = {k: v for k, v in input_dict.items()}

    for prefix_name, param_info in local_dict.items():
        if param_prefix in prefix_name:
            name, id, type = param_info.split()
            value = local_dict.get(val_prefix+name)
            # the type of the evaluated expression should evaluate to the specified json type
            value, is_expression = evaluate_expression(value, id, name, errors, pipe)

            params[id] = NamedParam(name, id, type, value, json_converter_funcs[type], is_expression)

    # now check if parameters are valid json
    for id, param in params.items():
        value = param.value
        param_field_id = 'val-' + id
        converter = param.converter
        try:
            converted_value = converter(value)
        except Exception as e:
            if param.is_expression and param_field_id not in errors:
                errors[param_field_id].append('Expression evaluated to a value that is not of type {}.'.format(param.type))
            elif not param.is_expression:
                errors[param_field_id].append('Value is not of type {}.'.format(param.type))
            break

    # remove errors that are due to required parameters unless these are expressions
    # if they are expressions we want to provide feedback on the evaluation
    for id, param in params.items():
        param_obj = Parameter.objects.get(pk=param.id)
        is_required = convert_bool(param_obj.required)
        is_empty = param.value == ''
        input_field_id = 'val-'+param.id

        if is_required and is_empty:

            if param.is_expression:
                errors[input_field_id].append('Parameter cannot be empty but expression evaluated to empty string.')
            else:
                # The key should be the input field id. This is used to map the message to an input field to display the
                # error message.
                errors[input_field_id].append('Parameter cannot be empty.')
        elif is_empty:

            if param.is_expression:
                errors[input_field_id].append("Expression evaluated to empty string. "
                                              "This was probably not intended though the parameter is not required.")
            else:
                # suppress any errors as val was not required so it being empty doesn't matter
                # this wouldn't be neccesary if converters don't create an error from an empty string
                if input_field_id in errors:
                    del errors[input_field_id]

    return list(params.values()), errors


def save_parameters(pipe_object, parameters, validation_errors):

    for param in parameters:
        param_obj = Parameter.objects.get(pk=param.id)
        param_obj.value = param.value
        param_obj.save()

    now = datetime.datetime.now()
    pipe_object.input_time = now

    if not validation_errors:
        pipe_object.output = ""
        pipe_object.output_time = None
        pipe_object.run_time = now
        pipe_object.save(force_update=True)


def format_error_output(errors):
    return "\n".join(list(errors.values()))


default_status_responses = {
    200: 'Success',
    300: 'Redirect occured', # probably not appropriate for penelope?
    400: 'There is some error in the form.',
    500: 'There was an error on the server.'
}


def round_down(num, divisor):
    return num - (num%divisor)


def get_spec_responses(pipe):

    defined_responses = {}

    responses_db = pipe.request.responses.all()

    for response in responses_db:
        if response.description:
            defined_responses[response.status_code] = response.description

    return defined_responses


def request_path(request_obj):
    component_obj = request_obj.component
    request_path = request_obj.path

    # TODO this is a dirty hack. The request path starts with a / and concatenating it with the base path results
    # in a double /. So we delete it
    if request_path[0] == '/':
        request_path = request_path[1:]

    return component_obj.host + component_obj.base_path + request_path


def save_output(pipe_object, output):
    now = datetime.datetime.now()
    pipe_object.output = json.dumps(output)
    pipe_object.output_time = now
    pipe_object.save(force_update=True)


def run(request, pk):
    if request.method == 'PUT':
        request_data = json.loads(request.body)

        rest_url = reverse('rest:rest')
        pipe = Pipe.objects.get(pk=request_data['pipe_id'])
        del request_data['pipe_id']

        # Extract params from form and validate formats
        source_params, validation_errors = convert_and_eval_params(request_data, pipe)
        save_parameters(pipe, source_params, validation_errors)

        if validation_errors:
            return JsonResponse({"errors": validation_errors}, status=400)

        # extract parameters for request
        request_data = get_request_params(pipe)
        request_obj = pipe.request
        request_url = request_path(request_obj)

        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

        try:
            if request_obj.type == "POST":
                r = requests.post('http://'+request_url, json=request_data, headers=headers)
            elif request_obj.type == "GET":
                r = requests.get('http://' + request_url, json=request_data, headers=headers)
        except Exception as e:
            return JsonResponse({"errors": {'general':
                                                     "Could not make request to {}. "
                                                     "Perhaps the server is down?".format(e.request.url)}},
                                status="500")

        spec_responses = get_spec_responses(pipe)

        try:
            content = json.loads(r.content)
        except Exception as e:
            content = None

        is_defined_in_spec = r.status_code in spec_responses

        if is_defined_in_spec and content:
            if round_down(r.status_code, 100) == 200:
                if 'html' in content:
                    save_output(pipe, content)
                else:
                    save_output(pipe, {"output": content,
                                       "description": spec_responses[r.status_code]})

                return JsonResponse({"output": content,
                                     "description": spec_responses[r.status_code]},
                                    status=r.status_code)
        if content:
            return JsonResponse(content, status=r.status_code)
        else:
            return JsonResponse({"errors": {'general': default_status_responses[round_down(r.status_code, 100)]}},
                                status=r.status_code)


def create_pipe(request, pk):

    if request.method == 'PUT':
        request_data = json.loads(request.body)
        pipe_id = request_data['pipe_id']  # use this to decide after which pipe to create new pipe
        request_id = request_data['request_id']

        pipeline = Pipeline.objects.get(pk=pk)
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
                                       position=next_postition,
                                       owner=request.owner)

        for parameter in parameters:
            new_pipe.parameters.add(parameter)

        new_pipe.save()
        json_new_pipe = json.loads(serializers.serialize('json', [new_pipe]))
        json_new_pipe = json_new_pipe[0]
        json_new_pipe['pipe_origin'] = pipe_id
        return JsonResponse({"created_pipe": json_new_pipe})


def delete_pipe(request, pk):
    if request.method == 'PUT':
        request_data = json.loads(request.body)
        pipe_id = request_data['pipe_id']  # use this to decide after which pipe to create new pipe
        pipe = Pipe.objects.get(pk=pipe_id)
        pipe.delete()
        return JsonResponse({"deleted_pipe": pipe_id})


def move_up_pipe(request, pk):
    if request.method == 'PUT':
        request_data = json.loads(request.body)
        pipe_id = request_data['pipe_id']  # use this to decide after which pipe to create new pipe
        current_pipe = Pipe.objects.get(pk=pipe_id)
        current_position = current_pipe.position
        try:
            pipe_after_current = Pipe.objects.filter(pipe_line=pk) \
                .get(position=current_position - 1)
            current_pipe.position = pipe_after_current.position
            pipe_after_current.position = current_position
            current_pipe.save()
            pipe_after_current.save()

            return JsonResponse({"pipe_origin_id": pipe_id,
                             "pipe_swap_id": pipe_after_current.id})
        except :

            return JsonResponse({"message": "couldn't process request"})


def move_down_pipe(request, pk):
    if request.method == 'PUT':
        request_data = json.loads(request.body)
        pipe_id = request_data['pipe_id']  # use this to decide after which pipe to create new pipe
        current_pipe = Pipe.objects.get(pk=pipe_id)
        current_position = current_pipe.position
        try:
            pipe_before_current = Pipe.objects.filter(pipe_line=pk)\
                                              .get(position=current_position + 1)
            current_pipe.position = pipe_before_current.position
            pipe_before_current.position = current_position
            current_pipe.save()
            pipe_before_current.save()

            return JsonResponse({"pipe_origin_id": pipe_id,
                             "pipe_swap_id": pipe_before_current.id})
        except:

            return JsonResponse({"message": "couldn't process request"})
