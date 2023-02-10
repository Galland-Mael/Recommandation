# Register your models here.

from django.contrib import admin
from .models import *

admin.site.register(Adherant)
admin.site.register(Groupe)
admin.site.register(Restaurant)
admin.site.register(Horaire)
admin.site.register(ImageRestaurant)
admin.site.register(RestaurantType)
admin.site.register(Avis)
admin.site.register(RecommandationUser)
admin.site.register(RecommandationGroupe)
admin.site.register(ImageUser)
admin.site.register(Restaurateur)
admin.site.register(DemandeCreationRestaurant)
admin.site.register(Administrateur)

