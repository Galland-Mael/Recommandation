from .models import *
from .gestion import connect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
import hashlib
import datetime
import time
from time import mktime


def validation_admin(request, pk):
    if 'mailAdministrateur' in request.session:
        demande = DemandeCreationRestaurant.objects.get(pk=pk)
        context = {
            'demande': demande,
            'pk': demande.pk
        }
        connect(request, context)
        return render(request, 'administrateur/validation.html', context)
    return redirect('index')


def administrateur_page(request):
    if 'mailAdministrateur' in request.session:
        context = {
            'demandes': DemandeCreationRestaurant.objects.filter(traite=False).order_by("-date_creation")
        }
        connect(request, context)
        return render(request, 'administrateur/index.html', context)
    return redirect('index')


def refuser_form(request, pk):
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
            return redirect('administrateur_page')
        connect(request, context)
        return render(request, 'administrateur/form_refus.html', context)
    return redirect('index')


def ajouter_resto(request, pk):
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
        )
        restaurant.save()
        Restaurateur.objects.filter(pk=demande.restaurateur_fk_id).update(restaurant_fk=restaurant)
        demande.delete()
        return redirect('administrateur_page')
    return redirect('index')


def register_restaurateur(request):
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
    # Déconnexion
    if 'mailUser' in request.session or 'mailAdministrateur' in request.session or 'mailRestaurateur' in request.session:
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
                return redirect('administrateur_page')

    return render(request, 'restaurateur/login_restaurateur.html')


def index_restaurateur(request):
    if 'mailRestaurateur' in request.session:
        restaurateur = Restaurateur.objects.get(mail=request.session['mailRestaurateur'])
        demande = DemandeCreationRestaurant.objects.filter(restaurateur_fk=restaurateur.pk)
        context = {
            'nombre': demande.count(),
            'restaurant_exist' : (restaurateur.restaurant_fk_id is not None)
        }
        if restaurateur.restaurant_fk_id is not None:
            context['restaurant'] = restaurateur.restaurant_fk
            return redirect('vueRestaurant', pk=restaurateur.restaurant_fk.pk)
        elif demande.count() == 1:
            refus =RefusDemandeRestaurant.objects.filter(restaurateur_fk=restaurateur.pk)
            if refus.count() != 0:
                context['refus'] = RefusDemandeRestaurant.objects.filter(restaurateur_fk=restaurateur.pk)[0]
            date_actuelle = datetime.datetime.today().replace(tzinfo=None).timetuple()
            date_bd = demande[0].date_creation.replace(tzinfo=None).timetuple()
            temps_entre_demande = 400 # replace with 259200
            temps = (int)(mktime(date_bd) + temps_entre_demande - mktime(date_actuelle))
            context['minutes'] = temps//60
            context['secondes'] = temps%60
            if demande[0].traite == 1:
                if mktime(date_bd) + temps_entre_demande < mktime(date_actuelle):
                    DemandeCreationRestaurant.objects.filter(pk=demande[0].pk).update(traite=2)
            context['demande'] = demande[0]
        connect(request, context)
        return render(request, 'restaurateur/index.html', context)
    return redirect('index')


def create_DemandeCreationRestaurant(info, request):
    """ Crée une DemandeCreationRestaurant dans la base de données avec les infos données en paramètres

    @param info: les informations du formulaire
    @param request: informations utilisateurs
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
        RefusDemandeRestaurant.objects.filter(restaurateur_fk=restaurateur.pk).delete()
        return True
    return False


def formulaire_demande_restaurateur(request):
    context = {}
    if 'mailRestaurateur' in request.session:
        restaurateur = Restaurateur.objects.get(mail=request.session['mailRestaurateur'])
        demande = DemandeCreationRestaurant.objects.filter(restaurateur_fk=restaurateur.pk)
        if request.method == "POST":
            info = request.POST
            test = False
            if demande.count() == 0:
                test = create_DemandeCreationRestaurant(info, request)
            elif demande.count() == 1 and demande[0].traite == 2:
                DemandeCreationRestaurant.objects.filter(restaurateur_fk=restaurateur.pk).delete()
                test = create_DemandeCreationRestaurant(info, request)
            if test:
                return redirect('index_restaurateur')
        elif demande.count() == 1:
            context['demande'] = demande[0]
        connect(request, context)
        return render(request, 'restaurateur/createResto.html', context)
    return redirect('index_restaurateur')