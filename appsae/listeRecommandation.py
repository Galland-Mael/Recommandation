import time

import pandas as pd
from .svd import*
from .models import Adherant


def suppEspace(mot):
    """ Supprime les espaces dans le mot entré en paramètres

    @param mot: le mot où il faut supprimer les espaces
    @return: le mot entré en paramètres sans espaces
    """
    nouveau_mot = ""
    for lettre in mot:
        if lettre in "azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN0123456789":
            nouveau_mot += lettre
    return nouveau_mot


def tupleToList(liste_algo, restaurant_metadata):
    """ Renvoie la liste des id de chaques restaurants présents dans la liste de tuples donnés en paramètres

    @param liste_algo: liste de tuples sous la forme (resto_name, prediction)
    @param restaurant_metadata: les restaurants de la ville de l'utilisateur
    @return: une liste d'id de restaurants
    """
    liste_complete = []
    for element in liste_algo:
        liste_complete.append(element[0])
    return liste_complete


def listeRecommandationIndividuelle(user, taille=10):
    """ Construit une liste de recommandations pour l'utilisateur entré en paramètres

    @param user: l'utilisateur
    @param taille: la taille de la liste à renvoyer
    @return: une liste d'id de restaurants
    """
    st = time.time()
    chemin_accces = './csv/restaurant_' + suppEspace(user.ville) + '.csv'
    restaurant_metadata = pd.read_csv(chemin_accces, delimiter=';', engine='python')
    tuples = algoRecommandationIndividuelleComplet(user.pk, svdAlgo(), restaurant_metadata, taille)
    # tuples = algoRecommandationIndividuelleRapide(user.pk, svdAlgo(), restaurant_metadata, taille)
    return tupleToList(tuples, restaurant_metadata)


def listeRecommandationGroupe(groupe, taille=15):
    """ Construit une liste de recommandations pour le groupe entré en paramètres

    @param groupe: le groupe
    @param taille: la taille de la liste à renvoyer
    @return: une liste d'id de restaurants
    """
    st = time.time()
    user = Adherant.objects.get(pk=groupe.id_gerant)
    chemin_accces = './csv/restaurant_' + suppEspace(user.ville) + '.csv'
    restaurant_metadata = pd.read_csv(chemin_accces, delimiter=';', engine='python')
    tuples = algoRecommandationGroupeComplet(groupe, svdAlgo(), restaurant_metadata, taille)
    # tuples = algoRecommandationGroupeRapide(groupe, svdAlgo(), restaurant_metadata, taille)
    return tupleToList(tuples, restaurant_metadata)
