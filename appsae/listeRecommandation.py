import difflib
import pandas as pd
from .svd import *


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
        liste_complete.append(get_restaurant_id(element[0], restaurant_metadata))
    return liste_complete


def listeRecommandationIndividuelle(user, taille=10):
    """ Construit une liste de recommandations pour l'utilisateur entré en paramètres

    @param user: l'utilisateur
    @param taille: la taille de la liste à renvoyer
    @return: une liste d'id de restaurants
    """
    restaurant_metadata = pd.read_csv('./restaurant_' + suppEspace(user.ville) + '.csv', delimiter=';', engine='python')
    tuples = algoRecommandationIndividuelleV3(user.pk, svdAlgo(), restaurant_metadata, taille)
    return tupleToList(tuples, restaurant_metadata)


def listeRecommandationGroupe(groupe, taille=15):
    """ Construit une liste de recommandations pour le groupe entré en paramètres

    @param groupe: le groupe
    @param taille: la taille de la liste à renvoyer
    @return: une liste d'id de restaurants
    """
    user = Adherant.objects.get(pk=groupe.id_gerant)
    restaurant_metadata = pd.read_csv('./restaurant_' + suppEspace(user.ville) + '.csv', delimiter=';', engine='python')
    tuples = algoRecommandationGroupe(groupe, svdAlgo(), restaurant_metadata, taille)
    return tupleToList(tuples, restaurant_metadata)
