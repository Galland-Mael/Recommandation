import difflib
import pandas as pd
from time import time
from surprise import Reader, Dataset, SVD
from surprise.model_selection import train_test_split
from .models import *
from random import shuffle
from math import ceil


def get_restaurant_id(restaurant_name, metadata):
    """ Récupère l'id du restaurant à partir de son nom entré en paramètres

    @param restaurant_name: le nom du restaurant
    @param metadata: le fichier contenant les restaurants de la ville du groupe
    @return: l'id du restaurant
    """
    existing_names = list(metadata['nom'].values)
    closest_names = difflib.get_close_matches(restaurant_name, existing_names)
    restaurant_id = metadata[metadata['nom'] == closest_names[0]]['id'].values[0]
    return restaurant_id


def predict_review(user_id, restaurant_name, model, metadata):
    """ Prédit la note de l'utilisateur sur le restaurant entré en paramètres

    @param user_id: l'id de l'utilisateur
    @param restaurant_name: le nom du restaurant
    @param model: le model de données (svd) pour faire des prédictions
    @param metadata: le fichier contenant les restaurants de la ville du groupe
    @return: la prédiction pour l'utilisateur sur le restaurant
    """
    restaurant_id = get_restaurant_id(restaurant_name, metadata)
    review_prediction = model.predict(uid=user_id, iid=restaurant_id)
    return review_prediction.est


def predict_review_id(user_id, restaurant_id, model):
    return model.predict(uid=user_id, iid=restaurant_id).est


def svdAlgo():
    """ Construction de l'algorithme de recommandation SVD

    @return: le modèle SVD construit
    """
    ratings_data = pd.read_csv('./ratings.csv')
    reader = Reader(rating_scale=(0, 5))
    data = Dataset.load_from_df(ratings_data[['user_id', 'restaurant_id', 'note']], reader)
    trainset, testset = train_test_split(data, test_size=0.20)
    svd = SVD(verbose=False, n_epochs=23, n_factors=7)
    svd.fit(trainset).test(testset)
    return svd


def retirerRestaurantAvecNote(liste_user, metadata):
    restaurants_id = list(metadata['id'].values)
    restaurants_notes_id = Avis.objects.filter(adherant_fk__in=liste_user).values_list('restaurant_fk', flat=True)
    for elem in restaurants_notes_id:
        if elem in restaurants_id:
            restaurants_id.remove(elem)
    return restaurants_id


def algoRecommandationGroupeComplet(groupe, model, metadata, taille=15):
    start = time.time()
    # Initialisation de la liste des restaurants
    liste_restaurants = []

    # Initialisation de la liste des adherents du groupe
    liste_adherents = groupe.liste_adherants.all()

    # Récupération de la liste des noms de restaurants mélangé au hasard et de la taille de cette liste
    restaurants_id = retirerRestaurantAvecNote(liste_adherents, metadata)
    taille_liste_resto = len(restaurants_id)

    # Initialisation de la variable de prise en compte des prédictions individuelles (de 2.5 à 3.75)
    taille_ajout = min(2.5 + (ceil(taille_liste_resto / 1000) - 1) * 2.5 / 10, 3.75)

    for restaurant_id in restaurants_id:
        ajouter = True
        moyenne = 0
        for people in liste_adherents:
            note = predict_review_id(people.pk, restaurant_id, model)
            # Si la note de cet utilisateur n'est pas "bonne", on ne prend pas le restaurant
            if note <= taille_ajout:
                ajouter = False
                break
            moyenne += note  # ajout de la prédiction de l'utilisateur à la moyenne
        moyenne = moyenne/(len(liste_adherents))
        if ajouter:
            liste_restaurants = ajoutValeur(liste_restaurants, restaurant_id, moyenne, taille)

    print("TEMPS TRI : " + str(time.time() - start))
    return liste_restaurants


def algoRecommandationGroupeRapide(groupe, model, metadata, taille=15):
    # Initialisation du temps de départ au temps actuel, des différentes listes à [] et des tailles de listes à 0
    start = time.time()
    liste_one, liste_two, liste_three, liste_last = [], [], [], []
    liste_1_len, liste_2_len, liste_3_len = 0, 0, 0

    # Initialisation de la liste des adherents du groupe
    liste_adherents = groupe.liste_adherants.all()

    # Récupération de la liste des noms de restaurants mélangé au hasard et de la taille de cette liste
    restaurants_id = retirerRestaurantAvecNote(liste_adherents, metadata)
    shuffle(restaurants_id)
    taille_liste_resto = len(restaurants_id)

    # Initialisation de la variable de prise en compte des prédictions individuelles (de 2.5 à 3.75)
    taille_ajout = min(2.5 + (ceil(taille_liste_resto / 1000) - 1) * 2.5 / 10, 3.75)
    compteur = 0

    # Parcours de chaque restaurant jusqu'à avoir assez de restaurants "intéressants" à retourner
    for restaurant_id in restaurants_id:
        compteur += 1
        moyenne = 0
        ajouter = True
        # Prédit les notes de chaque utilisateurs du groupe sur le restaurant
        for people in liste_adherents:
            note = predict_review_id(people.pk, restaurant_id, model)
            # Si la note de cet utilisateur n'est pas "bonne", on ne prend pas le restaurant
            if note <= taille_ajout:
                ajouter = False
                break
            moyenne += note  # ajout de la prédiction de l'utilisateur à la moyenne

        # Si les prédictions de chaque utilisateur sont au dessus du taux minimum
        if ajouter:
            moyenne = round(moyenne / (liste_adherents.count()), 5)
            if moyenne >= 3.5:
                if moyenne >= 4.35:
                    liste_1_len += 1
                    liste_one.append((restaurant_id, moyenne))
                    # Si la première liste fait la bonne taille, on arête l'algorithme
                    if liste_1_len == taille:
                        print("TEMPS TRI : " + str(time.time() - start))
                        return liste_one
                elif moyenne >= 4.25:
                    liste_2_len += 1
                    liste_two = ajoutValeur(liste_two, restaurant_id, moyenne, taille - liste_1_len)
                elif liste_1_len + liste_2_len < taille and moyenne >= 4.05:
                    liste_3_len += 1
                    liste_three = ajoutValeur(liste_three, restaurant_id, moyenne, taille - liste_1_len - liste_2_len)
                elif liste_2_len + liste_1_len + liste_3_len < taille:
                    liste_last = ajoutValeur(liste_last, restaurant_id, moyenne, taille - liste_1_len - liste_2_len -
                                             liste_3_len)

            # Si l'algorithme est lancé depuis plus de 20 secondes
            if time.time() - start > 20:
                # S'il y a assez de restaurants avec une note supérieur à 4.25 ou si l'algo est lancé depuis plus
                # de 30 secondes et qu'il y a assez de restaurants avec une note supérieur à 4.05, on arête l'algo
                if liste_1_len + liste_2_len >= taille \
                        or (time.time() - start > 30 and liste_1_len + liste_2_len + liste_3_len >= taille):
                    break

    liste_one = liste_one + liste_two + liste_three + liste_last
    print("TEMPS TRI : " + str(time.time() - start))
    return liste_one[:taille]


def algoRecommandationIndividuelleComplet(user_id, model, metadata, taille=10):
    start = time.time()
    # Initialisation de la liste des restaurants
    liste_restaurants = []

    # Récupération de la liste des id de restaurants et de la taille de cette liste
    restaurants_id = retirerRestaurantAvecNote([user_id], metadata)
    taille_liste_resto = len(restaurants_id)

    for restaurant_id in restaurants_id:
        note = predict_review_id(user_id, restaurant_id, model)
        # Si la note de cet utilisateur n'est pas "bonne", on ne prend pas le restaurant
        liste_restaurants = ajoutValeur(liste_restaurants, restaurant_id, note, taille)

    print("TEMPS TRI : " + str(time.time() - start))
    return liste_restaurants


def algoRecommandationIndividuelleRapide(user_id, model, metadata, taille=10):
    # Initialisation du temps de départ au temps actuel, des différentes listes à [] et des tailles de listes à 0
    start = time.time()
    liste_one, liste_two, liste_three, liste_last = [], [], [], []
    liste_1_len, liste_2_len, liste_3_len = 0, 0, 0

    # Récupération de la liste des noms de restaurants mélangé au hasard et de la taille de cette liste
    restaurants_id = retirerRestaurantAvecNote([user_id], metadata)
    shuffle(restaurants_id)
    taille_liste_resto = len(restaurants_id)

    for restaurant_id in restaurants_id:
        note = predict_review_id(user_id, restaurant_id, model)
        if note >= 3.75:
            if note >= 4.55:
                liste_1_len += 1
                liste_one.append((restaurant_id, note))
                if liste_1_len == taille:
                    return liste_one
            elif note >= 4.45:
                liste_2_len += 1
                liste_two = ajoutValeur(liste_two, restaurant_id, note, taille - liste_1_len)
            elif liste_1_len + liste_2_len < taille and note >= 4.25:
                liste_3_len += 1
                liste_three = ajoutValeur(liste_three, restaurant_id, note, taille - liste_1_len - liste_2_len)
            elif liste_1_len + liste_2_len + liste_3_len < taille:
                liste_last = ajoutValeur(liste_last, restaurant_id, note, taille - liste_1_len - liste_2_len -
                                         liste_3_len)

        # Si l'algorithme est lancé depuis plus de 20 secondes
        if time.time() - start > 10:
            # S'il y a assez de restaurants avec une note supérieur à 4.25 ou si l'algo est lancé depuis plus
            # de 30 secondes et qu'il y a assez de restaurants avec une note supérieur à 4.05, on arête l'algo
            if liste_1_len + liste_2_len >= taille \
                    or (time.time() - start > 15 and liste_1_len + liste_2_len + liste_3_len >= taille):
                break

    liste_one = liste_one + liste_two + liste_three + liste_last
    print("TEMPS TRI : " + str(time.time() - start))
    return liste_one[:taille]


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
    inserer = False

    # Parcours tous les élément de la liste list et compare leur prédiction à la nouvelle prédicition
    for i in range(taille):
        # Si la nouvelle prédiction est supérieure à la prédiction de la liste, on ajoute le tuple (resto_name,
        # prediction) à la liste avant l'élément actuel
        if list[i][1] < prediction:
            list.insert(i, (resto_name, prediction))
            inserer = True
            break

    # Si l'élément n'a pas été inséré, alors on l'ajoute à la fin de la liste
    if not inserer:
        list.insert(taille, (resto_name, prediction))

    return list[:taille_max] # On ne retourne que taille_max tuples de (restaurant, note)
