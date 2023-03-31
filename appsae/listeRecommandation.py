import difflib
import random
import numpy as np
import pandas as pd
import os
import time

from django.http import HttpResponse
from surprise import Reader, Dataset, SVD, accuracy
from surprise.model_selection import train_test_split
from surprise.model_selection import cross_validate
from .models import *
from .svd import *
from appsae.celery import app


def filterNomRestaurant(nom):
    """

    @param nom:
    @return:
    """
    list = "azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN0123456789"
    nouveau_nom = ""
    for lettre in nom:
        if lettre in list:
            nouveau_nom += lettre
    return nouveau_nom


@app.task
def listeRecommandationIndividuelle(user_id, taille=10):
    start = time.time()
    ratings_data = pd.read_csv('./ratings.csv')
    user = Adherant.objects.get(pk=user_id)
    restaurant_metadata = pd.read_csv('./restaurant_' + filterNomRestaurant(user.ville) +'.csv', delimiter=';', engine='python')
    reader = Reader(rating_scale=(0, 5))
    data = Dataset.load_from_df(ratings_data[['user_id', 'restaurant_id', 'note']], reader)
    trainset, testset = train_test_split(data, test_size=0.20)
    svd = SVD(verbose=False, n_epochs=23, n_factors=7)
    predictions = svd.fit(trainset).test(testset)
    accuracy.rmse(predictions)
    l = algoRecommandationIndividuelle.delay(user_id, svd, restaurant_metadata, taille)
    return HttpResponse("Recommendations are being loaded in the background.")
    liste_complete = []
    for elem in l:
        liste_complete.append(get_restaurant_id(elem[0],restaurant_metadata))
    return liste_complete