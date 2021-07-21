import os

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.metrics import classification_report
from joblib import dump

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def train_model():
    print('Training Model...')

    data = pd.read_csv(ROOT_DIR + '/processed_egvs.csv')

    X = data[['weekday', 'time']]  # Features
    y = data['state']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4)

    #print(X_test.head(5))
    # Create a Gaussian Classifier
    model = RandomForestClassifier(n_estimators=100)

    # Train the model using the training sets y_predict=clf.predict(X_test)
    model.fit(X_train, y_train)

    y_predictions = model.predict(X_test)

    print("\nAccuracy:", metrics.accuracy_score(y_test, y_predictions))

    # print('\n Confusion Matrix:\n', metrics.confusion_matrix(y_test, y_predictions))
    #
    # print('\n', classification_report(y_test, y_predictions, zero_division=0))

    dump(model, 'trained_model.joblib')
    print('\nFinished training and dumping Model...')


if __name__ == '__main__':
    train_model()
