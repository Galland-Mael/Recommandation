import os
from django.conf import settings
from .listeRecommandation import suppEspace


def add_restaurant_csv(restaurant):
    """
    Ajoute un nouveau restaurant dans le CSV lui correspondant
    @param restaurant: l'objet Restaurant dans le modèle de données à ajouter
    @return: /
    """
    if verif_csv(restaurant):
        add_existant_csv(restaurant)
    else:
        create_csv(restaurant)


def create_csv(restaurant):
    """
    Crée un nouveau CSV avec le nom de la ville du restaurant, et ajoute le restaurant dedans
    @param restaurant: l'objet Restaurant dans le modèle de données à ajouter au nouveau CSV
    @return: /
    """
    file = str(settings.BASE_DIR) + '/csv/' + "restaurant_" + suppEspace(restaurant.ville) + ".csv"
    f = open(file, "w")
    f.writelines("id;nom;genre")
    f.write('\n' + str(restaurant.pk) + ";" + restaurant.nom + ";")
    types = restaurant.type.all()
    taille = types.count()
    for i in range(taille):
        f.write(str(types[i]))
        if i != taille - 1:
            f.write(" ")
    f.close()


def verif_csv(restaurant):
    """
    Vérifie s'il existe un fichier CSV avec le nom de la ville du restaurant passé en paramètres
    @param restaurant: l'objet Restaurant dans le modèle de données à tester
    @return: true si le CSV existe, false sinon
    """
    return os.path.exists(os.path.join('csv', 'restaurant_'+str(suppEspace(restaurant.ville))+'.csv'))


def add_existant_csv(restaurant):
    """
    Ajoute un restaurant au fichier CSV de sa ville
    @param restaurant: l'objet Restaurant dans le modèle de données à ajouter
    @return:
    """
    with open(str(settings.BASE_DIR) + '/csv/restaurant_'+str(suppEspace(restaurant.ville))+'.csv', 'a') as f_object:
        f_object.write('\n' + str(restaurant.pk) + '; ' + str(restaurant.nom) + '; ')
        types = restaurant.type.all()
        taille = types.count()
        for i in range(taille):
            f_object.write(str(types[i]))
            if i != taille - 1:
                f_object.write(" ")
        f_object.close()
