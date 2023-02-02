from django.http import request
from surprise import Dataset

from .views import *
from .models import *
from .svd import *
from time import mktime
from django.db.models import Avg
from django.conf import settings
from csv import writer
from .listeRecommandation import *
from time import mktime


def addavisCSV(avis):
    """ Ajoute une ligne avec l'avis dans le fichier de restaurants

    @param avis:
    @return:
    """
    list = [str(avis.adherant_fk_id), ' ' + str(avis.restaurant_fk_id), ' ' + str(float(avis.note))]

    with open(str(settings.BASE_DIR) + '/' + "ratings.csv", 'a') as f_object:
        f_object.write('\n')
        f_object.write(str(avis.adherant_fk_id)+ ', ' + str(avis.restaurant_fk_id) + ', ' + str(float(avis.note)))
        f_object.close()


def filterNomRestaurant(nom):
    """

    @param nom:
    @return:
    """
    list = "azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN0123456789"
    nouveau_nom = ""
    for lettre in nom:
        if lettre in list:
            nouveau_nom += lettre
    return nouveau_nom


def avisExist(user, restaurant):
    """ Vérifie si l'utilisateur user a déjà ajouté un avis sur le restaurant

    @param user: l'utilisateur
    @param restaurant: le restaurant
    @return: true si l'avis existe, false sinon
    """
    return Avis.objects.filter(restaurant_fk=restaurant, adherant_fk=user).count() != 0


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


def majRecommandationsIndividuellesBD(user, recommandation_user):
    """ Appel de l'algorithme de recommandation individuelle pour l'utilisateur user

    @param user: l'utilisateur
    @param restaurant: le restaurant
    @param recommandation_user: la recommandation existante
    @return: /
    """
    date_bd = recommandation_user.date.replace(tzinfo=None).timetuple()
    date_actuelle = datetime.datetime.today().replace(tzinfo=None).timetuple()
    if mktime(date_bd) <= mktime(date_actuelle) - 200:
        # MAJ de la date de la recommandation
        RecommandationUser.objects.filter(adherant_fk=user.pk).update(date=datetime.datetime.now())
        liste = listeRecommandationIndividuelle(user.pk)  # Liste des restaurants à recommander
        reco = RecommandationUser.objects.get(adherant_fk=user.pk)
        liste_reco = reco.recommandation.all()
        # Supprime les recommandations existantes
        for elem in liste_reco:
            reco.recommandation.remove(elem)
        # Ajoute les nouvelles recommandations à la liste
        reco = RecommandationUser.objects.get(adherant_fk=user.pk)
        for elem in liste:
            reco.recommandation.add(elem)
        # MAJ du datetime
        RecommandationUser.objects.filter(adherant_fk=user.pk).update(date=datetime.datetime.now())


def ajoutAvis(user, restaurant, note, avis):
    """ Fonction permettant d'ajouter une note et un avis
    @param user: l'utilisateur
    @param restaurant: le restaurant
    @return: /
    """
    # si l'avis n'existe pas déjà
    if not avisExist(user, restaurant):
        nb_review_ad = Adherant.objects.get(pk=user.pk).nb_review
        nb_review_resto = Restaurant.objects.get(pk=restaurant.pk).nb_review
        ajout = Avis(note=note, texte=avis, restaurant_fk=restaurant, adherant_fk=user)
        ajout.save()
        Restaurant.objects.filter(pk=restaurant.pk).update(nb_review=(nb_review_resto+1))
        Adherant.objects.filter(pk=user.pk).update(nb_review=(nb_review_ad+1))
        addavisCSV(ajout)
        updateNoteMoyenneRestaurant(restaurant)
        if nb_review_ad >= 5: # si l'adhérent à déjà posté 5 notes
            recommandation_user = RecommandationUser.objects.filter(adherant_fk=user.pk)
            if recommandation_user.count() == 0: # si il n'a pas encore de recommandation
                reco = RecommandationUser(adherant_fk=user)
                reco.save()
                liste = listeRecommandationIndividuelle(user.pk)
                for elem in liste:
                    reco.recommandation.add(elem)
                RecommandationUser.objects.filter(adherant_fk=user.pk).update(date=datetime.datetime.now())
            else:
                majRecommandationsIndividuellesBD(user, recommandation_user[0])


def updateAvis(user, restaurant, note, avis):
    """ Mise à jour de le note (et l'avis) de l'utilisateur user pour le restaurant restaurant
    @param user: l'utilisateur
    @param restaurant: le restaurant
    @param note: la nouvelle note
    @param avis: le nouvel avis
    @return: /
    """
    if avisExist(user,restaurant):
        Avis.objects.filter(restaurant_fk=restaurant, adherant_fk=user).update(note=note, texte=avis)
        updateNoteMoyenneRestaurant(restaurant)


def suppressionAvis(user, restaurant):
    """ Suppression de l'avis de l'utilisateur user sur le restaurant restaurant

    @param user: l'utilisateur
    @param restaurant: le restaurant
    @return: /
    """
    if avisExist(user,restaurant):
        Avis.objects.get(restaurant_fk=restaurant, adherant_fk=user).delete()
        updateNoteMoyenneRestaurant(restaurant)
        nb_review_ad = Adherant.objects.get(pk=user.pk).nb_review
        nb_review_resto = Restaurant.objects.get(pk=restaurant.pk).nb_review
        Adherant.objects.filter(pk=user.pk).update(nb_review=(nb_review_ad-1))
        Restaurant.objects.filter(pk=restaurant.pk).update(nb_review=(nb_review_resto-1))


def listeAffichageAvis(restaurant, num, user=""):
    """ Renvoie une liste d'avis 10 par 10 ne contenant pas l'avis de l'utilisateur user,
    si num vaut 0, on renvoie de 0 à 9 dans la liste des avis, etc...

    @param restaurant: le restaurant
    @param user: l'utilisateur
    @param num: le numéro de la page
    @return: une liste (QuerySet) d'avis
    """
    taille_list = 2
    if user == "":
        avis = Avis.objects.filter(restaurant_fk=restaurant)
    else:
        avis = Avis.objects.filter(restaurant_fk=restaurant).exclude(adherant_fk=user)
    return avis[num*taille_list:(num + 1)*taille_list]


def afficherVoirPlus(restaurant, num, user=""):
    """Renvoie true s'il faut afficher le bouton "Voir Plus", false sinon

    @param restaurant: le restaurant concerné
    @param num: le numéro de la page actuelle
    @param user: l'utilisateur concerné
    @return: booléen en fonction de s'il faut afficher ou non "Voir Plus"
    """
    return listeAffichageAvis(restaurant, num + 1, user).count() != 0


def listRecommandationGroupe(groupe):
    ratings_data = pd.read_csv('./ratings.csv')
    user_idgerant = Groupe.objects.get(pk=groupe.pk).id_gerant
    user = Adherant.objects.filter(pk=user_idgerant)
    restaurant_metadata = pd.read_csv('./restaurant_' + filterNomRestaurant(str(user[0].ville)) + '.csv', delimiter=';', engine='python')
    reader = Reader(rating_scale=(0, 5))
    data = Dataset.load_from_df(ratings_data[['user_id', 'restaurant_id', 'note']], reader)
    trainset, testset = train_test_split(data, test_size=0.20)
    svd = SVD(verbose=False, n_epochs=23, n_factors=7)
    predictions = svd.fit(trainset).test(testset)
    # accuracy.rmse(predictions)
    # testMatteo(groupe, svd, restaurant_metadata, 15)
    l = algoRecommandationGroupe(groupe, svd, restaurant_metadata, 15)
    print(l)
    liste_complete = []
    for elem in l:
        liste_complete.append(get_restaurant_id(elem[0], restaurant_metadata))
    
    return liste_complete


def ajoutBDRecommandationGroupe(groupe):
    reco_groupe= RecommandationGroupe.objects.filter(groupe_fk=groupe)
    if reco_groupe.count() == 0:
        reco = RecommandationGroupe(groupe_fk=groupe)
        reco.save()
        list = listRecommandationGroupe(groupe)
        for elem in list:
            reco.recommandation.add(elem)
        RecommandationGroupe.objects.filter(groupe_fk=groupe).update(date=datetime.datetime.now())
    else:
        date_actuelle = datetime.datetime.today().replace(tzinfo=None).timetuple()
        date_bd = reco_groupe[0].date.replace(tzinfo=None).timetuple()
        if mktime(date_bd) <= mktime(date_actuelle)-200:
            RecommandationGroupe.objects.filter(groupe_fk=groupe).update(date=datetime.datetime.now())
            list = listRecommandationGroupe(groupe)
            reco = RecommandationGroupe.objects.get(groupe_fk=groupe)
            list_Reco = reco.recommandation.all()
            for elem in list_Reco:
                reco.recommandation.remove(elem)
            reco = RecommandationGroupe.objects.get(groupe_fk=groupe)
            for elem in list:
                reco.recommandation.add(elem)
            RecommandationGroupe.objects.filter(groupe_fk=groupe).update(date=datetime.datetime.now())


