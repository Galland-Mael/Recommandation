from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render, redirect

from .models import RestaurantType, Adherant
from .formulaire import RestaurantTypeForm, AdherantForm
from django.core.mail import send_mail
import random
from django.shortcuts import render

def testAntoine(request):
    '''
    nom = RestaurantType.objects.order_by('id')[:5]
    template = loader.get_template('appsae/testAntoine.html')
    context = {
        'nom': nom,
    }
    '''
    dataRestaurantType = RestaurantType.objects.all
    if request.method == "POST":
        form = RestaurantTypeForm(request.POST).save()
        return redirect('testAntoine')
    form = RestaurantTypeForm()
    return render(request, 'testAntoine.html', {'form': form, 'dataRestaurantType': RestaurantType.objects.all})


def register(request):
    dataAdherant = Adherant.objects.all
    if request.method == "POST":
        form = AdherantForm(request.POST).save()
        return redirect('')
    form = AdherantForm()
    return render(request, 'register.html', {'form': form, 'dataAdherant': Adherant.objects.all})



def login(request):
    return render(request,'login.html')


def verificationEmail(request):
    ''' Fonction qui permet l'envoi d'un mail à un utilisateur depuis l'adresse mail du site web '''
    try:
        send_mail("Vérification de votre compte - Ne pas répondre",
        "Code de vérification :\n"
                  + "         " + randomValue()
                  + "\n\nL'équipe EatAdvisor",
                  "eat_advisor2@outlook.fr",
                  ["maelgalland.71@gmail.com"],
                  fail_silently=False);
        print("reussi")
    except:
        print("fail")
    return render(request, 'mail.html')

def randomValue():
    ''' Fonction qui renvoie une chaîne composée de 6 caractères entre 0 et 9 '''
    value_random = ""
    for i in range(6):
        value_random += str(random.randint(0, 9))
    return value_random