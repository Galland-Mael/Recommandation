from .models import *

NB_CARROUSEL = 10

def liste_carrousel(type):
    """ Renvoie les meilleurs restaurants selon le type de restaurant donné en paramètres,
    si il n'y pas de filtre, le paramètre d'entrée est la chaine "tous"

    @param type: le type de restaurant recherché
    @type type : str
    @return: les meilleurs restaurants selon le filtre
    """
    if type != "tous":
        type_restaurant = RestaurantType.objects.filter(nom=type.lower())  # on stock le type de restaurant correspondant au filtre
        if type_restaurant.count() == 0: # si il n'y a pas de type avec ce nom on arête la fonction
            return []
        restaurant = Restaurant.objects.filter(type=type_restaurant[0]).order_by('-note')[:NB_CARROUSEL]
    else:
        restaurant = Restaurant.objects.order_by('-note')[:NB_CARROUSEL]
    return restaurant