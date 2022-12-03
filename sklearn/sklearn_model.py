from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from joblib import dump
from sklearn.datasets import load_boston
import pandas as pd

boston_df = load_boston()
boston = pd.DataFrame(boston_df.data, columns=boston_df.feature_names)
X=boston.iloc[:,0:-1]
y=boston.iloc[:,-1]

# split into train and test sets 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=42)

regressor = DecisionTreeRegressor(random_state=42, max_depth=5)
regressor.fit(X_train, y_train)

# how well does it do? 

# save our model results 
dump(regressor, 'boston_model.joblib')