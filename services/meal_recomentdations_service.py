from enum import Enum

from models.meal_nutrients import get_required_meal_nutrients_from_calories
from classifiers.meals.meal_recommendations_classifier import get_recommendations


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
    return (weight / (height_m ** 2)) * 100


# Harris Benedict’s equation
def calculate_basal_calories(user_sex, weight, height_cm, age, activity_factor):
    basal_calories = 0

    if user_sex == Sex.MALE.value:
        basal_calories = 10 * weight + 6.25 * height_cm - 5 * age + AgeFactor.MALE.value
    elif user_sex == Sex.FEMALE.value:
        basal_calories = 10 * weight + 6.25 * height_cm - 5 * age + AgeFactor.FEMALE.value

    basal_calories = basal_calories * activity_factor

    return basal_calories


def get_user_required_meal_nutrients(user_sex, weight, height_cm, age, activity_factor):
    user_basal_calories = calculate_basal_calories(user_sex, weight, height_cm, age, activity_factor)
    nutrients = get_required_meal_nutrients_from_calories(user_basal_calories)
    nutrients.fats = nutrients.calories * 0.15 if calculate_bmi(weight, height_cm) >= 25 else nutrients.fats
    nutrients.proteins = weight * 0.8
    return nutrients


def get_meal_recommendation_list(user_sex, weight, height_cm, age, activity_factor):
    required_meal_nutrients = get_user_required_meal_nutrients(user_sex, weight, height_cm, age, activity_factor)
    return get_recommendations(required_meal_nutrients)