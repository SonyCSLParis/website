from django.shortcuts import render
# Create your views here.
from django.views import generic
from .models import Request, ComponentSpecification
from .filters import ComponentFilter
from django_filters.views import FilterView


class ComponentDetailView(generic.DetailView):
    model = ComponentSpecification
    template_name = 'browser/component_detail.html'


class RequestDetailView(generic.DetailView):
    model = Request
    template_name = 'browser/request_detail.html'


# from django.views import generic
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#
# class ComponentGridView(generic.ListView):
#     model = Question
#     template_name = 'your_app_name/questions.html'
#     context_object_name = 'questions'
#     paginate_by = 10
#     queryset = Question.objects.all()


# def search(request):
#     component_list = ComponentSpecification.objects.all()
#     component_filter = ComponentFilter(request.GET, queryset=component_list)
#     return render(request, 'search/user_list.html', {'filter': component_filter})


class ComponentFilterView(FilterView):
    filterset_class = ComponentFilter
    template_name = 'browser/index.html'
    paginate_by = 4

# class IndexView(generic.ListView):
#     template_name = 'browser/index.html'
#     context_object_name = 'component_specifications'
#     model = ComponentSpecification
#     paginate_by = 3
#
#     user_filter = ComponentFilter(self.request.GET, queryset=user_list)
#
#     def get_queryset(self):
#
#
#
#         return ComponentSpecification.objects.prefetch_related('request_set').all()
