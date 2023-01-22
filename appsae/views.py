import json
import os.path
import sqlite3
import csv
from sqlite3 import OperationalError
import os, tempfile, zipfile, mimetypes
from wsgiref.util import FileWrapper
from django.conf import settings
from django.utils.dateformat import format
from surprise import KNNBasic
from surprise import Dataset
from surprise import Reader
from django.conf import settings
from collections import defaultdict
from operator import itemgetter
import heapq
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from surprise import SVD
from surprise.model_selection import cross_validate
import os
import csv
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.encoding import smart_str
from appsae.models import *
from .formulaire import *
from django.core.mail import send_mail
import random
from django.shortcuts import render
from django.http import HttpResponse
from .recommendation import *
from .gestion import *
from .gestion_note import *
from .gestion_utilisateur import *
from .gestion_groupes import *
from .gestion_avis import *
from .svd import *
import datetime
import time

PAGE = 0


def modifPAGE():
    global PAGE
    PAGE += 1


def index(request):
    if 'groupe' in request.session:
        del request.session['groupe']
    if 'nomGroupe' in request.session:
        del request.session['nomGroupe']
    context = {
        'meilleurRestaurants': listeAffichageCaroussel()
    }
    connect(request, context)
    return render(request, 'index/index.html', context)


def groupRecommandations(request):
    context = {
        'restaurants': listeAffichageCaroussel()
    }
    connect(request, context)
    return render(request, 'user/groupRecommandations.html', context)


def creationGroup(request):
    if 'groupe' in request.session:
        del request.session['groupe']
    if 'nomGroupe' in request.session:
        del request.session['nomGroupe']
    context = {}
    connect(request, context)
    return render(request, 'user/creationGroup.html', context)


def search(request):
    if request.GET["search"] != "":
        context = {
            'restaurants': Restaurant.objects.filter(nom__icontains=request.GET["search"]).order_by('-note')[:3]
        }
    elif request.GET["search"] == "":
        context = {
            'user': {}
        }
    return render(request, 'restaurants/searchRestaurants.html', context)


def createGroupe(request):
    if 'nomGroupe' not in request.POST:
        context = {}
        connect(request, context)
        return render(request, 'user/groupe.html', context)
    groupe = creationGroupe(request.POST['nomGroupe'], Adherant.objects.get(mail=request.session['mailUser']))
    for user in Adherant.objects.filter(mail__in=request.session['groupe']):
        ajoutUtilisateurGroupe(user, groupe)
    user = Adherant.objects.get(mail=request.session['mailUser'])
    list = []
    for groupe in Groupe.objects.all():
        if user in groupe.liste_adherants.all():
            list.append(groupe)
    context = {
        'groupe': Adherant.objects.filter(mail__in=request.session['groupe']),
        'nomGroup': request.POST['nomGroupe'],
        'listGroupe': list
    }
    connect(request, context)
    return render(request, 'user/groupe.html', context)


def groupe(request):
    user = Adherant.objects.get(mail=request.session['mailUser'])
    list = []
    for groupe in Groupe.objects.all():
        if user in groupe.liste_adherants.all():
            list.append(groupe)
    context = {
        'listGroupe': list
    }
    connect(request, context)
    return render(request, 'user/groupe.html', context)


def removeUser(request, user):
    list = request.session['groupe']
    if user in list:
        list.remove(user)
    request.session['groupe'] = list
    context = {
        'groupe': Adherant.objects.filter(mail__in=request.session['groupe'])
    }
    connect(request, context)
    return HttpResponse('')


def addUser(request, user):
    currentUser = Adherant.objects.get(mail=request.session['mailUser'])
    if 'groupe' in request.session:
        list = request.session['groupe']
    else:
        list = []
    if user not in list:
        list.append(user)
    request.session['groupe'] = list
    context = {
        'groupe': Adherant.objects.filter(mail__in=request.session['groupe']),
    }
    connect(request, context)
    return render(request, 'user/creationGroup.html', context)


def nomGroup(request):
    if 'groupe' not in request.session:
        return redirect('groupe')
    context = {
        'groupe': Adherant.objects.filter(mail__in=request.session['groupe']),
    }
    connect(request, context)
    return render(request, 'user/nomGroup.html', context)


def groupePage(request):
    if 'groupe' in request.session:
        del request.session['groupe']
    context = {}
    connect(request, context)
    return render(request, 'user/createGroup.html', context)


def searchUser(request):
    if request.GET["search"] != "":
        context = {
            'user': Adherant.objects.filter(mail__icontains=request.GET["search"]).exclude(
                mail=request.session['mailUser'])[:3]
        }
    elif request.GET["search"] == "":
        context = {
            'user': {}
        }
    return render(request, 'user/searchUser.html', context)


def vueRestaurant(request, pk):
    img = Restaurant.objects.get(pk=pk).img.all()
    user = Adherant.objects.get(mail=request.session['mailUser'])
    restaurant = Restaurant.objects.get(pk=pk)
    if (avisExist(user, restaurant)):
        avisUser = Avis.objects.filter(restaurant_fk=restaurant, adherant_fk=user)
        list = Avis.objects.filter(restaurant_fk=restaurant).all().exclude(adherant_fk=user)[:9]
    else:
        list = Avis.objects.filter(restaurant_fk=restaurant).all()[:10]
    context = {
        'restaurant': Restaurant.objects.filter(pk=pk),
        'imgRestaurants': ImageRestaurant.objects.filter(pk__in=img),
        'avis': list,
        'nbAvis': Avis.objects.filter(restaurant_fk=restaurant),
    }
    if Avis.objects.filter(adherant_fk=user, restaurant_fk=Restaurant.objects.get(pk=pk)):
        context['commentaire'] = True
    if (avisExist(user, restaurant)):
        context['avisUser'] = avisUser
    connect(request, context)
    return render(request, 'restaurants/vueRestaurant.html', context)


def addCommentaires(request, pk):
    user = Adherant.objects.get(mail=request.session['mailUser'])
    restaurant = Restaurant.objects.filter(pk=pk)
    img = Restaurant.objects.get(pk=pk).img.all()
    if (avisExist(user, restaurant[0])):
        avisUser = Avis.objects.filter(restaurant_fk=restaurant[0], adherant_fk=user)
        list = Avis.objects.filter().all()[:9]
    else:
        list = Avis.objects.filter().all()[:10]
    context = {
        'restaurant': restaurant,
        'imgRestaurants': ImageRestaurant.objects.filter(pk__in=img),
        'avis': list,
        'nbAvis': Avis.objects.filter(restaurant_fk=Restaurant.objects.get(pk=pk)),
    }
    if 'mailUser' in request.session:
        context['commentaire'] = True
    if (avisExist(user, restaurant[0])):
        context['avisUser'] = avisUser
    if (request.method == 'POST' and 'title-rating' in request.POST and 'comm' in request.POST):
        print(Adherant.objects.get(mail=request.session['mailUser']))
        print(Restaurant.objects.get(pk=pk))
        ajoutAvis(Adherant.objects.get(mail=request.session['mailUser']), Restaurant.objects.get(pk=pk),
                  request.POST['title-rating'], request.POST['comm'])
        if Avis.objects.get(adherant_fk=Adherant.objects.get(mail=request.session['mailUser']),
                            restaurant_fk=Restaurant.objects.get(pk=pk)) is not None:
            updateAvis(Adherant.objects.get(mail=request.session['mailUser']), Restaurant.objects.get(pk=pk),
                       request.POST['title-rating'], request.POST['comm'])
    else:
        messages.success(request, 'Les deux champs doivent être remplis.')
    connect(request, context)
    return render(request, 'restaurants/vueRestaurant.html', context)


def voirPlus(request, pk):
    context = {
        'avis': listeAffichageAvis(Restaurant.objects.get(pk=pk), 1),
    }
    if (afficherVoirPlus(Restaurant.objects.get(pk=pk), 1)):
        context['endAvis'] = True
    return render(request, 'avis/moreAvis.html', context)


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
            user = Adherant.objects.get(mail=request.POST['mail'])
            '''Création de la session ou je récupère que le mail de l'utilisateur'''
            request.session['mailUser'] = user.mail
            sessionMailUser = request.session['mailUser'];
            context = {
                'idUser': user.id,
                'name': user.nom,
                'prenom': user.prenom,
                'mail': user.mail,
                'birthDate': user.birthDate,
                'pseudo': user.pseudo,
                'photo': user.profile_picture.url,
                'meilleurRestaurants': listeAffichageCaroussel()
            }
            return render(request, 'index/index.html', context)
        else:
            messages.success(request, '*Wrong mail or password')
            return redirect('login')
    else:
        return render(request, 'user/login.html')


def modification(request):
    user = Adherant.objects.get(mail=request.session['mailUser'])
    #if request.FILES['photo'] !='' and request.FILES['photo'] != user.profile_picture.url:
        #updateProfilPick(user.mail,request.FILES['photo'])
    if request.POST['nom'] != '' and request.POST['nom'] != user.nom:
        updateNomUser(user.mail, request.POST['nom'])
    if request.POST['prenom'] != '' and request.POST['nom'] != user.prenom:
        updatePrenom(user.mail, request.POST['prenom'])
    context = {
        'meilleurRestaurants': listeAffichageCaroussel()
    }
    connect(request, context)
    return render(request, 'index/index.html', context)


def modifUser(request):
    context = {
        'user': Adherant.objects.get(mail=request.session['mailUser']),
    }
    connect(request, context)
    return render(request, 'user/modifUser.html', context)


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


def meilleurs_resto(request):
    ''' Renvoie les restaurants les mieux notés '''
    liste = listeAffichageCaroussel();
    return render(request, 'testMatteo.html', {'list': liste});


def carrousel():
    restaurant = Restaurant.objects.order_by('-note');
    list = [];
    for i in range(10):
        list.append(restaurant[i]);
    return list


def recommandation():
    restaurant = Restaurant.objects.order_by('-note');
    list = [];
    for i in range(3):
        list.append(restaurant[i]);
    return list


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
        return render(request, 'restaurants/searchRestaurants.html', context={'restaurants': restaurants})
    return HttpResponse('')


def matteo(request):
    adherant = Adherant.objects.filter(mail="matteo.miguelez@gmail.com")[0]
    resto = Restaurant.objects.filter(nom="Burger King")[0]
    print(afficherAvis(adherant, resto))
    print("------------------------------------------------")
    print(listeAffichageAvis(resto, adherant, PAGE))
    print(afficherVoirPlus(Restaurant.objects.filter(nom="Burger King")[0],
                           Adherant.objects.filter(mail="matteo.miguelez@gmail.com")[0], PAGE))
    modifPAGE()
    print("------------------------------------------------")
    print(listeAffichageAvis(resto, adherant, PAGE))
    print(afficherVoirPlus(Restaurant.objects.filter(nom="Burger King")[0],
                           Adherant.objects.filter(mail="matteo.miguelez@gmail.com")[0], PAGE))
    modifPAGE()
    print("------------------------------------------------")
    return redirect('index')


def recommendation(request):
    start = time.time()
    ratings_data = pd.read_csv('./ratings.csv')
    restaurant_metadata = pd.read_csv('./restaurant.csv', delimiter=';', engine='python')
    restaurant_metadata.info()
    ratings_data.info()
    """reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(ratings_data[['user_id', 'restaurant_id', 'note']], reader)
    svd = SVD(verbose=True, n_epochs=10, n_factors=100)
    cross_validate(svd, data, measures=['RMSE', 'MAE'], cv=4, verbose=True)
    trainset = data.build_full_trainset()
    svd.fit(trainset)
    print(svd.predict(uid=397784, iid=7859))  # uid user id iid item id"""
    # generate_recommendation(397784, svd, restaurant_metadata)
    print(time.time() - start)
    return HttpResponse('')


def export_restaurant(request):
    file = str(settings.BASE_DIR) + '/' + "restaurant.csv"
    f = open(file, "w")
    f.writelines("id ,nom, genre ")
    f.write('\n')
    for restaurant in Restaurant.objects.filter(ville='Philadelphia'):
        f.write(str(restaurant.pk))
        f.write(";")
        f.write(restaurant.nom)
        f.write(";")
        taille = restaurant.type.all().count()
        for i in range(taille):
            f.write(str(restaurant.type.all()[i]))
            if i != taille - 1:
                f.write(" ")
        f.write('\n')
    print(file)
    return redirect('index')


def export_ratings(request):
    file = str(settings.BASE_DIR) + '/' + "ratings.csv"
    f = open(file, "w")
    f.writelines("user_id,restaurant_id,note,timestamp")
    f.write('\n')
    for rating in Avis.objects.all().values_list('restaurant_fk', 'adherant_fk', 'note', 'unix_date'):
        f.write(str(rating)[1:-1])
        f.write('\n')
    print(file)
    return redirect('index')


def setImg(request):
    i = 0
    y = 0
    for restaurant in Restaurant.objects.all():
        y = y % 4
        if y == 0:
            print("insertion img front"'\n')
            restaurant.image_front = '/img_restaurant/imagefront1.jpg'
            restaurant.save()
        elif y == 1:
            print("insertion img front"'\n')
            restaurant.image_front = '/img_restaurant/imagefront2.jpg'
            restaurant.save()
        elif y == 2:
            print("insertion img front"'\n')
            restaurant.image_front = '/img_restaurant/imagefront3.jpg'
            restaurant.save()
        elif y == 3:
            print("insertion img front"'\n')
            restaurant.image_front = '/img_restaurant/imagefront4.jpg'
            restaurant.save()
        y += 1
        i = i % 12
        print("insertion liste img"'\n')
        imgset = ImageRestaurant.objects.all()
        restaurant.img.add(imgset[i])
        i += 1
        restaurant.img.add(imgset[i])
        i += 1
        restaurant.img.add(imgset[i])
        i += 1
        restaurant.img.add(imgset[i])
        i += 1
    return redirect('index')


def suppVille():
    listVilles = ["Philadelphia", "Tampa", "Indianapolis", "Nashville", "Tucson", "New Orleans", "Edmonton",
                  "Saint Louis", "Reno",
                  "Saint Petersburg", "Boise", "Santa Barbara", "Clearwater", "Wilmington", "St. Louis", "Metairie",
                  "Franklin"]
    Restaurant.objects.all().exclude(ville__in=listVilles).delete()
