from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader

from .models import RestaurantType


def index(request):
    nom = RestaurantType.objects.order_by('id')[:5]
    template = loader.get_template('appsae/index.html')
    context = {
        'nom': nom,
    }

    return HttpResponse(template.render(context, request))