FROM jupyter/scipy-notebook

ENV MODEL_DIR=/
ENV MODEL_FILE=trained_model.joblib

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY classifier/Processed_Data_Classified/184_Aleppo2017_processed.csv ./classifier/Processed_Data_Classified/184_Aleppo2017_processed.csv

COPY classifier/classifier.py ./classifier.py
COPY api/apicontroller.py ./apicontroller.py

RUN python3 classifier.py