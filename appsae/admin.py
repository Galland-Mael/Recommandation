from django.contrib import admin

# Register your models here.

from django.contrib import admin

from .models import Adherant, Groupe, Restaurant, RestaurantType, Horaire, ImageRestaurant

admin.site.register(Adherant)
admin.site.register(Groupe)
admin.site.register(Restaurant)
admin.site.register(Horaire)
admin.site.register(ImageRestaurant)
admin.site.register(RestaurantType)
