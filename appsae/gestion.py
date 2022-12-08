
from appsae.model.models import *
from django.db.models import Avg

NB_CARROUSEL = 10
def carrousel():
    restaurant = Restaurant.objects.order_by('-note');
    list = [];
    for i in range(10):
        list.append(restaurant[i]);
    return list;

def connect(request,context):
    if 'mailUser' in request.session:
        user = Adherant.objects.get(mail=request.session['mailUser'])
        context['mail'] = request.session['mailUser']
        context['photo'] = user.profile_picture.url
    return context
def randomValue():
    ''' Fonction qui renvoie une chaîne composée de 6 caractères entre 0 et 9 '''
    value_random = ""
    for i in range(6):
        value_random += str(random.randint(0, 9))
        print(value_random);
    return value_random

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


def update_note_moyenne_restaurant(nomRestaurant):
    """ Fonction de mise à jour de la note moyenne d'un restaurant passé en paramètres

    @param nomRestaurant: le nom du restaurant
    @return: /
    """
    restaurant = Restaurant.objects.filter(nom=nomRestaurant)
    if restaurant.count() != 0:
        note = Avis.objects.filter(restaurant=restaurant[0]).aggregate(Avg("note"))
        Restaurant.objects.filter(nom=nomRestaurant).update(note=note['note__avg'])

def liste_avis(restaurant, num = 0):
    """ Fonction pour renvoyer une liste d'avis 10 par 10,
    si num vaut 0, on renvoie de 0 à 9 dans la liste des avis, etc...

    @param restaurant: le restaurant où chercher les avis
    @param num: le numero de la liste
    @return:
    """
    avis = Avis.objects.filter(restaurant_fk=restaurant)
    taille = avis.count()
    taille_liste= 10 # Taille de la liste à prendre
    if taille < num*taille_liste:
        return []
    elif taille >= (num + 1) *taille_liste:
        return avis[num*taille_liste:(num + 1)*taille_liste]
    elif taille < (num +1 ) *taille_liste:
        return avis[num*taille_liste:taille]