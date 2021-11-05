import os

from sklearn.neighbors import NearestNeighbors
import numpy as np
import pandas as pd
from models.meal_nutrients import RequiredMealNutrients

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_recommendations(nutrients: RequiredMealNutrients):
    meals = pd.read_csv(ROOT_DIR + './meals.csv')

    x = meals[['calories', 'Protein/g', 'Fat/g', 'Carbohydrates/g']]
    meal_rows = meals[['id', 'title']]
    nbrs = NearestNeighbors(n_neighbors=5, algorithm='auto').fit(x.sample(frac=0.50))

    required_nutrients = {'calories': [nutrients.calories / 3], 'Protein/g': [nutrients.proteins / 3],
                          'Fat/g': [nutrients.fats / 3], 'Carbohydrates/g': [nutrients.carbohydrates / 3]}

    df_required_nutrients = pd.DataFrame(required_nutrients)

    distances, indexes = nbrs.kneighbors(df_required_nutrients)

    meal_names = []

    for i in indexes[0]:
        meal_names.append({
            'id': int(meal_rows.loc[i]['id']),
            'name': meal_rows.loc[i]['title']
        })

    return meal_names
