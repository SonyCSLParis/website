from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
import json, yaml
# Imaginary function to handle an uploaded file.
from core import parse_open_api
from bravado_core.spec import Spec
from django.urls import reverse
import requests
from django.http import JsonResponse


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            scheme = request.scheme
            host = request.get_host()
            rest_endpoint = reverse('rest:save_component')
            url = scheme + '://' + host + rest_endpoint

            if not form.errors:
                form.spec_dict['name'] = request.POST['name']
                r = requests.put(url=url, json=form.spec_dict)
                return render(request, 'upload/success.html', {'form': form})
            else:
                return JsonResponse({
                    'success': False,
                })
    else:
        form = UploadFileForm()

    return render(request, 'upload/upload.html', {'form': form})
