from django.views import generic
from .filters import PipelineFilter
from .models import Pipeline
from django_filters.views import FilterView
#from .forms import InputForm
from django.http import HttpResponse
from .models import Pipe
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
import json

class PipelineView(generic.TemplateView):
    model = Pipeline
    template_name = 'pipeline/pipeline.html'

    def get(self, request,  *args, **kwargs):
        return render(request, self.template_name, {"pipeline": Pipeline.objects.get(pk=self.kwargs['pk'])})

    def post(self, request,  *args, **kwargs):
        input_text = request.POST['input']
        pipe_id = request.POST['pipe_id']
        pipe_object = Pipe.objects.get(pk=pipe_id)
        pipe_object.input = input_text
        pipe_object.save()

        if self.request.is_ajax():
            return HttpResponse(json.dumps("success"),
                                content_type="application/json")
        else:
            return self.get(request, args, kwargs)


class PipelinesFilterView(FilterView):
    filterset_class = PipelineFilter
    template_name = 'pipeline/index.html'
    paginate_by = 4

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
#             input_inst.save()
#
#     # If this is a GET (or any other method) create the default form.
#     else:
#         form = InputForm(initial={'input': "", })
#
#     return render(request, 'pipeline/pipeline.html', {'form': form, 'bookinst': book_inst})
