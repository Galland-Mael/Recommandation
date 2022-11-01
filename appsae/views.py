from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render, redirect

from .models import RestaurantType, Adherant
from .formulaire import RestaurantTypeForm, AdherantForm
from django.core.mail import send_mail
import random


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

def verif_email(request):
    ''' Fonction qui permet l'envoi d'un mail à un utilisateur depuis l'adresse mail du site web '''
    try:
        send_mail("Vérification de votre compte - Ne pas répondre",
        "Code de vérification :\n"
        + "         " + random_value()
        + "\n\nL'équipe EatAdvisor",
        "eat_advisor2@outlook.fr",
        ["maelgalland.71@gmail.com"],
        fail_silently=False);
        print("reussi")
    except:
        print("fail")
    return render(request, 'appsae/mailtest.html')

def random_value():
    ''' Fonction qui renvoie une chaîne composée de 6 caractères entre 0 et 9 '''
    value_random = ""
    for i in range(6):
        value_random += str(random.randint(0, 9))
    return value_random