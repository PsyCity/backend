import os
from django.shortcuts import render
from django.http import HttpResponse
from psycity.settings import BASE_DIR
from django.views.generic import TemplateView, ListView
from core.models import Team
def data_dir_api(request, filedir, filename):
    print(os.path.join(BASE_DIR, 'data_dir', filedir, filename), 'r')
    try:
        with open(os.path.join(BASE_DIR, 'data_dir', filedir, filename), 'rb') as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    except Exception as e:
        return HttpResponse('<h1>File Not Found!</h1>', status=404)


class LeaderView(TemplateView):
    template_name = "core/leader.html"

    extra_context = {"teams": list(Team.objects.all()).sort(key=lambda x: x.total_asset)}
    

def leaderboard(request):
    teams = list(Team.objects.all())

    teams.sort(reverse=True, key=lambda x: x.total_asset)        
    return render(request, 'core/leader.html', {"teams": teams})