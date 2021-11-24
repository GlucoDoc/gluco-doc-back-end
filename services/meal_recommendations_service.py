import json
from enum import Enum

import pandas as pd
from bson import Decimal128

from models.meal_nutrients import get_required_meal_nutrients_from_calories
from classifiers.meals.meal_recommendations_classifier import get_recommendations, train_meal_model


class Sex(Enum):
    MALE = 1
    FEMALE = 2


class ActivityFactor(Enum):
    SEDENTARY = 1.2
    LIGHT = 1.375
    MEDIUM = 1.55
    HARD = 1.725


class AgeFactor(Enum):
    MALE = 5
    FEMALE = -161


# weight in kg
# weight = 54.4311
# height in meters
# height_m = 1.7

# height in cm
# height_cm = height_m * 100

# age in years
# age = 23

sex = Sex.MALE.value


def calculate_bmi(weight, height_m):
    # Formula: weight (kg) / [height (m)]^2
    return float(weight / height_m ** 2.0) * float(100)


# Harris Benedict’s equation
def calculate_basal_calories(user_sex, weight, height_cm, age, activity_factor):
    basal_calories = 0

    if user_sex == Sex.MALE.value:
        basal_calories = 10.0 * weight + 6.25 * height_cm - 5.0 * age + AgeFactor.MALE.value
    elif user_sex == Sex.FEMALE.value:
        basal_calories = 10.0 * weight + 6.25 * height_cm - 5.0 * age + AgeFactor.FEMALE.value

    basal_calories = basal_calories * activity_factor

    return basal_calories


def get_user_required_meal_nutrients(user_sex, weight, height_cm, age, activity_factor):
    user_basal_calories = calculate_basal_calories(user_sex, weight, height_cm, age, activity_factor)
    nutrients = get_required_meal_nutrients_from_calories(user_basal_calories)
    nutrients.fats = nutrients.calories * 0.15 if calculate_bmi(weight, height_cm) >= 25 else nutrients.fats
    nutrients.proteins = weight * 0.8
    return nutrients


def get_meal_recommendation_list(user_sex, weight, height_cm, age, activity_factor, time_hour):
    required_meal_nutrients = get_user_required_meal_nutrients(
        user_sex,
        convert_decimal128_to_float(weight),
        convert_decimal128_to_float(height_cm),
        age,
        activity_factor)
    return get_recommendations(required_meal_nutrients, time_hour)


def convert_decimal128_to_float(parameter) -> float:
    if isinstance(parameter, Decimal128):
        parameter = parameter.to_decimal()

    return float(parameter)


def generate_recommendation_email_content(meal_id, user):
    meal_tsv = pd.read_csv('../classifiers/meals/filtered_dataset.tsv', sep='\t')
    json_row = json.loads(meal_tsv.loc[int(meal_id)]['meals'])

    html_message = open("recommendation_templates/header_template.html", "r").read()
    meal_section = generate_dishes_html(json_row)

    if user.sex is not None and user.weight and user.height_cm and user.age:
        i = 0
        prev_factor = 0
        for factor in ActivityFactor:
            if i != 0 and prev_factor == user.activity_factor:
                recommendations, distances = get_meal_recommendation_list(user.sex, user.weight, user.height_cm,
                                                                          user.age, factor.value, 1)
                meal_section += open("recommendation_templates/activity_title_template.html", "r").read().replace(
                    '{title}', 'If you do ' + str(factor.name).lower() + ' exercise, you could eat...')
                next_json_row = json.loads(meal_tsv.loc[int(recommendations[0]['id'])]['meals'])

                meal_section += generate_dishes_html(next_json_row)
                break
            prev_factor = factor.value
            i += 1

    html_message = html_message.replace('{content}', meal_section)

    html_message += open("recommendation_templates/footer_template.html", "r").read()

    return html_message


def generate_dishes_html(meal_recommendation):
    macronutrients_to_display = ['Calories', 'Carbs', 'Carbohydrates', 'Fat', 'Fats', 'Protein', 'Proteins']
    meal_section = ''
    for meal in meal_recommendation:
        meal_section_temp = open("recommendation_templates/meal_section_template.html", "r").read().replace("\n", " ") \
            .replace("\t", " ")
        dishes = ''
        rows = ''
        i = 0
        dish_count = len(meal['dishes'])
        card1 = ''
        card2 = ''
        for dish in meal['dishes']:
            nutritional_facts = ''
            for nutrition in dish['nutritions']:
                if nutrition['name'] in macronutrients_to_display:
                    nutritional_facts += open("recommendation_templates/list_item_template.html", "r").read() \
                        .replace("\n", " ").replace("\t", " ").format(listItem=nutrition['name'],
                                                                      value=nutrition['value'])
            dishes = open("recommendation_templates/card_template.html", "r").read().replace("\n", " ").replace(
                "\t", " ").format(
                dishName=dish['name'], listItems=nutritional_facts)
            if dish_count == 1 and card1 == '':
                rows += open("recommendation_templates/card_row_template.html", "r").read().replace("\n",
                                                                                                    " ").replace(
                    "\t", " ").format(card1=dishes, card2='')
                card1 = ''
                card2 = ''
            else:
                if i % 2 == 0:
                    card1 += dishes
                else:
                    card2 += dishes
                    rows += open("recommendation_templates/card_row_template.html", "r").read().replace("\n",
                                                                                                        " ").replace(
                        "\t", " ").format(card1=card1, card2=card2)
                    card1 = ''
                    card2 = ''
            dish_count -= 1
            i += 1
        meal_section += meal_section_temp.format(title=meal['meal'], cards=rows)

    return meal_section
