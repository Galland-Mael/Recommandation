from django.contrib import admin
from django.urls import path

from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/register/', register, name='register'),
    path('user/login/', login, name='login'),
    path('modifuser/', modifUser, name='modifUser'),
    path('verificationEmail/', verificationEmail, name='verificationEmail'),
    path('test/', meilleurs_resto, name='meilleurs_resto'),
    path('adherant/', update, name='update'),
    path('noteMoyenne/', note_moyenne,name='note_moyenne'),
    path('', index, name='index'),
    path('logout/', logoutUser, name='logout'),
    path('matteo/', matteo, name='matteo'),
    path('search/', search, name='search'),
    path('carrousel/', meilleurs_resto, name='meilleurs_resto'),
    path('vueRestaurant/(<pk>)',vueRestaurant,name='vueRestaurant'),
]
'''Utile pour afficher les images de la base de données'''
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
