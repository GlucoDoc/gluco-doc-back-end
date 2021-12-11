FROM python:3.9-slim-buster

ENV MODEL_DIR=/
ENV MODEL_FILE=trained_model.joblib

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

#DIRS
CMD mkdir classifier
CMD mkdir apicontroller
CMD mkdir notifications
CMD mkdir models
CMD mkdir services

#CLASSIFIERS AND UTILS
COPY classifiers/egvs/egvs_data_processor.py ./classifier/data_processor.py
COPY classifiers/egvs/egvs_classifier.py ./classifier/classifier.py
COPY classifiers/meals/meal_recommendations_classifier.py ./classifier/meal_recommendations_classifier.py
COPY classifiers/meals/meals_model.pkl ./classifier/meals_model.pkl
COPY api/apicontroller.py ./apicontroller.py

#TEMPLATES
COPY api/default_api_page.html ./default_api_page.html
COPY api/recommendation_templates/activity_title_template.html ./activity_title_template.html
COPY api/recommendation_templates/card_row_template.html ./card_row_template.html
COPY api/recommendation_templates/card_template.html ./card_template.html
COPY api/recommendation_templates/footer_template.html ./footer_template.html
COPY api/recommendation_templates/full_template.html ./full_template.html
COPY api/recommendation_templates/header_template.html ./header_template.html
COPY api/recommendation_templates/list_item_template.html ./list_item_template.html
COPY api/recommendation_templates/meal_section_template.html ./meal_section_template.html
COPY api/recommendation_templates/recommendation_page.html ./recommendation_page.html

#SERVICES
COPY services/access_token_service.py ./notifications/access_token.py
COPY services/credentials.py ./notifications/credentials.py
COPY services/email_util_service.py ./notifications/email_util.py
COPY services/notification_service.py ./notifications/notification.py
COPY services/email_util_service.py ./notifications/email_util_service.py
COPY services/meal_recommendations_service.py ./services/meal_recommendations_service.py

#MODELS
COPY models/user.py ./models/user.py
COPY models/meal_nutrients.py ./models/meal_nutrients.py
COPY models/recommendation_enums.py ./models/recommendation_enums.py
