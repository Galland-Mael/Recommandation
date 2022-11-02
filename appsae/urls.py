from django.contrib import admin
from django.urls import path
from . import views
from .views import register,login,verificationEmail,testAntoine

urlpatterns = [
    path('admin/', admin.site.urls),
    path('testAntoine/',testAntoine , name='testAntoine'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('email/', verificationEmail, name='verificationEmail'),
]

