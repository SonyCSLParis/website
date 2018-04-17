from django.shortcuts import render
# Create your views here.
from django.views import generic
from .models import Request, ComponentSpecification


class DetailView(generic.DetailView):
    model = ComponentSpecification
    template_name = 'browser/detail.html'

# from django.views import generic
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#
# class ComponentGridView(generic.ListView):
#     model = Question
#     template_name = 'your_app_name/questions.html'
#     context_object_name = 'questions'
#     paginate_by = 10
#     queryset = Question.objects.all()


class IndexView(generic.ListView):
    template_name = 'browser/index.html'
    context_object_name = 'component_specifications'
    paginate_by = 2

    def get_queryset(self):
        """Return the last five published questions."""
        return ComponentSpecification.objects.prefetch_related('request_set').all()