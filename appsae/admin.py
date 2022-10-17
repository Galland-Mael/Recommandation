from django.contrib import admin

# Register your models here.

from django.contrib import admin

from .models import Adherant, Groupe, Restaurant, Type_restaurant, Horaire, ImageRestaurant

admin.site.register(Adherant)
admin.site.register(Groupe)
admin.site.register(Restaurant)
admin.site.register(Type_restaurant)
admin.site.register(Horaire)
admin.site.register(ImageRestaurant)
