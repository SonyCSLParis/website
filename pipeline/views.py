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
from core.pipeline import populate_pipe_params, populate_pipes_params


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
        pipe = Pipe.objects.get(pk=kwargs['pk'])

        context['pipe'] = populate_pipe_params(pipe)
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

        pipe_data = populate_pipes_params([Pipe.objects.get(pk=kwargs['pipe_pk'])])
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
