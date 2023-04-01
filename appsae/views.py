import _thread
import json
import os.path
import sqlite3
import csv
import hashlib
from sqlite3 import OperationalError
import os, tempfile, zipfile, mimetypes
from wsgiref.util import FileWrapper

from celery.result import AsyncResult
from django.conf import settings
from django.utils.dateformat import format
from surprise import KNNBasic
from surprise import Dataset
from surprise import Reader
from django.conf import settings
from collections import defaultdict
from operator import itemgetter
import heapq
import hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import chart_studio.plotly as py
from surprise import accuracy, SVD
from surprise.model_selection import train_test_split
from surprise.model_selection import cross_validate
import chart_studio
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

from .recommandation_groupe import recommandationGroupeAvisGroupeComplet
from .recommendation import *
from .gestion import *
from .gestion_note import *
from .gestion_utilisateur import *
from .gestion_groupes import *
import re
from .gestion_note import *
from .svd import *
from .models import *
# from .generateDoc import *
# from .ajoutRecoBd import ajoutBDRecommandationGroupe
from .ajoutRecoBd import ajoutBDRecommandationGroupe
from django.conf import settings
import datetime
import time
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
import hashlib
from random import sample

PAGE = 0


def modifPAGE():
    global PAGE
    PAGE += 1


def pageVerifMail(request):
    """Fonction qui permet de créer un formulaire pour verifier le mail"""
    if Adherant.objects.filter(mail=request.session['registerMail']).count() != 0:
        messages.error(request, _('Il y a déjà un compte associé à cette adresse mail'))
        return redirect('register')
    return render(request, 'user/pageVerifMail.html')


def verifMail(request):
    """
    Fonction qui créer un utilisateur après avoir validé son email
    @param request:
    @return:
    """
    if (request.session['code'] == request.POST['code']):
        user = Adherant.objects.create(
            prenom=request.session['registerPrenom'],
            nom=request.session['registerNom'],
            ville=request.session['registerVille'],
            mail=request.session['registerMail'],
            birthDate=request.session['registerBirthDate'],
            password=request.session['registerPassword'],
        )
        user.save()
        request.session['mailUser'] = user.mail
        return redirect('index')
    else:
        messages.success(request, _('Mot de passe ou mail incorrect'))
        return redirect('pageVerifMail')


class NumbersStars:
    def __init__(self, nombre_virgule):
        self.nombre = nombre_virgule + 0.5
        self.nombre_virgule = nombre_virgule


class RestaurantInfo:
    def __init__(self, restaurant):
        self.pk = restaurant.pk
        self.note = restaurant.note
        self.nb_review = restaurant.nb_review
        self.name = setNomRestaurant(restaurant.nom)
        self.image_front = restaurant.image_front
        self.types = setTypesRestaurant(restaurant.type.all())


def setNomRestaurant(nom):
    if len(nom) > 24:
        if len(nom) < 27:
            return nom
        else:
            return nom[:24] + "..."
    return nom


def setTypesRestaurant(types):
    taille_actuelle = 0
    return_types = "";
    for indice, type in enumerate(types):
        taille_actuelle += len(type.nom) + 3
        if taille_actuelle < 26:
            if indice != 0:
                return_types += " | "
            return_types += str(type.nom[0].upper()) + str(type.nom[1:])
    return return_types


def index(request):
    """
    Fonction qui permet de faire le template de la page d'index
    @param request:
    @return:
    """
    list = ["bars", "american (traditional)", "pizza", "fast food", "breakfast & brunch", "american (new)", "burgers",
            "mexican", "italian", "coffee & tea"]
    if 'groupe' in request.session:
        del request.session['groupe']
    if 'nomGroupe' in request.session:
        del request.session['nomGroupe']
    context = {
        'list_etoiles_virgules': [NumbersStars(0.5), NumbersStars(1.5), NumbersStars(2.5),
                                                NumbersStars(3.5), NumbersStars(4.5)]
    }
    if 'mailUser' in request.session:
        user = Adherant.objects.get(mail=request.session['mailUser'])
        context['meilleurRestaurants'] = [RestaurantInfo(elem) for elem in listeAffichageCarrouselVilles(user.ville)]
        context['italian'] = [RestaurantInfo(elem) for elem in listeAffichageCarrouselVilles(user.ville, "Italian")]
        reco = RecommandationUser.objects.filter(adherant_fk=user.pk)
        if reco.count() != 0:
            recommandations = reco[0].recommandation.all()
            context['recommandation'] = recommandations
            context['reco'] = [RestaurantInfo(elem) for elem in recommandations]
        restaurants_sans_note = Restaurant.objects.filter(nb_review=0, ville=user.ville)
        liste_restaurants_sans_note = []
        if user.nb_review >= NB_CARROUSEL:
            context['visites'] = [RestaurantInfo(elem) for elem in listeAffichageDejaVisiter(user.pk)]
        if restaurants_sans_note.count() >= NB_CARROUSEL:
            for restaurant in restaurants_sans_note:
                liste_restaurants_sans_note.append(restaurant)
            context['restaurants_sans_note'] = [RestaurantInfo(elem) for elem in
                                                random.sample(liste_restaurants_sans_note, NB_CARROUSEL)]
    else:
        context['meilleurRestaurants'] = [RestaurantInfo(elem) for elem in listeAffichageCarrouselVilles()]
        context['italian'] = [RestaurantInfo(elem) for elem in listeAffichageCaroussel("Italian")]
    connect(request, context)
    return render(request, 'index/index.html', context)


def deleteGroup(request, pk):
    """
    Fonction qui permet de supprimer un groupe
    @param request:
    @param pk pk du groupe:
    @return:
    """
    if 'mailUser' not in request.session:
        return redirect('index')
    groupe = Groupe.objects.get(pk=pk)
    suppressionGroupe(groupe)
    return redirect('groupe')

def deleteUser(request, pk):
    """
    fonction qui permet d'enlever un utilisateur d'un groupe
    @param request:
    @param pk pk du groupe:
    @return:
    """
    if 'mailUser' not in request.session:
        return redirect('index')
    groupe = Groupe.objects.get(pk=pk)
    user = Adherant.objects.get(mail=request.session['mailUser'])
    suppressionUtilisateur(user,groupe)
    return redirect('groupe')


def groupRecommandations(request, pk):
    """
    Fonction qui renvoit une liste de recommandation de restaurant
    @param request:
    @param pk pk du groupe:
    @return:
    """
    if 'mailUser' not in request.session:
        return redirect('index')
    user = Adherant.objects.get(mail=request.session['mailUser'])
    groupe = Groupe.objects.get(pk=pk)
    membres = groupe.liste_adherants.all()
    context = {
        'membres': membres,
        'groupe': groupe,
    }
    if groupe.id_gerant == user.pk:
        context['chef'] = True
    if 'mailUser' in request.session:
        if RecommandationGroupe.objects.filter(
                groupe_fk=groupe).count() != 0:
            context['recommandation'] = RecommandationGroupe.objects.get(
                groupe_fk=Groupe.objects.get(pk=pk)).recommandation.all()
    connect(request, context)
    return render(request, 'user/groupRecommandations.html', context)


def creationGroup(request):
    """
    Fonction qui permet de valider la création d'un groupe
    @param request:
    @return:
    """
    if 'mailUser' not in request.session:
        return redirect('index')
    if 'groupe' in request.session:
        del request.session['groupe']
    if 'nomGroupe' in request.session:
        del request.session['nomGroupe']
    context = {}
    connect(request, context)
    return render(request, 'user/creationGroup.html', context)


def search(request):
    """
    Fonciton qui permet de rechercher un utilisateur
    @param request:
    @return:
    """
    if request.GET["search"] != "":
        context = {
            'restaurants': Restaurant.objects.filter(nom__icontains=request.GET["search"]).order_by('-note')[:3]
        }
    elif request.GET["search"] == "":
        context = {
            'user': {}
        }
    return render(request, 'restaurants/searchRestaurants.html', context)


def testNomUTF(nom):
    """

    @param nom:
    @return:
    """
    list = "azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN0123456789&'-+/:,*#|!?°. "
    nouveau_nom = ""
    for lettre in nom:
        if lettre in list:
            nouveau_nom += lettre
        elif lettre in 'éèê':
            nouveau_nom += 'e'
        elif lettre in 'ÉÈ':
            nouveau_nom += 'E'
    return nouveau_nom


def supplettreUTF():
    """

    @return:
    """
    for resto in Restaurant.objects.all():
        nouveau_nom = testNomUTF(resto.nom)
        if (nouveau_nom != resto.nom):
            Restaurant.objects.filter(id_yelp=resto.id_yelp).update(nom=nouveau_nom)


def createGroupe(request):
    """
    Fonction qui permet de créer un groupe
    @param request:
    @return:
    """
    if 'mailUser' not in request.session:
        return redirect('index')
    if 'nomGroupe' not in request.POST:
        context = {}
        connect(request, context)
        return render(request, 'user/groupe.html', context)
    groupe = creationGroupe(request.POST['nomGroupe'], Adherant.objects.get(mail=request.session['mailUser']))
    user = Adherant.objects.get(mail=request.session['mailUser'])
    for user in Adherant.objects.filter(mail__in=request.session['groupe']):
        ajoutUtilisateurGroupe(user, groupe)
    ajoutBDRecommandationGroupe(groupe)
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
    return redirect('groupe')


def groupe(request):
    """
    Fonction qui permet d'afficher les donner d'un groupe
    @param request:
    @return:
    """
    if 'mailUser' not in request.session:
        return redirect('index')
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
    """
    Fonction qui permet d'enlever un utilisateurs d'un groupe lors de la création
    @param request:
    @param user utilisateur a enlever:
    @return:
    """
    if 'mailUser' not in request.session:
        return redirect('index')
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
    """
    Fonciton qui permet d'ajouter un utilisateur a un groupe"
    @param request:
    @param user utilisateur a ajouter aux groupes:
    @return:
    """
    if 'mailUser' not in request.session:
        return redirect('index')
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
    """
    Fonction qui permet de déterminer le noms du groupe
    @param request:
    @return:
    """
    if 'mailUser' not in request.session:
        return redirect('index')
    if 'groupe' not in request.session:
        return redirect('groupe')
    context = {
        'groupe': Adherant.objects.filter(mail__in=request.session['groupe']),
    }
    connect(request, context)
    return render(request, 'user/nomGroup.html', context)


def searchRestau(request):
    """
    fonction qui permet de rechercher un restaurant avec un le nom ou une filtres
    @param request:
    @return renvoie la liste des restaurans qui remplissent les critères:
    """
    type = RestaurantType.objects.filter(nom=request.POST["type"])
    search = request.POST["search"]
    if type == "" and search == "":
        return redirect(index)
    context = {}
    if request.POST["type"] == "":
        type = RestaurantType.objects.all()
    if search == "":
        search = ""
    if 'mailUser' in request.session:
        user = Adherant.objects.get(mail=request.session['mailUser'])
        context['list'] = Restaurant.objects.filter(nom__icontains=search, type__in=type, ville=user.ville)
    else:
        context['list'] = Restaurant.objects.filter(nom__icontains=search, type__in=type)
    if(context['list'].count()==0):
        return redirect('index')
    context = {
        'list': Restaurant.objects.filter(nom__icontains=request.POST["search"])
    }
    connect(request, context)
    return render(request, 'restaurants/searchRestau.html', context)


def groupePage(request):
    """
    Fonction qui affiche ous les groupes de l'utilisateur connecté
    @param request:
    @return:
    """
    if 'mailUser' not in request.session:
        return redirect('index')
    if 'groupe' in request.session:
        del request.session['groupe']
    context = {}
    connect(request, context)
    return render(request, 'user/createGroup.html', context)


def searchUser(request):
    """
    Fonction qui permet de renvoyer 3 utilisateur avec un système de recherche avec le mail des utilisateurs
    @param request:
    @return renvoie une list de trois utilisateur:
    """
    if 'mailUser' not in request.session:
        return redirect('index')
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
    """
    Fonction qui permet d'afficher toutes les informations sur un restaurant passer en paramètre
    @param request:
    @param pk pk du restaurant:
    @return:
    """
    img = Restaurant.objects.get(pk=pk).img.all()
    restaurant = Restaurant.objects.get(pk=pk)
    context = {
        'restaurant': restaurant,
        'imgRestaurants': ImageRestaurant.objects.filter(pk__in=restaurant.img.all()),
        'nbAvis': Avis.objects.filter(restaurant_fk=restaurant),
        'list_etoiles_virgules': [NumbersStars(0.5), NumbersStars(1.5), NumbersStars(2.5),
                         NumbersStars(3.5), NumbersStars(4.5)]
    }
    if 'mailUser' in request.session:
        user = Adherant.objects.get(mail=request.session['mailUser'])
        if avisExist(user, restaurant):
            avisUser = Avis.objects.filter(restaurant_fk=restaurant, adherant_fk=user)
            list_avis = Avis.objects.filter(restaurant_fk=restaurant).all().exclude(adherant_fk=user)[:9]
        else:
            list_avis = Avis.objects.filter(restaurant_fk=restaurant).all()[:10]
    else:
        list_avis = Avis.objects.filter(restaurant_fk=restaurant).all()[:10]
    context["avis"] = list_avis
    if 'mailUser' in request.session:
        user = Adherant.objects.get(mail=request.session['mailUser'])
        if Avis.objects.filter(adherant_fk=user, restaurant_fk=Restaurant.objects.get(pk=pk)):
            context['commentaire'] = True
        if avisExist(user, restaurant):
            context['avisUser'] = avisUser[0]
    connect(request, context)
    return render(request, 'restaurants/vueRestaurant.html', context)


def addCommentaires(request, pk):
    """
    Fonctino qui permet à un utilisateur de mettre des avis sur des commentaires
    @param request:
    @param pk pk du restaurant:
    @return:
    """
    user = Adherant.objects.get(mail=request.session['mailUser'])
    restaurant = Restaurant.objects.filter(pk=pk)
    restaurants = Restaurant.objects.get(pk=pk)
    img = Restaurant.objects.get(pk=pk).img.all()
    if (avisExist(user, restaurant[0])):
        avisUser = Avis.objects.filter(restaurant_fk=restaurant[0], adherant_fk=user)
        list = Avis.objects.filter(restaurant_fk=restaurants).all().exclude(adherant_fk=user)[:9]
    else:
        list = Avis.objects.filter(restaurant_fk=restaurants).all()[:10]
    context = {
        'restaurant': restaurant[0],
        'imgRestaurants': ImageRestaurant.objects.filter(pk__in=img),
        'avis': list,
        'nbAvis': Avis.objects.filter(restaurant_fk=restaurants),
        'list_etoiles_virgules': [NumbersStars(0.5), NumbersStars(1.5), NumbersStars(2.5), NumbersStars(3.5),
                                  NumbersStars(4.5)]
    }
    if 'mailUser' in request.session:
        context['commentaire'] = True
    if (avisExist(user, restaurant[0])):
        context['avisUser'] = avisUser
    if (request.method == 'POST' and 'title-rating' in request.POST and 'comm' in request.POST):
        ajoutAvis(Adherant.objects.get(mail=request.session['mailUser']), Restaurant.objects.get(pk=pk),
                  request.POST['title-rating'], request.POST['comm'])
        if Avis.objects.get(adherant_fk=Adherant.objects.get(mail=request.session['mailUser']),
                            restaurant_fk=Restaurant.objects.get(pk=pk)) is not None:
            updateAvis(Adherant.objects.get(mail=request.session['mailUser']), Restaurant.objects.get(pk=pk),
                       request.POST['title-rating'], request.POST['comm'])
    else:
        messages.success(request, _('Les deux champs doivent être remplis.'))
    connect(request, context)
    return render(request, 'restaurants/vueRestaurant.html', context)


def voirPlus(request, pk):
    """
    Fontion qui permet d'afficher plus d'avis sur une restaurant
    @param request:
    @param pk pk du restaurant:
    @return:
    """
    context = {
        'avis': listeAffichageAvis(Restaurant.objects.get(pk=pk), 1),
    }
    if (afficherVoirPlus(Restaurant.objects.get(pk=pk), 1)):
        context['endAvis'] = True
    return render(request, 'avis/moreAvis.html', context)


def register(request):
    """
    Fonction qui permet de créer un utilisateurs
    @param request:
    @return:
    """
    if request.method == "POST":
        user = request.POST
        '''Remplissage de la base de données'''
        password = user['password']
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        request.session['registerPrenom'] = user['prenom']
        request.session['registerNom'] = user['nom']
        request.session['registerVille'] = user['ville']
        request.session['registerMail'] = user['mail']
        request.session['registerBirthDate'] = user['birthDate']
        request.session['registerPassword'] = hashed_password
        request.session['code'] = verificationEmail(user["mail"])
        return redirect('pageVerifMail')
    form = AdherantForm()
    context = {
        'form': form,
        'info': Adherant.objects.all
    }
    return render(request, 'user/register.html', context)
    # return JsonResponse({"form": list(form.values) })


def validate_form(form):
    name = form.get("name")
    email = form.get("email")
    message = form.get("message")
    captcha = form.get("g-recaptcha-response")

    # Check if captcha is checked
    if not captcha:
        return False, "Please complete the captcha"

    # Check if name, email, and message are not empty
    if not name or not email or not message:
        return False, "Please fill in all fields"

    # Check if email is valid
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Please enter a valid email address"

    return True, ""


def login(request):
    """
    Fontion qui effectue les verifications lors du login
    @param request:
    @return:
    """
    if request.method == "POST":
        info = Adherant.objects.all()
        contain = False
        for adherant in info:
            # Verification
            if request.POST['mail'] == adherant.mail:
                password = request.POST['password']
                hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
                if hashed_password == adherant.password:
                    contain = True
        if contain:
            user = Adherant.objects.get(mail=request.POST['mail'])
            # Création de la session ou je récupère que le mail de l'utilisateur
            request.session['mailUser'] = user.mail
            return redirect('index')
        else:
            messages.success(request, '*Wrong mail or password')
            return redirect('login')
    else:
        return render(request, 'user/login.html')


def modification(request):
    """
    Fonction qui recupère les données du form de modfiication de l'utilisateur et qui le modifie
    @param request:
    @return retourne sur la page index:
    """
    if 'mailUser' not in request.session:
        return redirect('index')
    user = Adherant.objects.get(mail=request.session['mailUser'])
    if request.POST['nom'] != '' and request.POST['nom'] != user.nom:
        updateNomUser(user.mail, request.POST['nom'])
    if request.POST['prenom'] != '' and request.POST['nom'] != user.prenom:
        updatePrenom(user.mail, request.POST['prenom'])
    if len(request.FILES) != 0:
        img = ImageUser.objects.create(
            img=request.FILES['photo']
        )
        img.save();
        updateProfilPick(user.mail, 'img_user/' + str(request.FILES['photo']))
    if (request.POST['ville'] != user.ville):
        Adherant.objects.filter(mail=user.mail).update(ville=request.POST['ville'])
        # if (user.nb_review >= 5):
        # majRecommandationsIndividuellesBD(user, RecommandationUser.objects.get(adherant_fk=user))
    context = {}
    if 'mailUser' in request.session:
        context['meilleurRestaurants'] = listeAffichageCarrouselVilles(user.ville)
        context['italian'] = listeAffichageCarrouselVilles(user.ville, "Italian")
        if RecommandationUser.objects.filter(
                adherant_fk=Adherant.objects.get(mail=request.session['mailUser'])).count() != 0:
            context['recommandation'] = RecommandationUser.objects.get(
                adherant_fk=Adherant.objects.get(mail=request.session['mailUser'])).recommandation.all()
    connect(request, context)
    return render(request, 'index/index.html', context)


def modifUser(request):
    """
    Fonction qui permet de renvoyer le template pour modifier son profil
    @param request:
    @return:
    """
    if 'mailUser' not in request.session:
        return redirect('index')
    context = {
        'user': Adherant.objects.get(mail=request.session['mailUser']),
    }
    connect(request, context)
    return render(request, 'user/modifUser.html', context)


def random_value():
    """
    Fonction qui renvoie une chaine de caractère avec 6 chiffres
    @return retourne la chaine de caractère:
    """
    value_random = ""
    for i in range(6):
        value_random += str(random.randint(0, 9))
    return value_random


def verificationEmail(mail):
    """
    Fonction qui envoie un mail avec un code
    @param mail:
    @return:
    """
    random = random_value()
    print('appeler')
    try:
        send_mail("Vérification de votre compte - Ne pas répondre",
                  "Code de vérification :\n"
                  + "         " + random
                  + "\n\nL'équipe EatAdvisor",
                  "eat_advisor2@outlook.fr",
                  [mail],
                  fail_silently=False);
        return random
    except:
        return HttpResponse("le mail na pas pu etre envoyer")


def logoutUser(request):
    """
    Fonction qui deconnecte un utilisateur
    @param request:
    @return redirect sur la view index:
    """
    try:
        del request.session['mailUser']
    except KeyError:
        pass
    try:
        del request.session['mailRestaurateur']
    except KeyError:
        pass
    try:
        del request.session['mailAdministrateur']
    except KeyError:
        pass
    return redirect('index')


def search(request):
    """
    Fonction qui renvoie des restaurants avec un système de recherche
    @param request:
    @return 3 restaurant:
    """
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


def printeur(ddd):
    for i in range(10):
        print(ddd)


def recommendation(request):
    st = time.time()
    groupe = Groupe.objects.get(nom_groupe="testAlgoGroupeMatteo2")
    liste = listeRecommandationGroupe(groupe)
    # person = Adherant.objects.get(mail="matteo.miguelez@gmail.com")
    #liste = listeRecommandationIndividuelle(person)
    print(liste)
    print(time.time() - st)
    return HttpResponse('')


def export_restaurant(request):
    '''
    exporte l'ensemble des restaurants dans des fichiers csv séparés en fonction de leur ville
    @param request:
    @return:
    '''
    listVilles = ["Philadelphia", "Tampa", "Indianapolis", "Nashville", "Tucson", "New Orleans", "Edmonton",
                  "Saint Louis", "Reno",
                  "Saint Petersburg", "Boise", "Santa Barbara", "Clearwater", "Wilmington", "St. Louis", "Metairie",
                  "Franklin"]
    # user = Adherant.objects.get(mail=request.session['mailUser'])
    for villes in listVilles:
        file = str(settings.BASEDIR) + '/' + "restaurant" + filterNomRestaurant(villes) + ".csv"
        f = open(file, "w")
        f.writelines("id;nom;genre")
        f.write('\n')
        for restaurant in Restaurant.objects.filter(ville=villes):
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
    """
    Exporte l'ensemble des ratings dans un fichier csv ratings.csv
    @param request:
    @return:
    """
    file = str(settings.BASE_DIR) + '/' + "ratings.csv"
    f = open(file, "w")
    f.writelines("user_id,restaurant_id,note")
    for rating in Avis.objects.all().values_list('adherant_fk', 'restaurant_fk', 'note'):
        f.write('\n')
        f.write(str(rating)[1:-1])
    print(file)
    return redirect('index')


def setImg(request):
    """
    Met des photos pour chaque restaurant avec des img set
    @param request:
    @return:
    """
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


def getFirstElement():
    liste = []
    fichier = open("C:/Users/alhdv/Downloads/patronymes.csv", "r")
    cr = csv.reader(fichier, delimiter=",")
    for row in cr:
        if " " not in str(row[0]):
            liste.append(row[0])
    fichier.close()
    return liste


def addAvis(request, pk):
    context = {
        'avis': liste_avis(Restaurant.objects.get(pk=pk), 1)
    }
    connect(request, context)
    return render(request, 'avis/moreAvis.html', context)

#
# def exportHTML():
#     """
#     Crée un ensemble de fichier html qui correspondent à la doc
#     @return:
#     """
#     generate_html_docs("C:\\Users\\antoi\\PycharmProjects\\SAE-Recommandation\\appsae",
#                        "C:\\Users\\antoi\\PycharmProjects\\SAE-Recommandation\\pydoc")
#
