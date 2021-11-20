import json
import math
import os
import pickle

from sklearn.neighbors import NearestNeighbors
import pandas as pd

from models.meal_nutrients import RequiredMealNutrients
from joblib import dump, load


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_recommendations(nutrients: RequiredMealNutrients):
    meals = pd.read_csv(ROOT_DIR + '/filtered_dataset.tsv', sep='\t')
    meal_rows = meals[['id', 'calories', 'proteins', 'fats', 'carbohydrates', 'meals']]

    nbrs = pickle.load(open(ROOT_DIR + '/meals_model.pkl', 'rb'))
    #nbrs = NearestNeighbors(n_neighbors=5, algorithm='auto', metric='euclidean').fit(x)

    required_nutrients = {'calories': [nutrients.calories], 'proteins': [nutrients.proteins],
                          'fats': [nutrients.fats], 'carbohydrates': [nutrients.carbohydrates]}

    df_required_nutrients = pd.DataFrame(required_nutrients)

    distances, indexes = nbrs.kneighbors(df_required_nutrients)

    meal_names = []

    for i in indexes[0]:
        meal_dishes = json.loads(meal_rows.loc[i]['meals'])
        names = ''
        max_calories = 0
        max_calorie_meal_index = 0
        max_calorie_dish_index = 0

        for meal_index in range(len(meal_dishes)):
            for dish_index in range(len(meal_dishes[meal_index]['dishes'])):
                dish_calories = float(filter_totals('Calories', meal_dishes[meal_index]['dishes'][dish_index]['nutritions']))
                if dish_calories > max_calories:
                    max_calories = dish_calories
                    max_calorie_meal_index = meal_index
                    max_calorie_dish_index = dish_index

        names += meal_dishes[max_calorie_meal_index]['dishes'][max_calorie_dish_index]['name']

        meal_names.append({
            'id': str(i),
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
