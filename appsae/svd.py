import difflib
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import chart_studio.plotly as py
import chart_studio
import os


def get_restaurant_id(restaurant_name, metadata):
    """
    Gets the book ID for a book title based on the closest match in the metadata dataframe.
    """

    existing_names = list(metadata['nom'].values)
    closest_names = difflib.get_close_matches(restaurant_name, existing_names)
    restaurant_id = metadata[metadata['nom'] == closest_names[0]]['id'].values[0]
    return restaurant_id


def get_restaurant_info(restaurant_id, metadata):
    """
    Returns some basic information about a book given the book id and the metadata dataframe.
    """

    restaurant_info = metadata[metadata['id'] == restaurant_id][['id', 'nom']]
    return restaurant_info.to_dict(orient='records')


def predict_review(user_id, restaurant_name, model, metadata):
    """
    Predicts the review (on a scale of 1-5) that a user would assign to a specific book.
    """

    restaurant_id = get_restaurant_id(restaurant_name, metadata)
    review_prediction = model.predict(uid=user_id, iid=restaurant_id)
    return review_prediction.est


def generate_recommendation(user_id, model, metadata, thresh=3.5):
    """
    Generates a book recommendation for a user based on a rating threshold. Only
    books with a predicted rating at or above the threshold will be recommended
    """

    restaurant_names = list(metadata['nom'].values)
    random.shuffle(restaurant_names)

    for restaurant_name in restaurant_names:
        rating = predict_review(user_id, restaurant_name, model, metadata)
        if rating >= thresh:
            restaurant_id = get_restaurant_id(restaurant_name, metadata)
            return get_restaurant_info(restaurant_id, metadata)


def testMatteoRecommandation(user_id, model, metadata):
    """

    @param user_id:
    @param model:
    @param metadata:
    @return:
    """
    restaurant_names = list(metadata['nom'].values)
    dico_all = {}
    cpt = 0

    for restaurant_name in restaurant_names:
        rating = predict_review(user_id, restaurant_name, model, metadata)
        cpt+=1
        if (cpt < 100):
            print(str(restaurant_name) + "  " + str(rating))
