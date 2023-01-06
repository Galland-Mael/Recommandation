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

import os
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appsae.settings")

import django

django.setup()

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils.encoding import smart_str

from .models import *
from .formulaire import *
from django.core.mail import send_mail
import random
from django.shortcuts import render
from django.http import HttpResponse
from .gestion import *
from .gestion_utilisateur import *
from .gestion_groupes import *
from .gestion_avis import *
import datetime
import time
from surprise import KNNBasic
from surprise import Dataset
from surprise import Reader

PAGE = 0


def modifPAGE():
    global PAGE
    PAGE += 1


def register(request):
    if request.method == "POST":
        '''Remplissage de la base de données'''
        form = AdherantForm(request.POST).save()
        print(request.POST["mail"])
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
            '''Création de la session ou je récupère que le mail de l'utilisateur'''
            request.session['mailUser'] = user.mail
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
            return render(request, 'index/index.html', context)
        else:
            messages.success(request, '*Wrong mail or password')
            return redirect('login')
    else:
        return render(request, 'user/login.html')


def index(request):
    liste = carrousel();
    return render(request, 'index/index.html', {'list': liste})


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
    print("kerkekeke")
    if request.GET["search"] != "":
        restaurants = Restaurant.objects.filter(nom__icontains=request.GET["search"])[:3]
        return render(request, 'restaurants/searchRestaurants.html', context={'restaurants': restaurants})
    return HttpResponse('')


def vueRestaurant(request, pk):
    print("vuerestaurant")
    restaurant = Restaurant.objects.filter(pk=pk)
    imgRestaurants = ImageRestaurant.objects.filter
    return render(request, 'restaurants/vueRestaurant.html', context={'restaurant': restaurant})


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


def export_restaurant(request):
    file = str(settings.BASE_DIR) + '/' + "restaurant.csv"
    f = open(file, "w")
    f.writelines("id ,nom ,pays, telephone ,image_front ,note, ville ")
    f.write('\n')
    for restaurant in Restaurant.objects.all().filter(ville='Tucson').values_list('id', 'nom', 'pays', 'telephone', 'image_front', 'note', 'ville'):
            f.write(str(restaurant)[1:-1])
            f.write('\n')
    print(file)
    return redirect('index')


def export_ratings(request):
    file = str(settings.BASE_DIR) + '/' + "ratings.csv"
    f = open(file, "w")
    f.writelines("restaurant_id,user_id,note,timestamp")
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


def recommandation(request):
    def load_dataset():
        file = str(settings.BASE_DIR) + '/' + "ratings.csv"
        reader = Reader(line_format='user item rating timestamp', sep=',', skip_lines=1)
        ratings_dataset = Dataset.load_from_file(file, reader=reader)

        # Lookup a movie's name with it's Movielens ID as key
        restaurantID_to_name = {}
        file = str(settings.BASE_DIR) + '/' + "restaurant.csv"
        with open(file, newline='', encoding='ISO-8859-1') as csvfile:
            restaurant_reader = csv.reader(csvfile)
            next(restaurant_reader)
            for row in restaurant_reader:
                restaurantID = int(row[0])
                restaurant_name = row[1]
                restaurantID_to_name[restaurantID] = restaurant_name
        # Return both the dataset and lookup dict in tuple
        return (ratings_dataset, restaurantID_to_name)

    dataset, restaurantID_to_name = load_dataset()

    # Build a full Surprise training set from dataset
    trainset = dataset.build_full_trainset()

    similarity_matrix = KNNBasic(sim_options={
        'name': 'cosine',
        'user_based': False
    }) \
        .fit(trainset) \
        .compute_similarities()

    test_subject = '500'

    k = 1

    test_subject_iid = trainset.to_inner_uid(test_subject)
    test_subject_ratings = trainset.ur[test_subject_iid]
    k_neighbors = heapq.nlargest(k, test_subject_ratings, key=lambda t: t[1])

    candidates = defaultdict(float)

    for itemID, rating in k_neighbors:
        try:
            similaritities = similarity_matrix[itemID]
            for innerID, score in enumerate(similaritities):
                candidates[innerID] += score * (rating / 5.0)
        except:
            continue

    def getRestaurantName(RestaurantID):
        if int(RestaurantID) in restaurantID_to_name:
            return restaurantID_to_name[int(RestaurantID)]
        else:
            return ""

    visited = {}
    for itemID, rating in trainset.ur[test_subject_iid]:
        visited[itemID] = 1
        recommendations = []

        position = 0
        for itemID, rating_sum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
            if not itemID in visited:
                recommendations.append(getRestaurantName(trainset.to_raw_iid(itemID)))
                position += 1
                if (position > 10): break  # We only want top 10

        for rec in recommendations:
            print("Restaurant: ", rec)

    return redirect('index')
