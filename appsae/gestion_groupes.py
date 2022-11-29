from .models import *


def ajout_utilisateur(user, groupe):
    """ Ajout d'un utilisateur au groupe

    @param user: l'utilisateur à ajouter
    @param groupe : le groupe dans lequel ajouter l'utilisateur
    @return: /
    """
    groupe.add(user)


def suppression_utilisateur(user, groupe):
    """ Suppression d'un utilisateur au groupe

    @param user: l'utilisateur à supprimer
    @param groupe: le groupe dans lequel supprimer l'utilisateur
    @return:/
    """
    if (user.id == id_gerant):
        if (groupe.count() == 1):
            groupe.delete()
        else:
            groupe.remove(user)
            id_gerant = groupe.objects.all()[0]
    else:
        groupe.remove(user)


def creation_groupe(nom, user):
    """

    @param nom:
    @param user:
    @return:
    """
    gp = Groupe(nom=nom, id_gerant=user.id)
    gp.save()
    gp.add(user)

def renvoie_liste(groupe):
    """

    @param groupe:
    @return:
    """
    liste = Groupe.objects.filter(idGroupe=groupe);
    print(liste[0].liste_adherants)