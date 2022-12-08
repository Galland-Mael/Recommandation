import json
import os.path
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from appsae.model.models import *
from .formulaire import *
from django.core.mail import send_mail
import random
from django.shortcuts import render
from django.http import HttpResponse
from .gestion import liste_carrousel
from .gestion_utilisateur import *


def register(request):
    if request.method == "POST":
        '''Remplissage de la base de données'''
        form = AdherantForm(request.POST).save()
        return redirect('login')
    form = AdherantForm()
    context = {
        'form': form,
        'info': Adherant.objects.all
    }
    return render(request, 'user/register.html', context)
    # return JsonResponse({"form": list(form.values) })


def login(request):
    if request.method == "POST":
        info = Adherant.objects.all()
        contain = False
        for adherant in info:
            '''Verification'''
            if (request.POST['mail'] == adherant.mail):
                if (request.POST['password'] == adherant.password):
                    contain = True
        if contain:
            user = Adherant.objects.get(mail=request.POST['mail']);
            '''Création de la session ou je récupère que le mail de l'utilisateur'''
            request.session['mailUser'] = user.mail
            sessionMailUser = request.session['mailUser'];
            context = {
                'name': user.nom,
                'prenom': user.prenom,
                'mail': user.mail,
                'birthDate': user.birthDate,
                'pseudo': user.pseudo,
                'photo': user.profile_picture.url,
                'list': carrousel()
            }
            return render(request, 'index/index.html', context)
        else:
            messages.success(request, '*Wrong mail or password')
            return redirect('login')
    else:
        return render(request, 'user/login.html')


def index(request):
    context = {
        'list': carrousel()
    }
    return render(request, 'index/index.html', context)


def modifUser(request):
    return render(request, 'user/modifUser.html')


def verificationEmail(request):
    print("apeler")
    ''' Fonction qui permet l'envoi d'un mail à un utilisateur depuis l'adresse mail du site web '''
    try:
        send_mail("Vérification de votre compte - Ne pas répondre",
                  "Code de vérification :\n"
                  + "         " + randomValue()
                  + "\n\nL'équipe EatAdvisor",
                  "eat_advisor2@outlook.fr",
                  ["maelgalland.71@gail.com"],
                  fail_silently=False);
        print("reussi")
    except:
        print("fail")
        return HttpResponse("<p>Next</p>")


def randomValue():
    ''' Fonction qui renvoie une chaîne composée de 6 caractères entre 0 et 9 '''
    value_random = ""
    for i in range(6):
        value_random += str(random.randint(0, 9))
        print(value_random);
    return value_random


def meilleurs_resto(request):
    """ Renvoie les restaurants les mieux notés pour les carrousels """


def carrousel():
    restaurant = Restaurant.objects.order_by('-note');
    list = [];
    for i in range(10):
        list.append(restaurant[i]);
    return list;


def recommandation():
    restaurant = Restaurant.objects.order_by('-note');
    list = [];
    for i in range(3):
        list.append(restaurant[i]);
    return list;


'''Fonction qui detruit la session et redirige sur la page index'''


def logoutUser(request):
    try:
        del request.session['mailUser']
    except KeyError:
        pass
    return redirect('index')


def search(request):
    if request.GET["search"] != "":
        restaurants = Restaurant.objects.filter(nom__icontains=request.GET["search"])[:3]
        context = {
            'restaurants': restaurants
        }
        return render(request, 'restaurants/searchRestaurants.html', context)
    return HttpResponse('')


def vueRestaurant(request, pk):
    restaurant = Restaurant.objects.filter(pk=pk)
    imgRestaurants = ImageRestaurant.objects.filter(idRestaurant=pk)
    avis = Avis.objects.filter(restaurant_fk=restaurant[0]);
    user = Adherant.objects.get(mail=request.session['mailUser'])
    context = {
        'restaurant': restaurant,
        'imgRestaurants': imgRestaurants,
        'avis': avis,
        'mail': request.session['mailUser'],
        'photo': user.profile_picture.url,
    }
    return render(request, 'restaurants/vueRestaurant.html', context)


def addCommentaires(request, pk):
    valide = False;
    restaurant = Restaurant.objects.filter(pk=pk)
    imgRestaurants = ImageRestaurant.objects.filter(idRestaurant=pk)
    avis = Avis.objects.filter(restaurant_fk=restaurant[0]);
    context = {
        'restaurant': restaurant,
        'imgRestaurants': imgRestaurants,
        'avis': avis
    }
    print(request.POST['comm'])
    if (request.method == 'POST' and 'title-rating' in request.POST and 'comm' in request.POST):
        user = Adherant.objects.get(mail=request.session['mailUser'])
        print(user.pk)
        valide = True;
        Avis(note=request.POST['title-rating'], texte=request.POST['comm'], restaurant_fk=restaurant[0],adherant_fk=user).save()
    if (valide):

        return render(request, 'restaurants/vueRestaurant.html', context)
    else:
        messages.success(request, 'Les deux champs doivent être remplis.')
        return render(request, 'restaurants/vueRestaurant.html', context)


def update(request):
    return redirect('index')


def matteo(request):
    return redirect('index')
