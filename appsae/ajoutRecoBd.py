from .models import RecommandationGroupe, RecommandationUser
from .listeRecommandation import *
from time import mktime


def ajoutBDRecommandationGroupe(groupe):
    reco_groupe= RecommandationGroupe.objects.filter(groupe_fk=groupe)
    if reco_groupe.count() == 0:
        reco = RecommandationGroupe(groupe_fk=groupe)
        reco.save()
        list = listeRecommandationGroupe(groupe)
        for elem in list:
            reco.recommandation.add(elem)
        RecommandationGroupe.objects.filter(groupe_fk=groupe).update(date=datetime.datetime.now())
    else:
        date_actuelle = datetime.datetime.today().replace(tzinfo=None).timetuple()
        date_bd = reco_groupe[0].date.replace(tzinfo=None).timetuple()
        if mktime(date_bd) <= mktime(date_actuelle)-200:
            RecommandationGroupe.objects.filter(groupe_fk=groupe).update(date=datetime.datetime.now())
            list = listeRecommandationGroupe(groupe)
            reco = RecommandationGroupe.objects.get(groupe_fk=groupe)
            list_reco = reco.recommandation.all()
            for elem in list_reco:
                reco.recommandation.remove(elem)
            reco = RecommandationGroupe.objects.get(groupe_fk=groupe)
            for elem in list:
                reco.recommandation.add(elem)
            RecommandationGroupe.objects.filter(groupe_fk=groupe).update(date=datetime.datetime.now())


def ajoutRecommandationsIndividuellesBd(user):
    """ Crée ou met à jour une recommandation individuelle dans la table RecommandationIndividuelle

    @param user: l'utilisateur
    @return: /
    """
    recommandation_user = RecommandationUser.objects.filter(adherant_fk=user.pk)
    if recommandation_user.count() == 0:  # si il n'a pas encore de recommandation
        reco = RecommandationUser(adherant_fk=user)
        reco.save()
        liste = listeRecommandationIndividuelle(user)
        for elem in liste:
            reco.recommandation.add(elem)
        RecommandationUser.objects.filter(adherant_fk=user.pk).update(date=datetime.datetime.now())
    else:
        majRecommandationsIndividuellesBD(user, recommandation_user[0])


def majRecommandationsIndividuellesBD(user, recommandation_user):
    """ Appel de l'algorithme de recommandation individuelle pour l'utilisateur user

    @param user: l'utilisateur
    @param recommandation_user: la recommandation existante
    @return: /
    """
    date_bd = recommandation_user.date.replace(tzinfo=None).timetuple()
    date_actuelle = datetime.datetime.today().replace(tzinfo=None).timetuple()
    if mktime(date_bd) <= mktime(date_actuelle) - 200:
        # MAJ de la date de la recommandation
        RecommandationUser.objects.filter(adherant_fk=user.pk).update(date=datetime.datetime.now())
        list_restaurants = listeRecommandationIndividuelle(user)  # Liste des restaurants à recommander
        reco = RecommandationUser.objects.get(adherant_fk=user.pk)
        liste_reco = reco.recommandation.all()
        # Supprime les recommandations existantes
        for elem in liste_reco:
            reco.recommandation.remove(elem)
        # Ajoute les nouvelles recommandations à la liste
        reco = RecommandationUser.objects.get(adherant_fk=user.pk)
        for elem in list_restaurants:
            reco.recommandation.add(elem)
        # MAJ du datetime
        RecommandationUser.objects.filter(adherant_fk=user.pk).update(date=datetime.datetime.now())
