from django.contrib import admin
from django.urls import path

from .views import register,login,verificationEmail,modifUser,index


urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('modifuser/',modifUser,name='modifUser'),
    path('verificationEmail/',verificationEmail,name='verificationEmail'),
    path('index/',index,name='index'),
]

