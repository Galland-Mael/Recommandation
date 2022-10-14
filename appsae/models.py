from django.db import models

# Create your models here.

from django.db import models


class Adhérant(models.Model):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    mail = models.EmailField(max_length=254)
    telephone = models.CharField(max_length=10)
    Pseudo = models.CharField(max_length=20)
    profile_picture = models.ImageField(upload_to='media/img/profile_pictures')



class Groupe(models.Model):
    nom = models.CharField(max_length=25)



class Restaurant(models.Model):
    nom = models.CharField(max_length=50)
    pays = models.CharField(max_length=50)
    adresse = models.CharField(max_length=50)
    telephone = models.CharField(max_length=10)
    image_front = models.ImageField(upload_to='media/img/image_front')
    liste_image = models.ImageField(upload_to='media/img/liste_images')



class Type_restaurant(models.Model):
    nom = models.CharField(max_length=50)


class Horaire(models.Model):

    class Nom_jour(models.IntegerChoices):
        Lundi= 1
        Mardi = 2
        Mercredi = 3
        Jeudi = 4
        Vendredi = 5
        Samedi = 6
        Dimanche = 7

    Nom_jour  = models.IntegerField(choices=Nom_jour.choices)

    Debut_Horaire1 = models.TimeField
    Fin_Horaire1 = models.TimeField
    Debut_Horaire2 = models.TimeField
    Fin_Horaire2 = models.TimeField
    Debut_Horaire3 = models.TimeField
    Fin_Horaire3 = models.TimeField

