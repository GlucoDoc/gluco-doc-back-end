import json
import math
import os
import pickle

from sklearn.neighbors import NearestNeighbors
import pandas as pd

from models.meal_nutrients import RequiredMealNutrients
from joblib import dump, load

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def train_meal_model():
    meals = pd.read_csv(ROOT_DIR + '/filtered_dataset.tsv', sep='\t')
    x = meals[['calories', 'proteins', 'fats', 'carbohydrates']]
    file = open(ROOT_DIR + '/meals_model.pkl', 'wb')
    nbrs = NearestNeighbors(n_neighbors=5, algorithm='auto', metric='euclidean').fit(x)
    pickle.dump(nbrs, file)


def get_recommendations(nutrients: RequiredMealNutrients, time_hour):
    meals = pd.read_csv(ROOT_DIR + '/filtered_dataset.tsv', sep='\t')
    meal_rows = meals[['id', 'calories', 'proteins', 'fats', 'carbohydrates', 'meals']]

    nbrs = pickle.load(open(ROOT_DIR + '/meals_model.pkl', 'rb'))

    required_nutrients = {'calories': [nutrients.calories], 'proteins': [nutrients.proteins],
                          'fats': [nutrients.fats], 'carbohydrates': [nutrients.carbohydrates]}

    df_required_nutrients = pd.DataFrame(required_nutrients)

    distances, indexes = nbrs.kneighbors(df_required_nutrients)

    meal_names = []

    meal_type = ''

    if time_hour < 12:
        meal_type = 'Breakfast'
    elif 11 < time_hour < 18:
        meal_type = 'Lunch'
    else:
        meal_type = 'Dinner'

    for i in indexes[0]:
        meal_dishes = json.loads(meal_rows.loc[i]['meals'])
        names = ''
        max_calories = 0
        max_calorie_meal_index = 0
        max_calorie_dish_index = 0
        max_nutrition = None

        for meal_index in range(len(meal_dishes)):

            if meal_dishes[meal_index]['meal'] == meal_type:
                for dish_index in range(len(meal_dishes[meal_index]['dishes'])):
                    dish_calories = float(
                        filter_totals('Calories', meal_dishes[meal_index]['dishes'][dish_index]['nutritions']))
                    if dish_calories > max_calories:
                        max_calories = dish_calories
                        max_calorie_meal_index = meal_index
                        max_calorie_dish_index = dish_index

        names += meal_dishes[max_calorie_meal_index]['dishes'][max_calorie_dish_index]['name']
        max_nutrition = meal_dishes[max_calorie_meal_index]['dishes'][max_calorie_dish_index]['nutritions']

        meal_names.append({
            'id': str(i),
            'name': names,
            'calories': float(max_nutrition[0]['value'].replace(',', '')),
            'proteins': float(max_nutrition[3]['value']),
            'fats': float(max_nutrition[2]['value']),
            'carbohydrates': float(max_nutrition[1]['value'])
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
