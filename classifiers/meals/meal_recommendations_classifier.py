import json
import math
import os

from sklearn.neighbors import NearestNeighbors
import pandas as pd

from models.meal_nutrients import RequiredMealNutrients

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_recommendations(nutrients: RequiredMealNutrients):
    meals = pd.read_csv(ROOT_DIR + '/processed_meals.tsv', sep='\t', chunksize=500000)
    first_chunk = meals.get_chunk(500000)
    x = first_chunk[['calories', 'proteins', 'fats', 'carbohydrates']]
    meal_rows = first_chunk[['calories', 'proteins', 'fats', 'carbohydrates', 'meals']]

    nbrs = NearestNeighbors(n_neighbors=5, algorithm='auto', metric='euclidean').fit(x)

    required_nutrients = {'calories': [nutrients.calories], 'proteins': [nutrients.proteins],
                          'fats': [nutrients.fats], 'carbohydrates': [nutrients.carbohydrates]}

    df_required_nutrients = pd.DataFrame(required_nutrients)

    distances, indexes = nbrs.kneighbors(df_required_nutrients)

    meal_names = []

    for i in indexes[0]:
        meal_dishes = json.loads(meal_rows.loc[i]['meals'])
        names = ''
        for meal in meal_dishes:
            max_calories = 0
            for dish in meal['dishes']:
                dish_calories = float(filter_totals('Calories', dish['nutritions']))
                if dish_calories > max_calories:
                    max_calories = dish_calories
                    names += dish['name']
                    names += ' '

        meal_names.append({
            'name': names,
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


def filter_totals(property_name, totals_json):
    filtered_values = list(filter(lambda total: total['name'] == property_name, totals_json))
    return filtered_values[0]['value'].replace(',', '') if len(filtered_values) > 0 else -1
