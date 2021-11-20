import pandas as pd
import csv
import json
import os
import pandas as pd

data_file = pd.read_csv("processed_meals.tsv", sep='\t', encoding='utf-8')
indexes = []

filtered_dataset = data_file.loc[data_file['meals'].str.contains('"meal":"breakfast"', case=False)]
filtered_dataset = filtered_dataset.loc[data_file['meals'].str.contains('"meal":"dinner"', case=False)]
filtered_dataset = filtered_dataset.loc[data_file['meals'].str.contains('"meal":"lunch"', case=False)]
print(filtered_dataset)

pd.DataFrame(filtered_dataset).to_csv('filtered_dataset.tsv', sep='\t', encoding='utf-8', index=False)

print('finished processing')
