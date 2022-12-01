from .models import *


def ajout_utilisateur(user, groupe):
    """ Ajout d'un utilisateur au groupe

    @param user: l'utilisateur à ajouter
    @param groupe : le groupe dans lequel ajouter l'utilisateur
    @return: /
    """
    groupe.liste_adherants.add(user)


def suppressionGroupe(groupe):
    """ Supprime le groupe dans la base de données

    @param groupe: le groupe a supprimé
    @return: /
    """
    groupe.delete()


def updateId_gerant(groupe,id):
    """ Fonction de mise à jour de l'id_gerant du groupe avec l'id donné en paramètre

    @param groupe: le groupe à modifier
    @param id: l'id du nouveau gérant du groupe
    @return: /
    """
    Groupe.objects.filter(idGroupe=groupe.idGroupe).update(id_gerant=id)


def updateNom(groupe, nom):
    """ Fonction de mise à jour du nom du groupe

    @param groupe: le groupe à modifier
    @param nom: le nouveau nom du groupe
    @return: /
    """
    Groupe.objects.filter(idGroupe=groupe.idGroupe).update(nom_groupe=nom)


def suppression_utilisateur(user, groupe):
    """ Suppression d'un utilisateur au groupe
    Si il n'y a qu'un utilisateur dans le groupe, le groupe est supprimé,
    Si le gérant est supprimé du groupe on donne l'id_gerant au premier utilisateur
    dans la liste_adherants
    Sinon on supprime l'utilisateur

    @param user: l'utilisateur à supprimer
    @param groupe: le groupe dans lequel supprimer l'utilisateur
    @return:/
    """
    if user.id == groupe.id_gerant:
        if groupe.liste_adherants.count() == 1:
            groupe.delete()
        else:
            groupe.liste_adherants.remove(user)
            new_gerant = groupe.liste_adherants.all()[0]
            updateId_gerant(groupe, new_gerant.id)
    else:
        groupe.liste_adherants.remove(user)


def creation_groupe(nom, user):
    """ Création d'un groupe à partir de l'utilisateur user, user sera le
    gérant du groupe

    @param nom: le nom du groupe
    @param user: le gérant du groupe
    @return: /
    """
    # A faire : gérer l'id Groupe
    gp = Groupe(nom_groupe=nom, id_gerant=user.id, idGroupe=10)
    gp.save()
    gp.liste_adherants.add(user)