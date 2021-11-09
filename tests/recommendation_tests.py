# Test subject 1:
# Dataset ID: 190423
# Age range: 18-39
# Age: 20
# Height: 163.00 cm -> 1.63 m
# Weight: 183.80 Kg
# BMI: 36.50
# Sex: Female
# Exercise: HARD

# Test subject 2:
# Dataset ID: 316463
# Age range: 40-59
# Age: 50
# Height: 161.90 cm -> 1.015 m
# Weight: 76.40 Kg
# BMI: 29.10
# Sex: Female
# Exercise: Light

# Test subject 3:
# Dataset ID: 629795
# Age range: 60-75
# Age: 62
# Height: 143.70 cm -> 1.437 m
# Weight: 50.40 Kg
# BMI: 24.40
# Sex: Male
# Exercise: SEDENTARY
from models.meal_nutrients import RequiredMealNutrients
from models.recommendation_enums import *

from services.meal_recomentdations_service import *


def generate_test_cases():
    subject_1_nutrients = get_user_required_meal_nutrients(Sex.FEMALE.value, 183.80, 163, 20)
    subject_1_recommendations = get_meal_recommendation_list(Sex.FEMALE.value, 183.80, 163, 20)

    subject_2_nutrients = get_user_required_meal_nutrients(Sex.FEMALE.value, 76.40, 161.90, 50)
    subject_2_recommendations = get_meal_recommendation_list(Sex.FEMALE.value, 76.40, 161.90, 50)

    subject_3_nutrients = get_user_required_meal_nutrients(Sex.MALE.value, 50.40, 143.70, 62)
    subject_3_recommendations = get_meal_recommendation_list(Sex.MALE.value, 50.40, 143.70, 62)

    print_experiment(subject_1_nutrients, subject_1_recommendations)
    print_experiment(subject_2_nutrients, subject_2_recommendations)
    print_experiment(subject_3_nutrients, subject_3_recommendations)


def print_experiment(nutrients: RequiredMealNutrients, recommendations: []):
    print('User Required Calories: ' + str(nutrients.calories))
    print('User Required Proteins: ' + str(nutrients.proteins))
    print('User Required Fats: ' + str(nutrients.fats))
    print('User Required Carbohydrates: ' + str(nutrients.carbohydrates))

    for dish in recommendations:
        print(dish)
    print('====================================================================')


if __name__ == "__main__":
    generate_test_cases()
