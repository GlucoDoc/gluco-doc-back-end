FROM python:3.9-slim-buster

ENV MODEL_DIR=/
ENV MODEL_FILE=trained_model.joblib

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

CMD mkdir classifier
CMD mkdir apicontroller
CMD mkdir notifications
CMD mkdir models

COPY classifier/data_processor.py ./classifier/data_processor.py
COPY classifier/classifier.py ./classifier/classifier.py
COPY api/apicontroller.py ./apicontroller.py
COPY api/default_api_page.html ./default_api_page.html
COPY notifications/access_token.py ./notifications/access_token.py
COPY notifications/credentials.py ./notifications/credentials.py
COPY notifications/email_util.py ./notifications/email_util.py
COPY notifications/notification.py ./notifications/notification.py
COPY models/user.py ./models/user.py