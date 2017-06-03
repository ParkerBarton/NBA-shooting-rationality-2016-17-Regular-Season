def shot_make_probablity(team,test_data):
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
    db = client.NBA_shot_log2
    train_data = []
    cdir_init = os.getcwd()
    filename = 'NBA team name vs abbreviation.csv'
    with open(filename, "r") as f:
        f = csv.DictReader(f, delimiter = ',')
        for i, line in enumerate(f):
            Team_name = line['Abbreviation/Acronym']
            if Team_name != team:
                collection = db[Team_name]
                shots_temp = collection.find({'time from last shot':{'$gte':6}})
                for shot in shots_temp:
                    train_data.append(shot)
            else:
                pass

    train_data = pd.DataFrame(train_data)
    train_data = train_data[train_data['shot distance (feet)']!= '']

    #####################
    #select the features for the train and test data
    from parse_data import FactorizeCategoricalVariable
    train = pd.DataFrame()
    train['shot distance'] = train_data['shot distance (feet)'].astype(float)
    #train_data['opponent previous shot'].replace('',999,inplace = True)
    #train['opponent previous shot'] = train_data['opponent previous shot'].astype(float)
    #train['player percentage'] = train_data['player percentage'].astype(float)
    train['shot angle'] = train_data['shot angle (degree)'].astype(float)
    train['time'] = train_data['time(s)'].astype(float)
    train['points'] = train_data['points'].astype(int)
    train = pd.concat([train,FactorizeCategoricalVariable(train_data,'shot zone')],axis=1)
    train = pd.concat([train,FactorizeCategoricalVariable(train_data,'player position')],axis=1)
    #train = pd.concat([train,FactorizeCategoricalVariable(train_data,'home game')],axis=1)
    train = pd.concat([train,FactorizeCategoricalVariable(train_data,'shot type')],axis=1)
    train['shot outcome'] = train_data['current shot outcome'].astype(int)

    test = pd.DataFrame()
    #test['player percentage'] = test_data['player percentage'].astype(float)
    #test_data['opponent previous shot'].replace('',999,inplace = True)
    #test['opponent previous shot'] = test_data['opponent previous shot'].astype(float)
    test['shot distance'] = test_data['shot distance (feet)'].astype(float)
    test['time'] = test_data['time(s)'].astype(float)
    test['shot angle'] = test_data['shot angle (degree)'].astype(float)
    test['points'] = test_data['points'].astype(int)
    test = pd.concat([test,FactorizeCategoricalVariable(test_data,'shot zone')],axis=1)
    test = pd.concat([test,FactorizeCategoricalVariable(test_data,'player position')],axis=1)
    #test = pd.concat([test,FactorizeCategoricalVariable(test_data,'home game')],axis=1)
    test = pd.concat([test,FactorizeCategoricalVariable(test_data,'shot type')],axis=1)
    test['shot outcome'] = test_data['current shot outcome'].astype(int)

    for column in train.columns:
        if column not in test.columns:
            train = train.drop([column],1)


    train_x = train.drop(['shot outcome'],1).as_matrix()
    train_y = train['shot outcome'].as_matrix()

    test_x = test.drop(['shot outcome'],1).as_matrix()
    test_y = test['shot outcome'].as_matrix()

    ########
    #feature selection
    
    from sklearn.feature_selection import SelectPercentile, f_classif
    selector = SelectPercentile(f_classif, percentile = 100)
    selector.fit(train_x, train_y)
    train_x = selector.transform(train_x)
    test_x = selector.transform(test_x)
   

    ########
    #building estimators
    #random forest classifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GridSearchCV
    rfc = RandomForestClassifier(n_jobs=-1 ,n_estimators=100, max_depth  = 6, min_samples_split =5)
    rfc.fit(train_x, train_y)
    pred_rfc = rfc.predict_proba(test_x)[:,1]
    feature_importance_rfc = rfc.feature_importances_
    feature_importance_rfc = pd.DataFrame(np.transpose(np.vstack((pd.DataFrame(train_x).columns,
                                     feature_importance_rfc))),columns=['featureName', 'importanceET'])
    feature_importance_rfc = feature_importance_rfc.sort_values(['importanceET'],ascending = 0)                                  
    import datetime
    print('random forest done')
    #print(datetime.datetime.now())
    #plot the roc curve for rfc classifier
    from sklearn.metrics import roc_curve, auc
    fpr, tpr, threshold = roc_curve(test_y, pred_rfc)
    roc_auc = auc(fpr, tpr)
    plt.figure()
    lw = 2
    plt.plot(1-fpr, tpr, color='darkorange',
             lw=lw, label='ROC curve (area = %0.2f)' % roc_auc)
    plt.plot([0, 1], [1, 0], color='navy', lw=lw, linestyle='--')
    plt.title('Random Forest, auc score = '+str(roc_auc)+ ' for '+team)
    plt.xlabel('True Negative Rate')
    plt.ylabel('True Positive Rate')
    newpath = cdir_init+'\Auc figures for shot difficulty model'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    os.chdir(newpath)
    plt.savefig('AUC is '+ str(roc_auc)+' for '+team+' RFC'+'.jpg')
    plt.close()
    from sklearn.metrics import accuracy_score
    accuracy = accuracy_score(pred_rfc>=0.5, test_y)
    print 'prediction accuracy is: '+str(accuracy) + ' for '+team

    #Logistic regression
    '''from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GridSearchCV
    lgr = LogisticRegression()
    lgr.fit(train_x, train_y)
    pred_lgr = lgr.predict_proba(test_x)[:,1]
    import datetime
    print('logistic regression done')
    #print(datetime.datetime.now())
    #plot the roc curve for rfc classifier
    from sklearn.metrics import roc_curve, auc
    fpr_lgr, tpr_lgr, threshold = roc_curve(test_y, pred_lgr)
    roc_auc_lgr = auc(fpr_lgr, tpr_lgr)
    plt.figure()
    lw = 2
    plt.plot(1-fpr_lgr, tpr_lgr, color='darkorange',
             lw=lw, label='ROC curve (area = %0.2f)' % roc_auc_lgr)
    plt.plot([0, 1], [1, 0], color='navy', lw=lw, linestyle='--')
    plt.title('Logistic Regression, auc score = '+str(roc_auc_lgr)+ ' for '+team)
    plt.xlabel('True Negative Rate')
    plt.ylabel('True Positive Rate')
    newpath = cdir_init+'\Auc figures for shot difficulty model'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    os.chdir(newpath)
    plt.savefig('AUC is '+ str(roc_auc_lgr)+' for '+team+' LGR'+'.jpg')
    plt.close()
    from sklearn.metrics import accuracy_score
    accuracy = accuracy_score(pred_lgr>=0.5, test_y)
    print 'prediction accuracy is: '+str(accuracy) + ' for '+team'''
    

    
    #plt.show()

    #Gradient boosted tree
    '''from sklearn.ensemble import GradientBoostingClassifier
    GBC = GradientBoostingClassifier(n_estimators = 30, max_depth = 4,min_samples_split =5)
    GBC.fit(train_x, train_y)
    pred_GBC = GBC.predict_proba(test_x)[:,1]
    feature_importance_GBC = GBC.feature_importances_
    feature_importance_GBC = pd.DataFrame(np.transpose(np.vstack((train.drop(['shot outcome'],1).columns,
                                     feature_importance_GBC))),columns=['featureName', 'importanceET'])
    feature_importance_GBC = feature_importance_GBC.sort_values(['importanceET'],ascending = 0)                                  
    import datetime
    print('GBC done')
    print(datetime.datetime.now())
    #plot the roc curve for adab classifier
    fpr_GBC, tpr_GBC, threshold = roc_curve(test_y, pred_GBC)
    roc_auc_GBC = auc(fpr_GBC, tpr_GBC)
    plt.figure()
    lw = 2
    plt.plot(1-fpr_GBC, tpr_GBC, color='darkorange',
             lw=lw, label='ROC curve (area = %0.2f)' % roc_auc_GBC)
    plt.plot([0, 1], [1, 0], color='navy', lw=lw, linestyle='--')
    plt.title('Gradient Boosted Tree, auc score = '+str(roc_auc_GBC)+ ' for '+team)
    plt.xlabel('True Negative Rate')
    plt.ylabel('True Positive Rate')
    plt.savefig('AUC is '+ str(roc_auc_GBC)+' for '+team+' GBC'+'.jpg')
    plt.close()'''

    #Adaboost classifier
    '''from sklearn.ensemble import AdaBoostClassifier
    rfc = RandomForestClassifier(n_jobs=-1 ,n_estimators=100, max_depth  = 4, min_samples_split =5)
    #adab2 = AdaBoostClassifier(base_estimator = rfc, learning_rate = 1.1, n_estimators = 5)
    from sklearn.tree import DecisionTreeClassifier
    tree = DecisionTreeClassifier(max_depth  = 20, min_samples_split =5)
    adab = AdaBoostClassifier(base_estimator = lgr, learning_rate = 1.5, n_estimators = 50)
    adab.fit(train_x, train_y)
    pred_adab = adab.predict_proba(test_x)[:,1]
    #feature_importance_adab = adab.feature_importances_
    #feature_importance_adab = pd.DataFrame(np.transpose(np.vstack((train.drop(['shot outcome'],1).columns,
    #                                 feature_importance_adab))),columns=['featureName', 'importanceET'])
    #feature_importance_adab = feature_importance_adab.sort_values(['importanceET'],ascending = 0)                                  
    import datetime
    print('adaboost done')
    #print(datetime.datetime.now())
    #plot the roc curve for adab classifier
    fpr_adab, tpr_adab, threshold = roc_curve(test_y, pred_adab)
    roc_auc_adab = auc(fpr_adab, tpr_adab)
    plt.figure()
    lw = 2
    plt.plot(1-fpr_adab, tpr_adab, color='darkorange',
             lw=lw, label='ROC curve (area = %0.2f)' % roc_auc_adab)
    plt.plot([0, 1], [1, 0], color='navy', lw=lw, linestyle='--')
    plt.title('Adaboost, auc score = '+str(roc_auc_adab)+ ' for '+team)
    plt.xlabel('True Negative Rate')
    plt.ylabel('True Positive Rate')
    plt.savefig('AUC is '+ str(roc_auc_adab)+' for '+team+' Adaboost'+'.jpg')
    plt.close()
    from sklearn.metrics import accuracy_score
    accuracy = accuracy_score(pred_adab>=0.5, test_y)
    print 'prediction accuracy is: '+str(accuracy) + ' for '+team'''

    
    #Voting classifier
    '''from sklearn.ensemble import VotingClassifier
    vote = VotingClassifier(estimators = [('GBC',GBC),
                                          ('LGR',lgr)], voting = 'soft' )
    vote.fit(train_x, train_y)
    pred_vote = vote.predict_proba(test_x)[:,1]
    #feature_importance_adab = adab.feature_importances_
    #feature_importance_adab = pd.DataFrame(np.transpose(np.vstack((train.drop(['shot outcome'],1).columns,
    #                                 feature_importance_adab))),columns=['featureName', 'importanceET'])
    #feature_importance_adab = feature_importance_adab.sort_values(['importanceET'],ascending = 0)                                  
    import datetime
    print('Voting done')
    #print(datetime.datetime.now())
    #plot the roc curve for adab classifier
    fpr_vote, tpr_vote, threshold = roc_curve(test_y, pred_vote)
    roc_auc_vote = auc(fpr_vote, tpr_vote)
    plt.figure()
    lw = 2
    plt.plot(1-fpr_vote, tpr_vote, color='darkorange',
             lw=lw, label='ROC curve (area = %0.2f)' % roc_auc_vote)
    plt.plot([0, 1], [1, 0], color='navy', lw=lw, linestyle='--')
    plt.title('Voting algorithm, auc score = '+str(roc_auc_vote)+ ' for '+team)
    plt.xlabel('True Negative Rate')
    plt.ylabel('True Positive Rate')
    plt.savefig('AUC is '+ str(roc_auc_vote)+' for '+team+' Voting'+'.jpg')
    plt.close()
    from sklearn.metrics import accuracy_score
    accuracy = accuracy_score(pred_vote>=0.5, test_y)
    print 'prediction accuracy is: '+str(accuracy) + ' for '+team'''
    
    #plt.show()
    os.chdir(cdir_init)
    pred_miss = 1-pred_rfc
    pred_miss = pd.DataFrame(pred_miss)
    import os
    cdir_init = os.getcwd()
    newpath = cdir_init+'\predicted shot difficulty'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    os.chdir(newpath)
    pred_miss.to_csv(team+' predicted chance of missing one shot '+'.csv')
    os.chdir(cdir_init)
    return 1-pred_rfc


