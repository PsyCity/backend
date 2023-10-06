import os
from django.shortcuts import render
from django.http import HttpResponse
from psycity.settings import BASE_DIR

def data_dir_api(request, filedir, filename):
    print(os.path.join(BASE_DIR, 'data_dir', filedir, filename), 'r')
    try:
        with open(os.path.join(BASE_DIR, 'data_dir', filedir, filename), 'rb') as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    except Exception as e:
        raise e
        return HttpResponse('<h1>File Not Found!</h1>', status=404)
