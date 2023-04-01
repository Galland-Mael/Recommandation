from django.forms import ModelForm
from appsae.models import RestaurantType
from appsae.models import Adherant
from django import forms
from captcha.fields import ReCaptchaField


class RestaurantTypeForm(ModelForm):
    class Meta:
        model = RestaurantType

        fields = ['nom']


class AdherantForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    captcha = ReCaptchaField()

    class Meta:
        model = Adherant
        fields = ['prenom','nom','birthDate','mail','password']


class verifLogin(ModelForm):
    class Meta:
        model = Adherant
        fields =['mail','password']


