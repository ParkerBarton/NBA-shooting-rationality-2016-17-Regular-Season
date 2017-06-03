import os, csv
import numpy as np
import pandas as pd
from pymongo import MongoClient
import matplotlib.pyplot as plt

#I loaded the data from the mongodb database, you can also load from the generated csv files with saved shot data
#use the shot data from other 29 teams as training set
#load the data for the other 29 teams from the database
from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client.NBA_shot_log
team = 'GSW'
train_data = []
test_data = []
os.chdir('C:\PhD work of hao\New folder\NBA\Project-Team shoot rationality')
filename = 'NBA team name vs abbreviation.csv'
with open(filename, "r") as f:
    f = csv.DictReader(f, delimiter = ',')
    for i, line in enumerate(f):
        Team_name = line['Abbreviation/Acronym']
        if Team_name != team:
            collection = db[Team_name]
            shots_temp = collection.find({})
            for shot in shots_temp:
                train_data.append(shot)
        else:
            collection = db[Team_name]
            shots_temp = collection.find({})
            for shot in shots_temp:
                test_data.append(shot)

train_data = pd.DataFrame(train_data)
train_data = train_data[train_data['shot distance (feet)']!= '']
test_data = pd.DataFrame(test_data)
test_data = test_data[test_data['shot distance (feet)']!= '']

#####################
#select the features for the train and test data
from parse_data import FactorizeCategoricalVariable
train = pd.DataFrame()
train['shot distance'] = train_data['shot distance (feet)'].astype(float)
train['player percentage'] = train_data['player percentage'].astype(float)
train['shot angle'] = train_data['shot angle (degree)'].astype(float)
train['points'] = train_data['points'].astype(int)
train = pd.concat([train,FactorizeCategoricalVariable(train_data,'shot type')],axis=1)
train['shot outcome'] = train_data['current shot outcome'].astype(int)

test = pd.DataFrame()
test['player percentage'] = test_data['player percentage'].astype(float)
test['shot distance'] = test_data['shot distance (feet)'].astype(float)
test['shot angle'] = test_data['shot angle (degree)'].astype(float)
test['points'] = test_data['points'].astype(int)
test = pd.concat([test,FactorizeCategoricalVariable(test_data,'shot type')],axis=1)
test['shot outcome'] = test_data['current shot outcome'].astype(int)

train_x = train.drop(['shot outcome'],1).as_matrix()
train_y = train['shot outcome'].as_matrix()

test_x = test.drop(['shot outcome'],1).as_matrix()
test_y = test['shot outcome'].as_matrix()

########
#feature selection
'''
from sklearn.feature_selection import SelectPercentile, f_classif
selector = SelectPercentile(f_classif, percentile = 50)
selector.fit(train_x, train_y)
train_x = selector.transform(train_x)
test_x = selector.transform(test_x)
'''

########
#building estimators
'''
#random forest classifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_curve, auc

max_depth = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
opt_rfc = []
for depth in max_depth:
    rfc = RandomForestClassifier(n_jobs=-1 ,n_estimators=100, max_depth  = depth, min_samples_split =5)
    rfc.fit(train_x, train_y)
    pred_rfc = rfc.predict_proba(test_x)[:,1]                                 
    fpr, tpr, threshold = roc_curve(test_y, pred_rfc)
    roc_auc = auc(fpr, tpr)
    opt_rfc.append(roc_auc)
import datetime
print('random forest done')
print(datetime.datetime.now())
plt.figure()
lw = 2
plt.plot(max_depth, opt_rfc, color='darkorange',
         lw=lw)
plt.title('Parameter tuning for random forest')
plt.xlabel('max tree depth')
plt.ylabel('Auc score of prediction for '+team )
plt.show()'''

#gradient boosted tree
'''from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_curve, auc
opt_GBC = []
max_depth = [2,3,4,5]
n_estimator = [10,20,30,50,70,100]
opt_GBC = []
for i,n_est in enumerate(n_estimator):
    opt_temp = []
    for k, depth in enumerate(max_depth):
        GBC = GradientBoostingClassifier(n_estimators = n_est, max_depth = depth,min_samples_split =5)
        GBC.fit(train_x, train_y)
        pred_GBC = GBC.predict_proba(test_x)[:,1]
        fpr, tpr, threshold = roc_curve(test_y, pred_GBC)
        roc_auc = auc(fpr, tpr)
        opt_temp.append(roc_auc)
    opt_GBC.append(opt_temp)
opt_GBC = np.asarray(opt_GBC)
plt.figure()
plot = plt.contourf(max_depth,n_estimator,opt_GBC)
plt.title('Parameter tuning for Gradient Boosted Trees')
plt.xlabel('max_depth')
plt.ylabel('n_estimator')
bar = plt.colorbar(plot)
bar.ax.set_ylabel('GBC AUC score')
import datetime
print('GBC done')
print(datetime.datetime.now())
plt.show()'''

#Adaboost classifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
rfc = LogisticRegression()
n_estimator = [2,3,4,5]
learning_rate = [1.025,1.05,1.075,1.1,1.125,1.15,1.175,1.2,1.225,1.25]
#n_estimator = [2,4]
#learning_rate = [1.05,1.1,1.2]
opt_adab = []
for i,n_est in enumerate(n_estimator):
    opt_temp = []
    for k, learn_rate in enumerate(learning_rate):
        adab = AdaBoostClassifier(base_estimator = rfc, learning_rate = learn_rate, n_estimators = n_est)
        adab.fit(train_x, train_y)
        pred_adab = adab.predict_proba(test_x)[:,1]
        fpr, tpr, threshold = roc_curve(test_y, pred_adab)
        roc_auc = auc(fpr, tpr)
        opt_temp.append(roc_auc)
    opt_adab.append(opt_temp)
opt_adab = np.asarray(opt_adab)
plt.figure()
plot = plt.contourf(learning_rate,n_estimator,opt_adab)
plt.title('Parameter tuning for Adaboost')
plt.xlabel('learning_rate')
plt.ylabel('n_estimator')
bar = plt.colorbar(plot)
bar.ax.set_ylabel('Adaboost AUC score')
import datetime
print('adaboost forest done')
print(datetime.datetime.now())
plt.show()


