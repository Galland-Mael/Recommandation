from .models import *
from django.db.models import Avg


def updateNoteMoyenneRestaurant(restaurant):
    """ Fonction de mise à jour de la note moyenne d'un restaurant passé en paramètres

    @param nomRestaurant: le nom du restaurant
    @return: /
    """
    avis_resto = Avis.objects.filter(restaurant_fk=restaurant)
    if avis_resto.count() != 0:
        note = avis_resto.aggregate(Avg("note"))
        Restaurant.objects.filter(nom=restaurant.nom).update(note=round(note['note__avg'], 2))
    else:
        Restaurant.objects.filter(nom=restaurant.nom).update(note=-1)


def ajoutAvis(user, restaurant, note, avis):
    """ Fonction permettant d'ajouter une note et un avis
    @param user: l'utilisateur
    @param restaurant: le restaurant
    @return: /
    """
    ajout = Avis(note=note, texte=avis, restaurant_fk=restaurant, adherant_fk=user)
    ajout.save()
    updateNoteMoyenneRestaurant(restaurant)


def updateAvis(user, restaurant, note, avis):
    """ Mise à jour de le note (et l'avis) de l'utilisateur user pour le restaurant restaurant
    @param user: l'utilisateur
    @param restaurant: le restaurant
    @param note: la nouvelle note
    @param avis: le nouvel avis
    @return: /
    """
    Avis.objects.filter(restaurant_fk=restaurant, adherant_fk=user).update(note=note, texte=avis)
    updateNoteMoyenneRestaurant(restaurant)

def suppressionAvis(user, restaurant):
    """ Suppression de l'avis de l'utilisateur user sur le restaurant restaurant

    @param user: l'utilisateur
    @param restaurant: le restaurant
    @return: /
    """
    Avis.objects.get(restaurant_fk=restaurant, adherant_fk=user).delete()
    updateNoteMoyenneRestaurant(restaurant)

def supplettreUTF():
    """

    @return:
    """
    for resto in Restaurant.objects.all():
        nouveau_nom = testNomUTF(resto.nom)
        if (nouveau_nom != resto.nom):
            Restaurant.objects.filter(id_yelp=resto.id_yelp).update(nom=nouveau_nom)


def testNomUTF(nom):
    """

    @param nom:
    @return:
    """
    list = "azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN0123456789&'-_+/:,*²#|!?°. "
    nouveau_nom = ""
    for lettre in nom:
        if lettre in list:
            nouveau_nom += lettre
        elif lettre in 'éèê':
            nouveau_nom += 'e'
        elif lettre in 'ÉÈ':
            nouveau_nom += 'E'
    return nouveau_nom