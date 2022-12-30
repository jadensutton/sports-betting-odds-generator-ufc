import sklearn
import pickle

import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import log_loss

predict = 'result'

data = pd.read_csv('data/train_v3.csv', sep=',')

X = np.array(data.drop([predict], 1))
y = np.array(data[predict])

best = 1
for n in range(10):
    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(X, y, test_size = 0.2)

    model = RandomForestClassifier(n_estimators=500)
    model.fit(x_train, y_train)

    y_pred = [y[1] for y in model.predict_proba(x_test)]

    acc = model.score(x_test, y_test)
    lg_loss = log_loss(y_test, y_pred)
    print('Model Accuracy: {}%  Model Log Loss: {}'.format(str (acc * 100), lg_loss))

    if lg_loss < best:
        best = lg_loss
        with open('models/model_v3.pickle', 'wb') as f:
            pickle.dump(model, f)

print('Final model log loss: {}'.format(best))
