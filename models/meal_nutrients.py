
RECOMMENDED_CARBOHYDRATE_FACTOR = 0.45
RECOMMENDED_PROTEIN_FACTOR = 0.15
RECOMMENDED_FATS_FACTOR = 0.3


class RequiredMealNutrients:
    calories = 0
    carbohydrates = 0
    protein = 0
    fats = 0

    def __init__(self, calories, carbohydrates, proteins, fats):
        self.calories = calories
        self.carbohydrates = carbohydrates
        self.proteins = proteins
        self.fats = fats


def get_required_meal_nutrients_from_calories(calories):
    carbohydrates = calories * RECOMMENDED_CARBOHYDRATE_FACTOR
    proteins = calories * RECOMMENDED_PROTEIN_FACTOR
    fats = calories * RECOMMENDED_FATS_FACTOR
    return RequiredMealNutrients(calories, carbohydrates, proteins, fats)
