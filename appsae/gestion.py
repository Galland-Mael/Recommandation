from .models import *
import numpy as np

NB_CARROUSEL = 10

def liste_carrousel(type):
    """ Renvoie les meilleurs restaurants selon le type donné de restaurant donné en paramètres,
    si il n'y pas de filtre, le paramètre d'entrée est une chaine vide.

    @param type: le type de restaurant recherché
    @type type : str
    @return: les meilleurs restaurants selon le filtre
    """
    #for i in range(1000):
    #print(levenshtein("mc", "mcdonald's"))
    #print(str(levenshtein("Lorem ipsum dolor sit amet", "Laram zpsam dilir siy amot")))
    #print(levenshtein("Lorem ipsum dfezinfuezngolor sit amet", "Laram zpsam dilir siy amot"))
    list = []  # la liste des restaurants qui sera renvoyée
    if type != "tous":
        type_restaurant = RestaurantType.objects.filter(nom=type.lower())  # on stock le type de restaurant correspondant au filtre
        if type_restaurant.count() == 0: # si il n'y a pas de type avec ce nom on arête la fonction
            return list
        restaurant = Restaurant.objects.filter(type=type_restaurant[0]).order_by('-note')
    else:
        restaurant = Restaurant.objects.order_by('-note')
    i = 0  # le compteur de la boucle
    taille = restaurant.count()  # le nombre de restaurants renvoyés par la requête de recherche
    while i < NB_CARROUSEL and i < taille:
        list.append(restaurant[i])
        i = i+1
    return list

def recherche(type_restaurant, ville):
    list = []  # la liste des restaurants qui sera renvoyée
    if ville != "" and type_restaurant != "":
        restaurant = Restaurant.objects.filter(ville=ville, type="français").order_by('-note')
    elif ville != "":
        restaurant = Restaurant.objects.filter(ville=ville).order_by('-note')
    elif type_restaurant != "":
        restaurant = Restaurant.objects.filter(type="français").order_by('-note')
    i = 0  # le compteur de la boucle
    taille = restaurant.count()  # le nombre de restaurants renvoyés par la requête de recherche
    while i < taille:
        list.append(restaurant[i])
        i = i + 1
    return list

def levenshtein(chaine1, chaine2):
    taille_chaine1 = len(chaine1) + 1
    taille_chaine2 = len(chaine2) + 1
    levenshtein_matrix = np.zeros ((taille_chaine1, taille_chaine2))
    for x in range(taille_chaine1):
        levenshtein_matrix [x, 0] = x
    for y in range(taille_chaine2):
        levenshtein_matrix [0, y] = y
    for x in range(1, taille_chaine1):
        for y in range(1, taille_chaine2):
            if chaine1[x-1] == chaine2[y-1]:
                levenshtein_matrix [x,y] = min(
                    levenshtein_matrix[x-1, y] + 1,
                    levenshtein_matrix[x-1, y-1],
                    levenshtein_matrix[x, y-1] + 1)
            else:
                levenshtein_matrix [x,y] = min(
                    levenshtein_matrix[x-1,y] + 1,
                    levenshtein_matrix[x-1,y-1] + 1,
                    levenshtein_matrix[x,y-1] + 1)
    return (levenshtein_matrix[taille_chaine1 - 1, taille_chaine2 - 1])