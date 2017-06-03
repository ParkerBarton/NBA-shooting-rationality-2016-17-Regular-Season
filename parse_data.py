def parse_data(team):
    from parse_data import find_player_percentage
    import csv, os, math
    import numpy as np
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.NBA_regular_season
    cdir_init = os.getcwd()
    os.chdir(cdir_init+'\Shot data')
    data = []
    with open('shot log '+team+'.csv', "r") as f:
        f = csv.DictReader(f, delimiter = ',')
        headers = f.fieldnames
        for i, line in enumerate(f):
            if line['self previous shot'] == 'SCORED':
                line['self previous shot'] = int(1)
            else:
                if line['self previous shot'] == '':
                    line['self previous shot'] = None
                else:
                    line['self previous shot'] = int(0)
            
            if line['opponent previous shot'] == 'SCORED':
                line['opponent previous shot'] = int(1)
            else:
                if line['opponent previous shot'] == '':
                    line['opponent previous shot'] = None
                else:
                    line['opponent previous shot'] = int(0)

            if line['current shot outcome'] == 'SCORED':
                line['current shot outcome'] = int(1)
            else:
                if line['current shot outcome'] == '':
                    line['current shot outcome'] = None
                else:
                    line['current shot outcome'] = int(0)
            time = line['time'].split(':')
            line['time(s)'] = 60*int(time[0])+int(time[1])
            line['quarter'] = int(line['quarter'])
            replace = ['.', "'"]
            for r in replace:
                line['shot type'] = line['shot type'].replace(r,'.')
                line['shot type'] = line['shot type'].split('.')[-1].strip()
                
            type_list = ['Jump Shot', 'Layup', 'Pullup Jump Shot', 'Driving Layup', 'Dunk', 'Floating Jump Shot',
                         'Step Back Jump Shot', 'Hook Shot','Reverse Layup',
                         'Cutting Layup Shot','Running Layup','Turnaround Jump Shot',
                         'Fadeaway Jumper','Putback Layup', 'Running Jump Shot', 'Turnaround Hook Shot',
                          'Driving Hook Shot', 'Turnaround Fadeaway',
                         'Alley Oop Layup',
                         'Pull-Up Jump Shot','Bank Shot']
                         
            flag = 0
            shot_init = line['shot type']
            for shot in type_list:
                if shot in shot_init:
                    if flag == 0:
                        line['shot type'] = shot
                        flag = 1
                if flag == 1:
                    if shot in shot_init:
                        if len(shot) > len(line['shot type']):
                            line['shot type'] = shot
            if line['shot type'] == 'Pull-Up Jump Shot':
                line['shot type'] = 'Pullup Jump Shot'
            #parse the shot distance and angle
            try:
                line['location y'] = float(line['location y'])
                line['location x'] = float(line['location x'])
                line['quarter'] = int(line['quarter'])
                if line['home team'] == team:
                    if line['quarter'] == 1 or line['quarter'] == 2:
                        line['shot distance (feet)'] = (((line['location y']-250)/10)**2 + ((line['location x']-52.5)/10)**2)**0.5
                        line['shot angle (degree)'] = 180/math.pi*(math.atan((line['location y']-250)/(line['location x']-52.5)))
                        if line['location x']<=52.5:
                            line['shot angle (degree)'] = np.sign(line['location y']-250)*90.0 - math.atan((line['location x']-52.5)/(line['location y']-250.00001))
                    else:
                        line['shot distance (feet)'] = (((line['location y']-250)/10)**2 + ((line['location x']-887.5)/10)**2)**0.5
                        line['shot angle (degree)'] = 180/math.pi*(math.atan((line['location y']-250)/(line['location x']-887.5)))
                        if line['location x']>=887.5:
                            line['shot angle (degree)'] = -np.sign(line['location y']-250)*90.0 + math.atan((line['location x']-52.5)/(line['location y']-250.00001))
                else:
                    if line['quarter'] == 3 or line['quarter'] == 4:
                        line['shot distance (feet)'] = (((line['location y']-250)/10)**2 + ((line['location x']-52.5)/10)**2)**0.5
                        line['shot angle (degree)'] = 180/math.pi*(math.atan((line['location y']-250)/(line['location x']-52.5)))
                        if line['location x']<52.5:
                            line['shot angle (degree)'] = np.sign(line['location y']-250)*90.0 - math.atan((line['location x']-52.5)/(line['location y']-250.00001))
                    else:
                        line['shot distance (feet)'] = (((line['location y']-250)/10)**2 + ((line['location x']-887.5)/10)**2)**0.5
                        line['shot angle (degree)'] = 180/math.pi*(math.atan((line['location y']-250)/(line['location x']-887.5)))
                        if line['location x']>=887.5:
                            line['shot angle (degree)'] = -np.sign(line['location y']-250)*90.0 + math.atan((line['location x']-52.5)/(line['location y']-250.00001))
            except ValueError:
                line['shot distance (feet)'] = None
                line['shot angle (degree)'] = None
                
            line['player percentage'] = find_player_percentage(line['shoot player'],line['points'],db)
            # introduce 'shot zone' variable, divide the basketball field into 9 zones:
            # short range zone, mid-range zones (4 zones depends on shot angle)
            #and long range zones(4 zones depends on shot angle)
            distance_short = 10
            distance_long = 24
            if line['shot distance (feet)'] <= distance_short:
                line['shot zone'] = 'Inside'
            if line['shot distance (feet)'] > distance_long:
                if line['shot angle (degree)'] <=-45:
                    line['shot zone'] = 'long range left'
                if line['shot angle (degree)'] >-45 and line['shot angle (degree)'] <=0:
                    line['shot zone'] = 'long range central left'
                if line['shot angle (degree)'] >0 and line['shot angle (degree)'] <=45:
                    line['shot zone'] = 'long range central right'
                if line['shot angle (degree)'] >45:
                    line['shot zone'] = 'long range right'
            if line['shot distance (feet)'] > distance_short and line['shot distance (feet)'] <= distance_long:
                if line['shot angle (degree)'] <=-45:
                    line['shot zone'] = 'mid range left'
                if line['shot angle (degree)'] >-45 and line['shot angle (degree)'] <=0:
                    line['shot zone'] = 'mid range central left'
                if line['shot angle (degree)'] >0 and line['shot angle (degree)'] <=45:
                    line['shot zone'] = 'mid range central right'
                if line['shot angle (degree)'] >45:
                    line['shot zone'] = 'mid range right'
            data.append(line)



    newpath = cdir_init+'\Parsed Shot data'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    os.chdir(newpath)
        
    datafile = 'parsed shot log' + ' '+ team + '.csv'
    flag = 0
    with open(datafile, 'wb') as filename:
        w = csv.writer(filename, delimiter = ',')
        for i, item in enumerate(data):
            if flag == 0:
                flag = 1
                w.writerow(item.keys())
            w.writerow(item.values())



    os.chdir(cdir_init)

def save_to_db_shot_log(team):
    import csv, os, pymongo
    #team = 'GSW'
    cdir_init = os.getcwd()
    os.chdir(cdir_init+'\Parsed Shot data')
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.NBA_shot_log2


    with open('parsed shot log '+team+'.csv','r') as f:
        f = csv.DictReader(f, delimiter = ',')
        headers = f.fieldnames
        for i, line in enumerate(f):
            try:
                line['self previous shot'] = int(line['self previous shot'])
            except ValueError:
                line['self previous shot'] = int(9999)
            try:
                line['opponent previous shot'] = int(line['opponent previous shot'])
            except ValueError:
                line['opponent previous shot'] = int(9999)
            try:
                line['time from last shot'] = int(line['time from last shot'])
            except ValueError:
                line['time from last shot'] = int(9999)
            db[team].insert(line)


    os.chdir(cdir_init)

def save_to_db_16_17_regular():
    import csv, os, pymongo
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.NBA_regular_season

    with open('Player Regular 16-17 Stats.csv','r') as f:
        f = csv.DictReader(f, delimiter = ',')
        headers = f.fieldnames
        for i, line in enumerate(f):
            line['#Player Name'] = line['#FirstName']+' '+line['#LastName']  
            db['16-17'].insert(line)
def update_shot_distance_difference_from_previous_shot(team):
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.NBA_shot_log2
    collection= db[team]
    shots = collection.find({})
    for i, shot in enumerate(shots):
        if shot['shot distance (feet)'] != '':
            if shot['self previous shot']==9999:
                shot_prev = float(shot['shot distance (feet)'])
                difficulty_prev = float(shot['predicted shot difficulty'])
                continue
            shot_difference = float(shot['shot distance (feet)'])-shot_prev
            difficulty_difference = float(shot['predicted shot difficulty'])-difficulty_prev
            collection.update({'_id':shot['_id']},
                {'$set':{'shot distance difference from previous':shot_difference,
                         'shot difficulty difference from previous':difficulty_difference}})
            #shot['shot distance difference from previous'] = shot_difference
            shot_prev = float(shot['shot distance (feet)'])
            difficulty_prev = float(shot['predicted shot difficulty'])
        else:
            pass
def update_db_predicted_shot_difficulty(team):
    from pymongo import MongoClient
    import os, csv
    client = MongoClient("mongodb://localhost:27017")
    db = client.NBA_shot_log2
    collection= db[team]
    cdir_init = os.getcwd()
    newpath = cdir_init + '\predicted shot difficulty'
    os.chdir(newpath)
    shot_difficulty = []
    with open(team+' predicted chance of missing one shot '+'.csv', "r") as f:
        f = csv.DictReader(f, delimiter = ',')
        headers = f.fieldnames
        for line in f:
            shot_difficulty.append(line['0'])
    shots = collection.find({})
    i = 0
    for shot in shots:
        if shot['shot distance (feet)'] != '':
            collection.update({'_id':shot['_id']},
                {'$set':{'predicted shot difficulty':shot_difficulty[i]}})
            i += 1
        else:
            pass
    os.chdir(cdir_init)

def update_db_shot_distance_shot_percentage(team):
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.NBA_shot_log2
    collection= db[team]
    shots = collection.find({})
    gameID = []
    for shot in shots:
        if shot['date'] not in gameID:
            gameID.append(shot['date'])

    for date in gameID:
        shots_made = collection.find({'date':date, 'self previous shot':1,
                                      'shot distance (feet)':{'$ne':''}})
        shots_miss = collection.find({'date':date, 'self previous shot':0,
                                      'shot distance (feet)':{'$ne':''}})
        shot_distance = 0
        for i, shot in enumerate(shots_made):
            shot_distance += float(shot['shot distance (feet)'])
        shot_distance_made = shot_distance/(i+1)
        shot_distance = 0
        for i, shot in enumerate(shots_miss):
            shot_distance += float(shot['shot distance (feet)'])
        shot_distance_miss = shot_distance/(i+1)
        collection.update({'date':date},
                          {'$set':{'shot distance after made':shot_distance_made,
                                   'shot distance after miss':shot_distance_miss}},
                          multi = True
                            )

        shots_made_2pt = collection.find({'date':date, 'self previous shot':1,
                                      'shot distance (feet)':{'$ne':''},'points':'2'})
        shots_miss_2pt = collection.find({'date':date, 'self previous shot':0,
                                      'shot distance (feet)':{'$ne':''},'points':'2'})
        shot_distance_2pt = 0
        for i, shot in enumerate(shots_made_2pt):
            shot_distance_2pt += float(shot['shot distance (feet)'])
        shot_distance_made_2pt = shot_distance_2pt/(i+1)
        shot_distance_2pt = 0
        for i, shot in enumerate(shots_miss_2pt):
            shot_distance_2pt += float(shot['shot distance (feet)'])
        shot_distance_miss_2pt = shot_distance_2pt/(i+1)
        collection.update({'date':date},
                          {'$set':{'2pt shot distance after made':shot_distance_made_2pt,
                                   '2pt shot distance after miss':shot_distance_miss_2pt}},
                          multi = True
                            )

        shots_made_3pt = collection.find({'date':date, 'self previous shot':1,
                                      'shot distance (feet)':{'$ne':''},'points':'3'})
        shots_miss_3pt = collection.find({'date':date, 'self previous shot':0,
                                      'shot distance (feet)':{'$ne':''},'points':'3'})
        shot_distance_3pt = 0
        for i, shot in enumerate(shots_made_3pt):
            shot_distance_3pt += float(shot['shot distance (feet)'])
        shot_distance_made_3pt = shot_distance_3pt/(i+1)
        shot_distance_3pt = 0
        for i, shot in enumerate(shots_miss_3pt):
            shot_distance_3pt += float(shot['shot distance (feet)'])
        shot_distance_miss_3pt = shot_distance_3pt/(i+1)
        collection.update({'date':date},
                          {'$set':{'3pt shot distance after made':shot_distance_made_3pt,
                                   '3pt shot distance after miss':shot_distance_miss_3pt}},
                          multi = True
                            )

        
        shots_all = collection.find({'date':date})
        percent_2pt = 0
        percent_3pt = 0
        percent_all = 0
        count_all = 0
        count_2pt = 0
        count_3pt = 0
        
        for shot in shots_all:
            count_all += 1
            if shot['current shot outcome']=='1':
                percent_all+=1
            if shot['points'] == '2':
                count_2pt+=1
                if shot['current shot outcome']=='1':
                    percent_2pt+=1
            if shot['points'] == '3':
                count_3pt+=1
                if shot['current shot outcome']=='1':
                    percent_3pt+=1
        percent_2pt = float(percent_2pt)/count_2pt
        percent_3pt = float(percent_3pt)/count_3pt
        percent_all = float(percent_all)/count_all
        collection.update({'date':date},
                          {'$set':{'percentage 2pt':percent_2pt,
                                   'percentage 3pt':percent_3pt,
                                   'percentage all':percent_all,
                                   'trial count 2pt':count_2pt,
                                   'trial count 3pt':count_3pt}},
                          multi = True
                            ) 
                

def find_player_percentage(player_name, shot_type,db):
    from pymongo import MongoClient
    #client = MongoClient("mongodb://localhost:27017")
    #db = client.NBA_regular_season
    collection = db['16-17']
    player = collection.find({'#Player Name':player_name})
    for item in player:
        if shot_type == '2':
            return (float(item['#Fg2PtMade'])/float(item['#Fg2PtAtt']))
        else:
            return (float(item['#Fg3PtMade'])/float(item['#Fg3PtAtt']))


def FactorizeCategoricalVariable(inputDB,categoricalVarName):
    import pandas as pd
    opponentCategories = inputDB[categoricalVarName].value_counts().index.tolist()
    outputDB = pd.DataFrame()
    for category in opponentCategories:
        featureName = categoricalVarName + ': ' + str(category)
        outputDB[featureName] = (inputDB[categoricalVarName] == category).astype(int)
    return outputDB
