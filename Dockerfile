FROM python:3.9-slim-buster

ENV MODEL_DIR=/
ENV MODEL_FILE=trained_model.joblib

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

CMD mkdir classifier
CMD mkdir apicontroller
CMD mkdir notifications
CMD mkdir models

COPY classifiers/egvs/egvs_data_processor.py ./classifier/data_processor.py
COPY classifiers/egvs/egvs_classifier.py ./classifier/classifier.py
COPY api/apicontroller.py ./apicontroller.py
COPY api/default_api_page.html ./default_api_page.html
COPY services/access_token_service.py ./notifications/access_token.py
COPY services/credentials.py ./notifications/credentials.py
COPY services/email_util_service.py ./notifications/email_util.py
COPY services/notification_service.py ./notifications/notification.py
COPY models/user.py ./models/user.py