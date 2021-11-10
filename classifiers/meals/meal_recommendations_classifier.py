import math
import os

from sklearn.neighbors import NearestNeighbors
import numpy as np
import pandas as pd
from models.meal_nutrients import RequiredMealNutrients

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_recommendations(nutrients: RequiredMealNutrients):
    meals = pd.read_csv(ROOT_DIR + '/we_made_it_bitchez.tsv', sep='\t', chunksize=500000)
    x = meals.get_chunk(500000)[['calories', 'proteins', 'fats', 'carbohydrates']]
    meal_rows = x

    nbrs = NearestNeighbors(n_neighbors=5, algorithm='auto', metric='euclidean').fit(x)

    required_nutrients = {'calories': [nutrients.calories], 'proteins': [nutrients.proteins],
                          'fats': [nutrients.fats], 'carbohydrates': [nutrients.carbohydrates]}

    df_required_nutrients = pd.DataFrame(required_nutrients)

    distances, indexes = nbrs.kneighbors(df_required_nutrients)

    meal_names = []

    for i in indexes[0]:
        meal_names.append({
            # 'name': meal_rows.loc[i]['title'],
            'calories': float(meal_rows.loc[i]['calories']),
            'proteins': float(meal_rows.loc[i]['proteins']),
            'fats': float(meal_rows.loc[i]['fats']),
            'carbohydrates': float(meal_rows.loc[i]['carbohydrates'])
        })

    return meal_names, distances


def euclidean_distance(row, meal_rows, meal):
    inner_value = 0
    for k in meal_rows:
        inner_value += (row[k] - meal[k]) ** 2
    return math.sqrt(inner_value)
