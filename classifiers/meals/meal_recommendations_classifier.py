import os

from sklearn.neighbors import NearestNeighbors
import numpy as np
import pandas as pd
from models.meal_nutrients import RequiredMealNutrients

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_recommendations(nutrients: RequiredMealNutrients):
    meals = pd.read_csv(ROOT_DIR + '/meals.csv')

    print("processing...")

    for i, row in meals.iterrows():
        meals.at[i, 'Protein/g'] = int(meals.at[i, 'Protein/g']) * int(meals.at[i, 'weightPerServing'])
        meals.at[i, 'Fat/g'] = int(meals.at[i, 'Fat/g']) * int(meals.at[i, 'weightPerServing'])
        meals.at[i, 'Carbohydrates/g'] = int(meals.at[i, 'Carbohydrates/g']) * int(meals.at[i, 'weightPerServing'])

    x = meals[['calories', 'Protein/g', 'Fat/g', 'Carbohydrates/g']]
    meal_rows = meals[['id', 'title', 'calories', 'Protein/g', 'Fat/g', 'Carbohydrates/g']]

    nbrs = NearestNeighbors(n_neighbors=5, algorithm='auto', metric='euclidean').fit(x)

    required_nutrients = {'calories': [nutrients.calories / 3], 'Protein/g': [nutrients.proteins / 3],
                          'Fat/g': [nutrients.fats / 3], 'Carbohydrates/g': [nutrients.carbohydrates / 3]}

    df_required_nutrients = pd.DataFrame(required_nutrients)

    distances, indexes = nbrs.kneighbors(df_required_nutrients)

    meal_names = []

    for i in indexes[0]:
        meal_names.append({
            'id': int(meal_rows.loc[i]['id']),
            'name': meal_rows.loc[i]['title'],
            'calories': float(meal_rows.loc[i]['calories']),
            'Protein/g': float(meal_rows.loc[i]['Protein/g']),
            'Fat/g': float(meal_rows.loc[i]['Fat/g']),
            'Carbohydrates/g': float(meal_rows.loc[i]['Carbohydrates/g'])
        })

    return meal_names
