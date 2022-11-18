from .models import *

NB_CARROUSEL = 10

def liste_carrousel(type):
    """ Renvoie les meilleurs restaurants selon le type donné de restaurant donné en paramètres,
    si il n'y pas de filtre, le paramètre d'entrée est une chaine vide.

    @param type: le type de restaurant recherché
    @type type : str
    @return: les meilleurs restaurants selon le filtre
    """
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