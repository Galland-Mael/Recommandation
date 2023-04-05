from .models import *
from .gestion import connect
from django.conf import settings
from django.shortcuts import render, redirect
import hashlib
import datetime
from time import mktime
from .ajoutCSV import add_restaurant_csv
from random import randint
from .classes import Horaire
from .fonctionsBd import testNomUTF


def validation_admin(request, pk):
    """
    Vue d'une demande de création de restaurant pour un admin
    @param request: L'objet HttpRequest qui est envoyé par le client
    @param pk: la clé primaire de la demande
    @return:
    """
    if 'mailAdministrateur' in request.session:
        demande = DemandeCreationRestaurant.objects.get(pk=pk)
        context = {
            'demande': demande,
            'pk': demande.pk
        }
        connect(request, context)
        return render(request, 'administrateur/validation.html', context)
    return redirect('index')


def index_administrateur(request):
    """
    Vue de l'index de l'administrateur avec toutes les demandes de création a valider ou refuser
    @param request: L'objet HttpRequest qui est envoyé par le client
    @return:
    """
    if 'mailAdministrateur' in request.session:
        context = {
            'demandes': DemandeCreationRestaurant.objects.filter(traite=False).order_by("-date_creation")
        }
        connect(request, context)
        return render(request, 'administrateur/index.html', context)
    return redirect('index')


def modif_resto(request):
    """
    Vue de la page de modifications et d'informations sur le restaurant.
    @param request: L'objet HttpRequest qui est envoyé par le client
    @return:
    """
    if 'mailRestaurateur' in request.session:
        if request.method == "POST":
            info = request.POST
            if 'telephone' in info and info['telephone'] != '':
                print("Ajout du téléphone")
            if 'test' in info:
                print(info)
        last_avis = Avis.objects.filter(restaurant_fk=Restaurateur.objects.get(
            mail=request.session['mailRestaurateur']).restaurant_fk).order_by('-unix_date')
        context = {
            'list': [Horaire("Lundi", "11:00", "15:00"), Horaire("Mardi", "11:00", "15:00"),
                     Horaire("Mercredi", "11:00", "15:00"), Horaire("Jeudi", "11:00", "15:00"),
                     Horaire("Vendredi", "11:00", "15:00"), Horaire("Samedi", "11:00", "15:00"),
                     Horaire("Dimanche", "11:00", "15:00")],
            'restaurant': Restaurant.objects.get(
                pk=Restaurateur.objects.get(mail=request.session['mailRestaurateur']).restaurant_fk.pk),
        }
        if last_avis.count() != 0:
            context['lastComments'] = last_avis[:2]
        return render(request, 'restaurateur/modifResto.html', connect(request, context))
    return redirect('index')


def refuser_form(request, pk):
    """
    Vue permettant à l'administrateur de refuser une demande de création de restaurant
    @param request: L'objet HttpRequest qui est envoyé par le client
    @param pk: la clé primaire de la demande
    @return:
    """
    if 'mailAdministrateur' in request.session:
        context = {}
        if request.method == "POST":
            refus = RefusDemandeRestaurant(
                titre=request.POST['title'],
                message=request.POST['description'],
                restaurateur_fk=DemandeCreationRestaurant.objects.get(pk=pk).restaurateur_fk
            )
            refus.save()
            DemandeCreationRestaurant.objects.filter(pk=pk).update(traite=1)
            return redirect('index_administrateur')
        connect(request, context)
        return render(request, 'administrateur/form_refus.html', context)
    return redirect('index')


def ajouter_resto(request, pk):
    """
    Vue permettant de valider la demande de création de restaurant par un administrateur
    @param request: L'objet HttpRequest qui est envoyé par le client
    @param pk: la clé primaire de la demande
    @return:
    """
    if 'mailAdministrateur' in request.session:
        demande = DemandeCreationRestaurant.objects.get(pk=pk)
        restaurant = Restaurant(
            nom=demande.nom,
            adresse=demande.adresse,
            ville=demande.ville,
            zip_code=demande.zip_code,
            pays=demande.pays,
            etat=demande.etat,
            longitude=demande.longitude,
            latitude=demande.latitude,
            note = -1
        )
        restaurant.save()
        new_restaurant = Restaurant.objects.get(
            nom=demande.nom,
            adresse=demande.adresse,
            ville=demande.ville,
            zip_code=demande.zip_code,
            pays=demande.pays,
            etat=demande.etat,
            longitude=demande.longitude,
            latitude=demande.latitude
        )
        for type_name in demande.type.all():
            type = RestaurantType.objects.get(nom=type_name)
            restaurant.type.add(type)
        add_restaurant_csv(new_restaurant)
        setImageAleatoireRestaurant(new_restaurant, request)
        Restaurateur.objects.filter(pk=demande.restaurateur_fk_id).update(restaurant_fk=new_restaurant)
        demande.delete()
        return redirect('index_administrateur')
    return redirect('index')


def register_restaurateur(request):
    """
    Vue permettant au restaurateur de se créer un compte
    @param request: L'objet HttpRequest qui est envoyé par le client
    @return:
    """
    if request.method == "POST":
        info = request.POST
        if info['password_verif'] == info['password']:
            if info['mail'] != '' and info['password'] != '':
                restaurateur = Restaurateur(
                    mail=info['mail'],
                    password=hashlib.sha256(info['password'].encode('utf-8')).hexdigest()
                )
                restaurateur.save()
                return redirect('../restaurateur/login')
    return render(request, 'restaurateur/register_restaurateur.html')


def login_restaurateur(request):
    """
    Vue permettant au restaurateur ou a un administrateur de se connecter
    @param request: L'objet HttpRequest qui est envoyé par le client
    @return:
    """
    # Déconnexion
    if 'mailUser' in request.session or 'mailAdministrateur' in request.session or 'mailRestaurateur' \
            in request.session:
        return redirect('logout')

    if request.method == "POST":
        info = request.POST

        # Cas restaurateur
        restaurateur = Restaurateur.objects.filter(mail=info['mail'])
        if restaurateur.count() == 1:
            hashed_password = hashlib.sha256(info['password'].encode('utf-8')).hexdigest()
            if hashed_password == restaurateur[0].password:
                request.session['mailRestaurateur'] = restaurateur[0].mail
                return redirect('index_restaurateur')

        # Cas administrateur
        administrateur = Administrateur.objects.filter(mail=info['mail'])
        if administrateur.count() == 1:
            hashed_password = hashlib.sha256(info['password'].encode('utf-8')).hexdigest()
            if hashed_password == administrateur[0].password:
                request.session['mailAdministrateur'] = administrateur[0].mail
                return redirect('index_administrateur')

    return render(request, 'restaurateur/login_restaurateur.html')


def index_restaurateur(request):
    """
    Vue de l'index du restaurateur
    @param request: L'objet HttpRequest qui est envoyé par le client
    @return:
    """
    if 'mailRestaurateur' in request.session:
        restaurateur = Restaurateur.objects.get(mail=request.session['mailRestaurateur'])
        demande = DemandeCreationRestaurant.objects.filter(restaurateur_fk=restaurateur.pk)
        context = {
            'nombre': demande.count(),
            'restaurant_exist': (restaurateur.restaurant_fk_id is not None),
        }
        if restaurateur.restaurant_fk_id is not None:
            context['restaurant'] = restaurateur.restaurant_fk
            return redirect('vueRestaurant', pk=restaurateur.restaurant_fk.pk)
        elif demande.count() == 1:
            refus = RefusDemandeRestaurant.objects.filter(restaurateur_fk=restaurateur.pk)
            if refus.count() != 0:
                context['refus'] = RefusDemandeRestaurant.objects.filter(restaurateur_fk=restaurateur.pk)[0]
            date_actuelle = datetime.datetime.today().replace(tzinfo=None).timetuple()
            date_bd = demande[0].date_creation.replace(tzinfo=None).timetuple()
            temps_entre_demande = 400  # replace with 259200
            temps = int(mktime(date_bd) + temps_entre_demande - mktime(date_actuelle))
            context['minutes'] = temps // 60
            context['secondes'] = temps % 60
            if demande[0].traite == 1:
                if mktime(date_bd) + temps_entre_demande < mktime(date_actuelle):
                    DemandeCreationRestaurant.objects.filter(pk=demande[0].pk).update(traite=2)
            context['demande'] = demande[0]
        connect(request, context)
        return render(request, 'restaurateur/index.html', context)
    return redirect('index')


def create_demandecreationrestaurant(info, request):
    """
    Crée une DemandeCreationRestaurant dans la base de données avec les infos données en paramètres
    @param info: les informations du formulaire
    @param request: L'objet HttpRequest qui est envoyé par le client
    @return: /
    """
    if info['nom'] != '' and info['adresse'] != '' and info['ville'] != '' and info['postal'] and info['pays'] != '' \
            and info['longitude'] and info['latitude'] != '':
        restaurateur = Restaurateur.objects.get(mail=request.session['mailRestaurateur'])
        demande_creation = DemandeCreationRestaurant(
            nom=info['nom'],
            adresse=info['adresse'],
            ville=info['ville'],
            zip_code=info['postal'],
            pays=info['pays'],
            etat=info['etat'],
            longitude=info['longitude'],
            latitude=info['latitude'],
            restaurateur_fk=restaurateur,
        )
        demande_creation.save()
        for type_name in info.getlist('type'):
            type = RestaurantType.objects.get(nom=type_name)
            demande_creation.type.add(type)
        RefusDemandeRestaurant.objects.filter(restaurateur_fk=restaurateur.pk).delete()
        return True
    return False


def formulaire_demande_restaurateur(request):
    """
    Vue du formulaire de demande de création de restaurant pour le restaurateur
    @param request: L'objet HttpRequest qui est envoyé par le client
    @return:
    """
    context = {}
    if 'mailRestaurateur' in request.session:
        restaurateur = Restaurateur.objects.get(mail=request.session['mailRestaurateur'])
        context['restaurant_exist'] = (restaurateur.restaurant_fk_id is not None)
        demande = DemandeCreationRestaurant.objects.filter(restaurateur_fk=restaurateur.pk)
        if request.method == "POST":
            info = request.POST
            test = False
            if demande.count() == 0:
                test = create_demandecreationrestaurant(info, request)
            elif demande.count() == 1 and demande[0].traite == 2:
                DemandeCreationRestaurant.objects.filter(restaurateur_fk=restaurateur.pk).delete()
                test = create_demandecreationrestaurant(info, request)
            if test:
                return redirect('index_restaurateur')
        elif demande.count() == 1:
            context['demande'] = demande[0]
        context['types'] = RestaurantType.objects.all()
        connect(request, context)
        return render(request, 'restaurateur/createResto.html', context)
    return redirect('index')


def setImageAleatoireRestaurant(restaurant, request):
    """
    Fonction pour mettre un set aléatoire d'image à un nouveau restaurant
    @param restaurant: l'objet Restaurant dans le modèle de données à modifier
    @return: /
    """
    if 'mailAdministrateur' in request.session:
        random_value = randint(1, 4)
        restaurant.image_front = "/img_restaurant/imagefront" + str(random_value) + ".jpg"
        '/img_restaurant/imagefront3.jpg'
        restaurant.save()
        indice_in_list = (random_value - 1) * 4  # Les images des sets sont stockées les unes après les autres et il y en a 4

        imgset = ImageRestaurant.objects.all()
        for index in range(4):
            restaurant.img.add(imgset[indice_in_list + index])
    return redirect('index')


def export_restaurant(request):
    """
    exporte l'ensemble des restaurants dans des fichiers csv séparés en fonction de leur ville
    @param request: L'objet HttpRequest qui est envoyé par le client
    @return:
    """
    if 'mailAdministrateur' in request.session:
        listVilles = ["Philadelphia", "Tampa", "Indianapolis", "Nashville", "Tucson", "New Orleans", "Edmonton",
                      "Saint Louis", "Reno",
                      "Saint Petersburg", "Boise", "Santa Barbara", "Clearwater", "Wilmington", "St. Louis", "Metairie",
                      "Franklin"]
        for villes in listVilles:
            file = str(settings.BASE_DIR) + '/csv/' + "restaurant_" + filterVilleResto(villes) + ".csv"
            f = open(file, "w")
            f.writelines("id;nom;genre")
            f.write('\n')
            for restaurant in Restaurant.objects.filter(ville=villes):
                f.write(str(restaurant.pk))
                f.write(";")
                f.write(testNomUTF(restaurant.nom))
                f.write(";")
                taille = restaurant.type.all().count()
                for i in range(taille):
                    f.write(str(restaurant.type.all()[i]))
                    if i != taille - 1:
                        f.write(" ")
                f.write('\n')
            print(file)
    return redirect('index')


def export_ratings(request):
    """
    Exporte l'ensemble des ratings dans un fichier csv ratings.csv
    @param request: L'objet HttpRequest qui est envoyé par le client
    @return:
    """
    if 'mailAdministrateur' in request.session:
        file = str(settings.BASE_DIR) + '/' + "ratings.csv"
        f = open(file, "w")
        f.writelines("user_id,restaurant_id,note")
        for rating in Avis.objects.all().values_list('adherant_fk', 'restaurant_fk', 'note'):
            f.write('\n')
            f.write(str(rating)[1:-1])
        print(file)
    return redirect('index')

def filterVilleResto(nom):
    """

    @param nom:
    @return:
    """
    list = "azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN0123456789"
    nouveau_nom = ""
    for lettre in nom:
        if lettre in list:
            nouveau_nom += lettre
        elif lettre in 'éèê':
            nouveau_nom += 'e'
        elif lettre in 'ÉÈ':
            nouveau_nom += 'E'
    return nouveau_nom