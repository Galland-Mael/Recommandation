from django.contrib import admin
from django.urls import path

from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/register/', register, name='register'),
    path('user/login/', login, name='login'),
    path('modifuser/',modifUser,name='modifUser'),
    path('verificationEmail/',verificationEmail,name='verificationEmail'),
    path('index/',index,name='index'),
    path('carrousel/', meilleurs_resto, name='meilleurs_resto')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
