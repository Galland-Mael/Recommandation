from django.contrib import admin
from django.urls import path
from . import views
from .views import index,register,login,verificationEmail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('email/', verificationEmail, name='verificationEmail'),
]

