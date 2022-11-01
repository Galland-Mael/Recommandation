from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render, redirect

from .models import RestaurantType, Adherant
from .formulaire import RestaurantTypeForm, AdherantForm


def index(request):
    '''
    nom = RestaurantType.objects.order_by('id')[:5]
    template = loader.get_template('appsae/index.html')
    context = {
        'nom': nom,
    }
    '''
    dataRestaurantType = RestaurantType.objects.all
    if request.method == "POST":
        form = RestaurantTypeForm(request.POST).save()
        return redirect('/appsae')
    form = RestaurantTypeForm()
    return render(request, 'appsae/index.html', {'form': form, 'dataRestaurantType': RestaurantType.objects.all})


def register(request):
    dataAdherant = Adherant.objects.all
    if request.method == "POST":
        form = AdherantForm(request.POST).save()
        return redirect('/appsae')
    form = AdherantForm()
    return render(request, 'appsae/register.html', {'form': form, 'dataAdherant': Adherant.objects.all})


def login(request):
    return render(request, 'appsae/login.html')