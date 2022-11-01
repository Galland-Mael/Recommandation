from django.forms import ModelForm
from .models import RestaurantType
from .models import Adherant


class RestaurantTypeForm(ModelForm):
    class Meta:
        model = RestaurantType
        fields = ['nom']


class AdherantForm(ModelForm):
    class Meta:
        model = Adherant
        fields = ['nom', 'prenom', 'birthdate', 'Pseudo']
