import difflib
import random
import numpy as np
import pandas as pd
import os
import time
from surprise import Reader, Dataset, SVD, accuracy
from surprise.model_selection import train_test_split
from surprise.model_selection import cross_validate
from .models import *


def get_restaurant_id(restaurant_name, metadata):
    """
    Gets the book ID for a book title based on the closest match in the metadata dataframe.
    """

    existing_names = list(metadata['nom'].values)
    closest_names = difflib.get_close_matches(restaurant_name, existing_names)
    restaurant_id = metadata[metadata['nom'] == closest_names[0]]['id'].values[0]
    return restaurant_id


def get_restaurant_objects(restaurant_id):
    restaurant_objects = Restaurant.objects.filter(id__in=restaurant_id)
    return restaurant_objects


def get_restaurant_info(restaurant_id, metadata):
    """
    Returns some basic information about a book given the book id and the metadata dataframe.
    """

    restaurant_info = metadata[metadata['id'] == restaurant_id][['id', 'nom']]
    return restaurant_info.to_dict(orient='records')


def predict_review(user_id, restaurant_name, model, metadata):
    """
    Predicts the review (on a scale of 1-5) that a user would assign to a specific book.
    """

    restaurant_id = get_restaurant_id(restaurant_name, metadata)
    review_prediction = model.predict(uid=user_id, iid=restaurant_id)
    return review_prediction.est


def algoRecommandationGroupe(groupe, model, metadata, taille=10):
    st = time.time()
    restaurant_names = list(metadata['nom'].values)
    liste_recommandations, liste_secondaires, liste_tertiaire, liste_last = [], [], [], []
    liste_length, liste_secondaires_length, liste_tertiaire_length = 0, 0, 0
    cpt = 0

    for restaurant_name in restaurant_names:
        cpt+=1
        moyenne = 0
        for people in groupe.liste_adherants.all():
            moyenne += predict_review(people.pk, restaurant_name, model, metadata)

        moyenne = round(moyenne/(groupe.liste_adherants.all().count()),5)
        if moyenne >= 4.35:
            liste_recommandations.append((restaurant_name, round(moyenne,5)))
            liste_length+=1
            if liste_length == taille:
                print(cpt)
                print(time.time() - st)
                return liste_recommandations
        elif moyenne >= 4.25:
            liste_secondaires_length+=1
            liste_secondaires = ajoutValeur(liste_secondaires, restaurant_name, moyenne, taille - liste_length)
        elif moyenne >= 4.05:
            liste_tertiaire_length += 1
            liste_tertiaire = ajoutValeur(liste_tertiaire, restaurant_name, moyenne, taille - liste_length - liste_secondaires_length)
        elif liste_secondaires_length + liste_length < taille and moyenne >= 3.5:
            liste_last = ajoutValeur(liste_last, restaurant_name, moyenne, taille - liste_length - liste_secondaires_length)
        if time.time() - st > 20 and liste_length + liste_secondaires_length >= taille//1.2 and liste_tertiaire_length >= taille//5:
            break
    print(time.time() - st)
    print(cpt)
    liste_recommandations = liste_recommandations + liste_secondaires + liste_tertiaire + liste_last
    return liste_recommandations[:taille]


def testMatteo(groupe, model, metadata, taille=10):
    restaurant_names = list(metadata['nom'].values)
    cpt_total = 0
    cpt_45, cpt_4,cpt_3, cpt_2, cpt_1, cpt_0 = 0, 0, 0, 0, 0, 0
    for restaurant_name in restaurant_names:
        cpt_total+=1
        moyenne = 0
        #for people in groupe.liste_adherants.all():
            #moyenne += predict_review(people.pk, restaurant_name, model, metadata)

        #moyenne = round(moyenne/(groupe.liste_adherants.all().count()),5)
        moyenne = round(predict_review(groupe.liste_adherants.all()[0].pk, restaurant_name, model, metadata))
        if moyenne > 4.5: cpt_45 += 1
        elif moyenne > 4: cpt_4 += 1
        elif moyenne > 3: cpt_3 += 1
        elif moyenne > 2: cpt_2 += 1
        elif moyenne > 1: cpt_1 += 1
        elif moyenne > 0: cpt_0 += 1

        if cpt_total%500 == 0:
            print("total : " + str(cpt_total))
            print("cpt 0 : "+ str(cpt_0))
            print("cpt 1 : "+ str(cpt_1))
            print("cpt 2 : "+ str(cpt_2))
            print("cpt 3 : "+ str(cpt_3))
            print("cpt 4 : "+ str(cpt_4))
            print("cpt 4.5 : "+ str(cpt_45))
            print("---------------------------")
    print("total : " + str(cpt_total))
    print("cpt 0 : " + str(cpt_0))
    print("cpt 1 : " + str(cpt_1))
    print("cpt 2 : " + str(cpt_2))
    print("cpt 3 : " + str(cpt_3))
    print("cpt 4 : " + str(cpt_4))
    print("cpt 4.5 : " + str(cpt_45))
    print("---------------------------")


def algoRecommandationIndividuelle_v2(user_id, model, metadata,taille=10):
    restaurant_names = list(metadata['nom'].values)
    liste = []
    list_length = 0

    st = time.time()
    for restaurant_name in restaurant_names:
        rating = predict_review(user_id, restaurant_name, model, metadata)
        if rating > 4.5:
            liste.append((restaurant_name, rating))
            list_length+=1
            if (list_length == taille):
                return liste
    return liste


def algoRecommandationIndividuelle(user_id, model, metadata,taille=10):
    restaurant_names = list(metadata['nom'].values)
    liste = []
    list_length = 0

    # Pour prendre les elements dans une liste de 10 max
    for restaurant_name in restaurant_names[:taille]:
        rating = predict_review(user_id, restaurant_name, model, metadata)
        liste = ajoutDebutListe(liste, restaurant_name, rating, taille)
    min = liste[taille-1][1]
    # on fait commencer le min à minimum 4.5
    if (min < 4.5):
        min = 4.5

    for restaurant_name in restaurant_names[taille:]:
        rating = predict_review(user_id, restaurant_name, model, metadata)
        if rating > min:
            liste = ajoutList(liste,restaurant_name, rating, taille)
            min = liste[taille-1][1]
    return liste


def ajoutValeur(list, resto_name, prediction, taille_max=15):
    """ Ajout du tuple (resto_name, prediction) dans la liste list, triée dans l'odre croissant,
    la taille de la liste retournée sera forcément inférieure à taille_max

    @param list: la liste de départ
    @param resto_name: le nom du restaurant
    @param prediction: la note prédite
    @param taille_max: la taille maximum à renvoyer
    @return: une liste, triée par ordre croissant des prédictions sous la forme de tuple (resto_name, prediction)
    """
    taille = min(len(list), taille_max)
    test = False
    for i in range(taille):
        if list[i][1] < prediction:
            list.insert(i, (resto_name, prediction))
            test = True
            break
    if not test:
        list.insert(taille, (resto_name, prediction))
    return list[:taille_max]


def ajoutDebutListe(list,resto_name, prediction, taille_max=10):
    taille = len(list)
    return_list = []
    if (taille == 0):
        return_list.append((resto_name, prediction))
    else:
        i = 0
        while (list[i][1] > prediction and i!= taille - 1):
            return_list.append(list[i])
            i+=1
        return_list.append((resto_name, prediction))
        if i <= taille - 1:
            while(i!=taille):
                return_list.append(list[i])
                i+=1
    return return_list


def ajoutList(list, resto_name, prediction, taille=10):
    """ Ajoute le tuple (resto_name, prediction) dans la liste (de taille maximale 10), à l'endroit où la prédiction
    est inférieur au deuxieme élement du tuple

    @param list: la liste de tuples
    @param resto_name: le nom du restaurant à ajouter
    @param prediction: la prediction sur le restaurant à ajouter
    @return: la liste mise à jour
    """
    last = 0
    for i in range(taille):
        if (list[i][1] < prediction):
            tmp = list[i]
            list[i] = (resto_name, prediction)
            for j in range(i + 1, taille):
                next = list[j]
                list[j] = tmp
                tmp = next
            break
    return list