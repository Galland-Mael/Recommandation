from django.http import HttpResponse
from django.shortcuts import render

def vue_test(request):
    return HttpResponse("<h1> TEST </h1>")

