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


def generate_recommendation(user_id, model, metadata, thresh=3.5):
    """
    Generates a book recommendation for a user based on a rating threshold. Only
    books with a predicted rating at or above the threshold will be recommended
    """

    restaurant_names = list(metadata['nom'].values)
    random.shuffle(restaurant_names)

    for restaurant_name in restaurant_names:
        rating = predict_review(user_id, restaurant_name, model, metadata)
        if rating >= thresh:
            restaurant_id = get_restaurant_id(restaurant_name, metadata)
            return get_restaurant_info(restaurant_id, metadata)


def algoRecommandationGroupe(groupe, model, metadata, taille=10):
    restaurant_names = list(metadata['nom'].values)
    liste_recommandations = []
    liste_length = 0

    for restaurant_name in restaurant_names:
        moyenne = 0
        for people in groupe.liste_adherants.all():
            moyenne += predict_review(people.pk, restaurant_name, model, metadata)

        moyenne = moyenne/(groupe.liste_adherants.all().count())
        if moyenne > 4.5:
            liste_recommandations.append((restaurant_name, moyenne))
            liste_length+=1
            if liste_length == taille:
                return liste_recommandations
    return liste_recommandations


def algoRecommandationIndividuelle_v3(user_id, model, metadata, taille=10):
    restaurant_names = list(metadata['nom'].values)
    liste = []

    # Pour prendre les elements dans une liste de 10 max
    for restaurant_name in restaurant_names[:taille]:
        rating = predict_review(user_id, restaurant_name, model, metadata)
        liste = ajoutDebutListe(liste,restaurant_name, rating,taille)
    min = liste[taille-1][1]
    # on fait commencer le min à minimum 4.5
    if (min < 4.5):
        min = 4.5

    st = time.time()
    for restaurant_name in restaurant_names[taille:]:
        rating = predict_review(user_id, restaurant_name, model, metadata)
        if rating > min:
            liste = ajoutList(liste, restaurant_name, rating, taille)
            min = liste[taille-1][1]
    print(time.time() - st)
    return liste[:taille]


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


def listeRecommandationIndividuelle(user_id, taille=10):
    start = time.time()
    ratings_data = pd.read_csv('./ratings.csv')
    restaurant_metadata = pd.read_csv('./restaurant.csv', delimiter=';', engine='python')
    reader = Reader(rating_scale=(0, 5))
    data = Dataset.load_from_df(ratings_data[['user_id', 'restaurant_id', 'note']], reader)
    trainset, testset = train_test_split(data, test_size=0.20)
    svd = SVD(verbose=False, n_epochs=23, n_factors=7)
    predictions = svd.fit(trainset).test(testset)
    accuracy.rmse(predictions)
    #print(time.time() - start)
    l = algoRecommandationIndividuelle(user_id, svd, restaurant_metadata, taille)
    liste_complete = []
    for elem in l:
        liste_complete.append(get_restaurant_id(elem[0],restaurant_metadata))
    return liste_complete
    #print(time.time() - start)