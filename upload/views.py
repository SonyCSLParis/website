from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render

from component_browser.models import ComponentSpecification, Parameter, PathResponse, PathRequest
from .forms import UploadFileForm
import json
from django.urls import reverse
from django.http import JsonResponse


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            if not form.errors:
                form.spec_dict['name'] = request.POST['name']

                component_id = save_component(form.spec_dict, user=request.user)

                return HttpResponseRedirect(reverse('component_browser:component',
                                                    kwargs={'pk': component_id}
                                                    )
                                            )
            else:
                return JsonResponse({
                    'success': False,
                })
    else:
        form = UploadFileForm()

    return render(request, 'upload/upload.html', {'form': form})


def save_component(response_json, user):

        component_spec = response_json
        requests = component_spec['requests']
        del component_spec['requests']

        component = ComponentSpecification.objects.create(**component_spec)
        component.owner = user
        component.save()

        for request in requests:

            request_params = request['parameters']
            request_responses = request['responses']
            del request['parameters']
            del request['responses']

            request['component'] = component

            request_inst = PathRequest.objects.create(**request)
            request_inst.component = component
            request_inst.owner = user
            request_inst.save()

            def json_dump_val(param_dict):
                return {key: json.dumps(val) for key, val in param_dict.items()}

            def add_params(request_params, inst, parent_param=None):

                for parameter in request_params:

                    nested_params = None

                    if 'properties' in parameter or 'items' in parameter:

                        field_name = 'properties' if 'properties' in parameter else 'items'
                        nested_params = parameter[field_name]
                        del parameter[field_name]

                    if 'in' in parameter:
                        parameter['location'] = parameter['in']
                        del parameter['in']

                    # we want to represent all values as json strings so we can deserialise them as objects later
                    json_val_param = json_dump_val(parameter)
                    param_instance = Parameter.objects.create(**json_val_param)

                    # link parameter to parent param if it has one else link to response parameter
                    if parent_param:
                        parent_param.nested.add(param_instance)
                    else:
                        inst.parameters.add(param_instance)

                    if nested_params:
                        add_params(nested_params, inst, param_instance)

            def add_responses(responses, request_inst):

                for response in responses:

                    response_inst = PathResponse()
                    response_inst.request = request_inst
                    response_inst.status_code = response['status_code']
                    response_inst.save()
                    request_inst.responses.add(response_inst)

                    if 'description' in response:
                        response_inst.description = response['description']

                    if 'schema' in response:
                        print('schema', response['schema'])
                        add_params(response['schema'], response_inst)

                    response_inst.save()

            add_params(request_params, request_inst) # add params to request
            add_responses(request_responses, request_inst) # add responses to request

        return component.pk

