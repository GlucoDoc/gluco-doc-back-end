FROM python:3.9-slim-buster

ENV MODEL_DIR=/
ENV MODEL_FILE=trained_model.joblib

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

CMD mkdir classifier
CMD mkdir apicontroller

COPY classifier/data_processor.py ./classifier/data_processor.py
COPY classifier/classifier.py ./classifier/classifier.py
COPY api/apicontroller.py ./apicontroller.py