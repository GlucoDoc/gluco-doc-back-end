# Test subject 1:
# Dataset ID: 190423
# Age range: 18-39
# Age: 20
# Height: 163.00 cm -> 1.63 m
# Weight: 183.80 Kg
# BMI: 36.50
# Sex: Female
# Exercise: HARD

# Test subject 1:
# Dataset ID: 190423
# Age range: 18-39
# Age: 20
# Height: 177.30 cm -> 1.77 m
# Weight: 92.70 Kg
# BMI: 29.50
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

from services.meal_recommendations_service import *


class TestSubject:
    def __init__(self, sex, weight, height, age, excercise_level):
        self.age = age
        self.height = height
        self.weight = weight
        self.sex = sex
        self.excercise_level = excercise_level


def generate_test_cases():
    subject_0 = TestSubject(Sex.FEMALE.value, 183.80, 163.00, 20, ActivityFactor.SEDENTARY.value)
    subject_0_nutrients = get_user_required_meal_nutrients(subject_0.sex, subject_0.weight, subject_0.height,
                                                           subject_0.age, subject_0.excercise_level)
    subject_0_recommendations, subject_0_distances = get_meal_recommendation_list(subject_0.sex, subject_0.weight,
                                                                                  subject_0.height, subject_0.age,
                                                                                  subject_0.excercise_level)

    subject_1 = TestSubject(Sex.FEMALE.value, 92.70, 177.30, 20, ActivityFactor.HARD.value)
    subject_1_nutrients = get_user_required_meal_nutrients(subject_1.sex, subject_1.weight, subject_1.height,
                                                           subject_1.age, subject_1.excercise_level)
    subject_1_recommendations, subject_1_distances = get_meal_recommendation_list(subject_1.sex, subject_1.weight,
                                                                                  subject_1.height, subject_1.age,
                                                                                  subject_1.excercise_level)

    subject_2 = TestSubject(Sex.FEMALE.value, 76.40, 161.90, 50, ActivityFactor.LIGHT.value)
    subject_2_nutrients = get_user_required_meal_nutrients(subject_2.sex, subject_2.weight, subject_2.height,
                                                           subject_2.age, subject_2.excercise_level)
    subject_2_recommendations, subject_2_distances = get_meal_recommendation_list(subject_2.sex, subject_2.weight,
                                                                                  subject_2.height, subject_2.age,
                                                                                  subject_2.excercise_level)

    subject_3 = TestSubject(Sex.MALE.value, 50.40, 143.70, 62, ActivityFactor.SEDENTARY.value)
    subject_3_nutrients = get_user_required_meal_nutrients(subject_3.sex, subject_3.weight, subject_3.height,
                                                           subject_3.age, subject_3.excercise_level)
    subject_3_recommendations, subject_3_distances = get_meal_recommendation_list(subject_3.sex, subject_3.weight,
                                                                                  subject_3.height, subject_3.age,
                                                                                  subject_3.excercise_level)

    print_experiment(subject_0, subject_0_nutrients, subject_0_recommendations, subject_0_distances)
    print_experiment(subject_1, subject_1_nutrients, subject_1_recommendations, subject_1_distances)
    print_experiment(subject_2, subject_2_nutrients, subject_2_recommendations, subject_2_distances)
    print_experiment(subject_3, subject_3_nutrients, subject_3_recommendations, subject_3_distances)


def print_experiment(subject: TestSubject, nutrients: RequiredMealNutrients, recommendations: [], distances):
    print_subject(subject)
    print('User Required Calories: ' + str(nutrients.calories))
    print('User Required Proteins: ' + str(nutrients.proteins))
    print('User Required Fats: ' + str(nutrients.fats))
    print('User Required Carbohydrates: ' + str(nutrients.carbohydrates))
    all_distances = distances[0].tolist()
    print('')

    for i, dish in enumerate(recommendations):
        print(str(i + 1) + ') Dish Name: ' + dish['name'])
        print('Calories: ' + str(dish['calories']))
        print('Proteins: ' + str(dish['proteins']))
        print('Fats: ' + str(dish['fats']))
        print('Carbohydrates: ' + str(dish['carbohydrates']))
        print('Euclidean Distance: ' + str(all_distances[i]))
        print('')

    print('')
    print('===============================================================================================')
    print('')


def print_subject(subject: TestSubject):
    print('Sex: ' + 'female' if subject.sex == Sex.FEMALE.value else 'male')
    print('Weight (kg): ' + str(subject.weight))
    print('Height (cm): ' + str(subject.height))
    print('Age: ' + str(subject.age))
    print('Activity Level: ' + str(subject.excercise_level))


if __name__ == "__main__":
    generate_test_cases()
