import pandas as pd
import csv
import json
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_meals_dataframe():
    meals_dataframe = {'id': [], 'calories': [], 'proteins': [], 'fats': [], 'carbohydrates': [], 'meals': []}

    tsv_file = open("mfp-diaries.tsv")
    read_tsv = csv.reader(tsv_file, delimiter="\t")

    i = 0
    for row in read_tsv:
        i += 1
        totals_json = json.loads(str(row[3]))
        meals_json = json.loads(str(row[2]))
        total_calories, total_proteins, total_fats, total_carbohydrates, total_sugar = get_total_nutrients_from_json(totals_json['total'])

        if total_sugar != -1 and float(total_sugar) <= 30 and total_calories != -1 and total_proteins != -1 and total_fats != -1 and total_carbohydrates != -1:
            meals_dataframe['id'].append(i)
            meals_dataframe['calories'].append(total_calories)
            meals_dataframe['proteins'].append(total_proteins)
            meals_dataframe['fats'].append(total_fats)
            meals_dataframe['carbohydrates'].append(total_carbohydrates)
            a = json.dumps(meals_json, separators=(',', ':'))
            meals_dataframe['meals'].append(a)

    pd.DataFrame(meals_dataframe).to_csv('processed_meals.tsv', sep='\t', encoding='utf-8', index=False)


def get_total_nutrients_from_json(totals_json):
    calories = filter_totals('Calories', totals_json)
    protein = filter_totals('Protein', totals_json)
    fat = filter_totals('Fat', totals_json)
    carbs = filter_totals('Carbs', totals_json)
    sugar = filter_totals('Sugar', totals_json)

    return calories, protein, fat, carbs, sugar


def filter_totals(property_name, totals_json):
    filtered_values = list(filter(lambda total: total['name'] == property_name, totals_json))
    return filtered_values[0]['value'] if len(filtered_values) > 0 else -1


get_meals_dataframe()
