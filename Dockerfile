FROM jupyter/scipy-notebook

ENV MODEL_DIR=/
ENV MODEL_FILE=trained_model.joblib

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY classifier/classifier.py ./classifier.py
COPY api/apicontroller.py ./apicontroller.py

CMD docker run -it -p 5000:5000 classifier-img python3 apicontroller.py