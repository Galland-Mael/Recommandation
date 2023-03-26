from .models import *

NB_CARROUSEL = 8


def connect(request,context):
    if 'mailUser' in request.session:
        user = Adherant.objects.get(mail=request.session['mailUser'])
        context['mail'] = request.session['mailUser']
        context['photo'] = user.profile_picture.url
    elif 'mailRestaurateur' in request.session:
        restaurateur = Restaurateur.objects.get(mail=request.session['mailRestaurateur'])
        context['mailR'] = request.session['mailRestaurateur']
        context['profil_picture'] = restaurateur.profile_picture.url
    elif 'mailAdministrateur' in request.session:
        context['mailA'] = request.session['mailAdministrateur']
    return context


def listeAffichageCaroussel(type=""):
    """ Renvoie les meilleurs restaurants selon le type de restaurant donné en paramètres,
    si il n'y pas de filtre, le paramètre d'entrée est la chaine "", donnée par défaut

    @param type: le type de restaurant recherché
    @return: les meilleurs restaurants selon le filtre
    """
    if type != "":
        type_restaurant = RestaurantType.objects.filter(nom=type.lower())  # on stock le type de restaurant correspondant au filtre
        if type_restaurant.count() == 0: # si il n'y a pas de type avec ce nom on arête la fonction
            return []
        return Restaurant.objects.filter(type=type_restaurant[0]).order_by('-note')[:NB_CARROUSEL]
    return Restaurant.objects.order_by('-note')[:NB_CARROUSEL]


def listeAffichageCarrouselVilles(ville="", type=""):
    """ Renvoie les meilleurs restaurants selon le type de restaurant et la ville donnés en paramètres,
    s'il n'y a pas de de ville et de filtre, on renvoit les meilleurs restaurants de la base de données,
    s'il n'y a pas de ville mais un filtre, on renvoit les meilleurs restaurants de la base de données avec le filtre
    s'il y a une ville mais pas de filtre, on renvoit les meilleurs restaurants dans la ville donnée,
    s'il y a une ville et un filtre, on renvoit les meilleurs restaurants avec le filtre et dans la ville donnée

    @param ville: la ville concernée
    @param type: le type de restaurant recherché
    @return:
    """
    NB_MINIMUM = 10
    if type != "":
        type_restaurant = RestaurantType.objects.filter(nom=type.lower())  # on stock le type de restaurant correspondant au filtre
        if type_restaurant.count() == 0: # si il n'y a pas de type avec ce nom on arête la fonction
                return []

        if ville != "":
            meilleurs = Restaurant.objects.filter(ville=ville, type=type_restaurant[0], nb_review__gte=NB_MINIMUM).order_by('-note')
            if meilleurs.count() >= NB_CARROUSEL:
                return meilleurs[:NB_CARROUSEL]
            return Restaurant.objects.filter(ville=ville, type=type_restaurant[0]).order_by('-note')[:NB_CARROUSEL]
        else:
            meilleurs = Restaurant.objects.filter(type=type_restaurant[0], nb_review__gte=NB_MINIMUM).order_by('-note')
            if meilleurs.count() >= NB_CARROUSEL:
                return meilleurs[:NB_CARROUSEL]
            return Restaurant.objects.filter(type=type_restaurant[0]).order_by('-note')[:NB_CARROUSEL]
    if ville != "" and type == "":
        meilleurs = Restaurant.objects.filter(ville=ville, nb_review__gte=NB_MINIMUM).order_by('-note')
        if meilleurs.count() >= NB_CARROUSEL:
            return meilleurs[:NB_CARROUSEL]
        return Restaurant.objects.filter(ville=ville).order_by('-note')[:NB_CARROUSEL]
    meilleurs = Restaurant.objects.filter(nb_review__gte=NB_MINIMUM).order_by('-note')
    if meilleurs.count() >= NB_CARROUSEL:
        return meilleurs[:NB_CARROUSEL]
    return Restaurant.objects.order_by('-note')[:NB_CARROUSEL]


def listeAffichageDejaVisiter(user_id):
    """ Renvoie une liste de taille max NB_CARROUSEL contenant les restaurants que l'utilisateur
    a déjà noté, et qu'il a apprécié (note >= 3.5)

    @param user: l'utilisateur
    @return: une liste de restaurants
    """
    avis_bonnes_notes =  Avis.objects.filter(adherant_fk=user_id, note__gte=3.5).order_by("-note")[:NB_CARROUSEL]
    restaurant_visites = []
    if avis_bonnes_notes.count() < NB_CARROUSEL:
        return
    for element in avis_bonnes_notes:
        restaurant_visites.append(Restaurant.objects.get(pk=element.restaurant_fk.pk))
    return restaurant_visites