from django.contrib import admin
from django.urls import path
from appsae.views import *
from django.conf import settings
from .models import *
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/register/', register, name='register'),
    path('user/login/', login, name='login'),
    path('modifuser/', modifUser, name='modifUser'),
    path('verificationEmail/', verificationEmail, name='verificationEmail'),
    path('', index, name='index'),
    path('carrousel/', meilleurs_resto, name='meilleurs_resto'),
    path('logout/', logoutUser, name='logout'),
    path('addCommentaires/(<pk>)', addCommentaires, name='addCommentaires'),
    path('vueRestaurant/(<pk>)', vueRestaurant, name='vueRestaurant'),
    path('search/', search, name='search'),
    path('addUser/(<user>)', addUser, name='addUser'),
    path('removeUser/(<user>)', removeUser, name='removeUser'),
    path('searchUser/', searchUser, name='searchUser'),
    path('export_restaurant/', export_restaurant, name='export'),
    path('export_ratings/', export_ratings, name='export'),
    path('voirPlus/(<pk>)', voirPlus, name='voirPlus'),
    path('groupe/', groupe, name='groupe'),
    path('creationGroup/', creationGroup, name='creationGroup'),
    path('groupRecommandations/(<pk>)', groupRecommandations, name='groupRecommandations'),
    path('groupePage/', groupePage, name='groupePage'),
    path('searchRestau/', searchRestau, name='searchRestau'),
    path('nomGroup/', nomGroup, name='nomGroup'),
    path('createGroupe/', createGroupe, name='createGroupe'),
    path('modification/', modification, name='modification'),
    path('recommandation/', recommandation, name='recommandation'),
    path('setImg/', setImg, name='setImg'),
    path('deleteGroup/(<pk>)', deleteGroup, name='deleteGroup'),
    path('recommendation', recommendation, name='recommendation'),
    path('restaurateur/login', login_restaurateur, name='login_restaurateur'),
    path('restaurateur/register', register_restaurateur, name='register_restaurateur'),
    path('restaurateur', index_restaurateur, name='index_restaurateur'),
    path('restaurateur/formulaire', formulaire_demande_restaurateur, name='formulaire_demande_restaurateur'),
    path('administrateur', administrateur_page, name="administrateur_page"),
    path('administrateur/demande/(<pk>)', validation_admin, name="validation_admin"),
    path('administrateur/suppression/(<pk>)', refuser_form, name="refuser_form"),
    path('administrateur/ajout/(<pk>)', ajouter_resto, name="ajouter_resto")
]
'''Utile pour afficher les images de la base de données'''
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
