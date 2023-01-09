def train(train_x_path: InputPath("pickle"),
train_y_path: InputPath("pickle"),
test_x_path: InputPath("pickle"),
test_y_path: InputPath("pickle"), 
model_path: OutputPath("dump")):
    import pandas as pd 
    import os, pickle
    from sklearn.tree import DecisionTreeRegressor
    import lightgbm as lgb
    from joblib import dump
    import sklearn.metrics as metrics
    #import mlflow 

    with open(train_x_path, mode = "rb") as f:
        X_train = pickle.load(f)
    with open(train_y_path, mode = "rb") as f:
        y_train = pickle.load(f)
    with open(test_x_path, mode = "rb") as f:
        X_test = pickle.load(f)
    with open(test_y_path, mode = "rb") as f:
        y_test = pickle.load(f)

    train_set = lgb.Dataset(X_train, y_train)
    lgb_eval = lgb.Dataset(X_test, y_test, reference=train_set)
    # define our parameters 
    params = {
    'task': 'train', 
    'boosting': 'gbdt',
    'objective': 'regression',
    'num_leaves': 10,
    'learnnig_rage': 0.05,
    'metric': {'l2','l1'},
    'verbose': -1
    }
    model = lgb.train(params, train_set, 
    num_boost_round=100, 
    valid_sets = lgb_eval,
    early_stopping_rounds=10)

# https://www.datatechnotes.com/2022/03/lightgbm-regression-example-in-python.html

    with open(model_path, mode = "wb") as f:
        dump(model, f)

    # evaluate our model
    y_pred = model.predict(X_test)
    #metrics.r2_score(y_test, y_pred)
    lgb_mse = metrics.mean_squared_error(y_test, y_pred)
    # output here to compare so that we can then decide which to use
    