from django.views import generic
from .filters import PipelineFilter
from .models import Pipeline
from django_filters.views import FilterView
from django.http import HttpResponse
from .models import Pipe
from django.utils.timezone import utc
import json
import datetime
from django.utils import formats
from django.template.loader import render_to_string

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


def extract_fields(dictionary):

        parameters = {}

        for k, v in dictionary.items():
            k = k if k != 'enum' else 'options'

            if k not in ['_state'] and v is not None:
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


def populate_params(sorted_pipe_objs):

    pipes = []

    for pipe in sorted_pipe_objs:
        parent_parameters = pipe.parameters.filter(sub_param=None)
        param_dict = extract_parameters(parent_parameters)
        request_dict = extract_fields(pipe.request.__dict__)
        request_dict['component'] = pipe.request.component.__dict__
        pipe_dict = extract_fields(pipe.__dict__)
        pipe_dict['parameters'] = param_dict
        pipe_dict['request'] = request_dict
        pipes.append(pipe_dict)

    return pipes


class PipelineView(generic.DetailView):
    model = Pipeline
    template_name = 'pipeline/pipeline.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        sorted_pipe_objs = [pipe for pipe in Pipe.objects.filter(pipe_line=context["pipeline"]).order_by('position')]

        populate_params(sorted_pipe_objs)
        context['pipes'] = populate_params(sorted_pipe_objs)

        return context


class PipelinesFilterView(FilterView):
    filterset_class = PipelineFilter
    template_name = 'pipeline/index.html'
    paginate_by = 4


class OutputDetailView(generic.TemplateView):
    template_name = 'pipeline/output.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pipe'] = Pipe.objects.get(pk=kwargs['pk'])
        return context


class InputDetailView(generic.TemplateView):
    template_name = 'pipeline/input.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pipe'] = Pipe.objects.get(pk=kwargs['pk'])
        return context


class EmptyPipeView(generic.TemplateView):
    template_name = 'pipeline/empty_pipeline.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pipeline'] = Pipeline.objects.get(pk=kwargs['pipeline_pk'])
        return context


class InputOutputDetailView(generic.TemplateView):
    template_name = 'pipeline/input_output.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pipeline'] = Pipeline.objects.get(pk=kwargs['pipeline_pk'])

        pipe_data = populate_params([Pipe.objects.get(pk=kwargs['pipe_pk'])])
        context['pipe'] = pipe_data[0]

        return context

#
# def input(request, pk):
#     input_inst = get_object_or_404(Pipe, pk=pk)
#
#     # If this is a POST request then process the Form data
#     if request.method == 'POST':
#
#         # Create a form instance and populate it with data from the request (binding):
#         form = InputForm(request.POST)
#
#         # Check if the form is valid:
#         if form.is_valid():
#             # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
#             input_inst.input = form.cleaned_data['input']
#             input_inst.data()
#
#     # If this is a GET (or any other method) create the default form.
#     else:
#         form = InputForm(initial={'input': "", })
#
#     return render(request, 'pipeline/pipeline.html', {'form': form, 'bookinst': book_inst})
