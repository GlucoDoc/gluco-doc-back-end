import json
import os

from dateutil import parser

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def process_data(json_string_data):
    print("processing json to csv...")

    new_file = ROOT_DIR + '/processed_egvs.csv'

    loaded_json = json.loads(json_string_data)

    export = open(new_file, "w")
    export.write("\"weekday\",\"time\",\"gl\",\"state\"\n")

    value_to_use = "value"

    for egv in loaded_json['egvs']:

        this_datetime = parser.parse(egv['displayTime'])

        def get_class():
            if (loaded_json['unit'] == "mg/dL" and float(egv[value_to_use]) < 70) or (
                    loaded_json['unit'] == "mmol/L" and float(egv[value_to_use]) < 3.9):
                return "Hypoglycemia"
            elif (loaded_json['unit'] == "mg/dL" and float(egv[value_to_use]) > 179) or (
                    loaded_json['unit'] == "mmol/L" and float(egv[value_to_use]) > 9.9):
                return "Hyperglycemia"
            else:
                return "normal"

        export.write(str(this_datetime.weekday()) + "," + str(this_datetime.hour) + "," + str(
            egv[value_to_use]) + "," + get_class() + "\n")

    print("Done processing json to csv!")
