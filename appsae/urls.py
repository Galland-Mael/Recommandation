from django.contrib import admin
from django.urls import path
from appsae.views import *
from django.conf import settings
from .models import *
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [

]

urlpatterns += i18n_patterns(
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('user/register/', register, name='register'),
    path('user/login/', login, name='login'),
    path('modifuser/', modifUser, name='modifUser'),
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
    path('pageVerifMail', pageVerifMail, name='pageVerifMail'),
    path('verifMail',verifMail,name='verifMail'),
    path('deleteUser/(<pk>)',deleteUser,name='deleteUser'),
)
'''Utile pour afficher les images de la base de données'''
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
