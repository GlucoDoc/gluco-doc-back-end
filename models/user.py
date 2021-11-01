class User:
    def __init__(self, user_id, model, last_model_date, user_email, locale, sex=None, weight=None, height_m=None,
                 height_cm=None, activity_factor=None, profile_modification_date=None):
        self.user_id = user_id
        self.model = model
        self.last_model_date = last_model_date
        self.user_email = user_email
        self.locale = locale
        self.sex = sex
        self.weight = weight
        self.height_m = height_m
        self.height_cm = height_cm
        self.activity_factor = activity_factor
        self.profile_modification_date = profile_modification_date
