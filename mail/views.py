from django.shortcuts import render
from django.core.mail import send_mail
import random

def verif_email(request):
    try:
        send_mail("Vérification de votre compte - Ne pas répondre",
        "Code de vérification :\n"
        + "         " + random_value()
        + "\n\nL'équipe EatAdvisor",
        "eat_advisor2@outlook.fr",
        ["matteo.miguelez@gmail.com"],
        fail_silently=False);
    except:
        print("test")
    return render(request, 'send/mailtest.html')

def random_value():
    value_random = ""
    for i in range(6):
        value_random += str(random.randint(0, 9))
    return value_random