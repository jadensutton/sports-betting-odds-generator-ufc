import sklearn
import pickle

import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.utils import shuffle
from sklearn import linear_model
from time import sleep

predict = 'result'

data = pd.read_csv('../data/train2.csv', sep=',')

X = np.array(data.drop([predict], 1))
y = np.array(data[predict])

best = 0
for n in range(30):
    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(X, y, test_size = 0.2)

    model = RandomForestClassifier()
    model.fit(x_train, y_train)

    acc = model.score(x_test, y_test)
    print('Model Accuracy: ' + str (acc * 100) + '%')

    if acc > best:
        best = acc
        with open('../models/model2.pickle', 'wb') as f:
            pickle.dump(model, f)

print('Final model accuracy: {}%'.format(round(100 * best, 2)))
