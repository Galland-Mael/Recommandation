from django.forms import ModelForm
from .models import RestaurantType


class RestaurantTypeForm(ModelForm) :
    class Meta:
        model = RestaurantType
        fields = ['nom']
