import os.path
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from .formulaire import *
from django.core.mail import send_mail
import random
from django.shortcuts import render
from django.http import HttpResponse


def register(request):
    if request.method == "POST":
        '''Remplissage de la base de données'''
        form = AdherantForm(request.POST).save()
        return redirect('login')
    form = AdherantForm()
    return render(request, 'user/register.html', {'form': form, 'info': Adherant.objects.all})
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
            user = Adherant.objects.get(mail=request.POST['mail'])
            '''Création de la session ou je récupère que l'id de l'utilisateur'''
            request.session['idUser'] = user.id
            context = {
                'idUser': user.id,
                'name': user.nom,
                'prenom': user.prenom,
                'mail': user.mail,
                'birthDate': user.birthDate,
                'pseudo': user.pseudo,
                'photo': user.profile_picture.url,
                'list': carrousel()
            }
            return render(request, 'index.html', context)
        else:
            messages.success(request, '*Wrong mail or password')
            return redirect('login')
    else:
        return render(request, 'user/login.html')


def index(request):
    liste = carrousel();
    return render(request, 'index.html', {'list': liste})


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
    ''' Renvoie les restaurants les mieux notés '''
    liste = carrousel();
    return render(request, 'testMatteo.html', {'list': liste});


def carrousel():
    restaurant = Restaurant.objects.order_by('-note');
    list = [];
    for i in range(10):
        list.append(restaurant[i]);
    return list;


'''Fonction qui detruit la session et redirige sur la page index'''


def logoutUser(request):
    try:
        del request.session['idUser']
    except KeyError:
        pass
    return redirect('index')


def search(request):
    print(request.GET["search"])
    return HttpResponse(request.GET["search"])

def goo(request):
    print('good')
    return HttpResponse('Réussie')
