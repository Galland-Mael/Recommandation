class Horaire:
    """
    Classe stockant les horaires sur une journée d'un restaurant
    """
    def __init__(self, jour, horaire1_deb="00:00", horaire1_fin="00:00", horaire2_deb="00:00", horaire2_fin="00:00"):
        """
        Constructeur de la classe Horaire
        @param jour: le jour de la semaine (Lundi, Mardi,...)
        @param horaire1_deb: le début du premier horaire
        @param horaire1_fin: la fin du premier horaire
        @param horaire2_deb: le début du deuxième horaire (si vide "00:00")
        @param horaire2_fin: la fin du deuxième horaire (si vide "00:00")
        """
        self.jour = jour
        self.horaire1_deb = horaire1_deb
        self.horaire2_deb = horaire2_deb
        self.horaire1_fin = horaire1_fin
        self.horaire2_fin = horaire2_fin


class NumbersStars:
    """
    Classe stockant un nombre à virgule et son entier supérieur
    """
    def __init__(self, nombre_virgule):
        """
        Constructeur de la classe NumbersStars, prend en argument un nombre à virgule (un demi entier) et l'ajoute à
        l'attribut nombre_virgule, et initialise le nombre à l'entier supérieur
        @param nombre_virgule: le nombre a virgule (demi entier)
        """
        self.nombre = nombre_virgule + 0.5
        self.nombre_virgule = nombre_virgule


class RestaurantInfo:
    """
    Classe stockant les informations d'un restaurant
    """
    def __init__(self, restaurant):
        """
        Constructeur de la classe RestaurantInfo, prend en argument un restaurant et conserve ses informations
        importantes pour son affichage
        @param restaurant: une instance du modèle de données Restaurant
        """
        self.pk = restaurant.pk
        self.note = restaurant.note
        self.nb_review = restaurant.nb_review
        self.name = setNomRestaurant(restaurant.nom)
        self.image_front = restaurant.image_front
        self.types = setTypesRestaurant(restaurant.type.all())


def setNomRestaurant(nom):
    """
    Racourci le nom du restaurant et ajoute des '...' si le nom est trop long
    @param nom: le nom originel
    @return: le nouveau nom modifié si la taille est trop grande
    """
    if len(nom) > 24:
        if len(nom) < 27:
            return nom
        else:
            return nom[:24] + "..."
    return nom


def setTypesRestaurant(types):
    """
    Renvoie les types du restaurant concaténés avec des '|' avec une taille limitée à 26
    @param types:
    @return:
    """
    taille_actuelle = 0
    return_types = ""
    for indice, type in enumerate(types):
        taille_actuelle += len(type.nom) + 3
        if taille_actuelle < 26:
            if indice != 0:
                return_types += " | "
            return_types += str(type.nom[0].upper()) + str(type.nom[1:])
    return return_types