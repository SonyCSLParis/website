from django.shortcuts import render
# Create your views here.
from django.views import generic
from .models import PathRequest, ComponentSpecification
from .filters import ComponentFilter
from django_filters.views import FilterView


class ComponentDetailView(generic.DetailView):
    model = ComponentSpecification
    template_name = 'component_browser/component_detail.html'


class RequestDetailView(generic.DetailView):
    model = PathRequest
    template_name = 'component_browser/request_detail.html'

    def get_context_data(self, **kwargs):

        context = {'request': {k: v for k, v in self.object.__dict__.items() if k != '_state'}}
        context['request']['component_name'] = self.object.component.name
        def extract_param_fields(dictionary, filter_fields):

            parameters = {}

            for k, v in dictionary.items():
                k = k if k != 'enum' else 'options'
                k = k if k!= 'location' else 'in'

                if k not in filter_fields and v is not '' and v is not None:
                    parameters[k] = v

            return parameters

        def extract_parameters(objects):

            internal_parameters = []

            for obj in objects:
                nested_params = obj.nested.all()

                if nested_params:
                    nested_params = extract_parameters(nested_params)

                param_dict = obj.__dict__
                if nested_params:
                        param_dict['properties'] = nested_params

                if param_dict.get('location', None) == '"body"':
                    return nested_params
                else:
                    internal_parameters.append(extract_param_fields(param_dict, ['id', '_state']))

            return internal_parameters

        def extract_response_fields(response_dict):

            return {key: value for key, value in response_dict.items() if key in ['status_code', 'description', 'parameters']}

        def extract_responses(objects):

            responses = []

            for obj in objects:

                response_dict = obj.__dict__
                params = obj.parameters.all()
                params = extract_parameters(params)
                response_dict['parameters'] = params
                responses.append(extract_response_fields(response_dict))

            return responses

        context['parameters'] = extract_parameters(self.object.parameters.filter(sub_param=None))
        context['responses'] = extract_responses(self.object.responses.all())
        return context


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
    template_name = 'component_browser/index.html'
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            context['specifications'] = ComponentSpecification.objects.filter(owner=user)

        return context

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
