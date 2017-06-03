def Game_ID(team):
    datafile = "Game Schedule 16-17-Regular.csv"
    #team = 'GSW'
    import csv
    import os.path
    data = []
    with open(datafile, "r") as f:
        f = csv.DictReader(f, delimiter = ',')
        #data.append(['Game Date', 'Game Date Formatted','Away Team', 'Home Team'])
        for i, line in enumerate(f):
            dict = {}
            if line['#Away Team Abbr.'] == team or line['#Home Team Abbr.']== team:
                dict['Game Date'] = line['#Game Date']
                temp = line['#Game Date']
                temp = temp.split('-')
                date = ''
                for item in temp:
                    date = date+item
                dict['Game Date Formatted']= date
                dict['Away Team'] = line['#Away Team Abbr.']
                dict['Home Team'] = line['#Home Team Abbr.']
                data.append(dict)
            else:
                continue
    cdir = os.getcwd()
    newpath = cdir+'\GameID'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    os.chdir(newpath)
    savefile = team + ' '+'GameID.csv'
    with open(savefile, 'wb') as filename:
        w = csv.writer(filename, delimiter = ',')
        for i, line in enumerate(data):
            if i == 0:
                w.writerow(line.keys())
            w.writerow(line.values())
    os.chdir(cdir)

def download_play_by_play(team):
    import base64
    import requests
    import json
    import os
    import csv
    username = xxxxx #input your user name
    password = xxxxx #input your password
    url = 'https://www.mysportsfeeds.com/api/feed/pull/nba/2016-2017-regular/game_playbyplay.json'
    cdir = os.getcwd()
    os.chdir(cdir+'\GameID')

    with open(team+' '+'GameID.csv', "r") as f:
        f = csv.DictReader(f, delimiter = ',')
        for i, line in enumerate(f):
            id = line['Game Date Formatted']+'-'+line['Away Team']+'-'+line['Home Team']
            try:
                response = requests.get(
                    url,
                    params={
                        "gameid": id
                    },
                    headers={
                        "Authorization": "Basic " + base64.b64encode(username + ":" + password)
                    }
                )
                #print('Response HTTP Status Code: {status_code}'+' for '+id.format(
                 #   status_code=response.status_code))
                #print('Response HTTP Response Body: {content}'.format(
                    #content=response.content))
                os.chdir(cdir)
                cdir = os.getcwd()
                newpath = cdir+'\Play by Play' +'\\'+ team
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                os.chdir(newpath)
                with open(id+'.json', mode='w') as v:
                    v.write(json.dumps(response.json()))
            except requests.exceptions.RequestException:
                print('HTTP Request failed')
    os.chdir(cdir)
def parse_shot_log(team):
    import os, json, pprint, csv
    #team = 'GSW'
    cdir_init = os.getcwd()
    os.chdir(cdir_init+'\Play by Play'+'\\'+team)

    data_shot = []
    headers = ['date','home game','away team','home team','time','quarter',
                'shoot player','player position', 'shot type', 'points',
               'location x', 'location y', 'current shot outcome', 'opponent previous shot',
               'self previous shot','time from last shot', 'shot distance',
               'shot angle']

    for m, filename in enumerate(os.listdir(os.getcwd())):
        data_single_game = []
        with open(filename) as f:
            content = json.loads(f.read())
            for item in content:
                temp = content[item]
                temp_game = content[item]['game']
                date_temp = content[item]['game']['date']
                away_team_temp = content[item]['game']['awayTeam']['Abbreviation']
                home_team_temp = content[item]['game']['homeTeam']['Abbreviation']
                if team == home_team_temp:
                    homegame = 'Yes'
                    oppteam = away_team_temp
                else:
                    homegame = 'No'
                    oppteam = home_team_temp
                temp_play = content[item]['plays']['play']
                #print[date_temp,away_team_temp,home_team_temp]
                for i, item in enumerate(temp_play):
                    if 'fieldGoalAttempt' in item.keys() and item[
                        'fieldGoalAttempt']['teamAbbreviation'] == team:
                        data_single_shot = {}
                        data_single_shot['date'] = date_temp
                        data_single_shot['home game'] = homegame
                        data_single_shot['away team'] = away_team_temp
                        data_single_shot['home team'] = home_team_temp
                        data_single_shot['time'] = item['time']
                        data_single_shot['quarter'] = item['quarter']
                        shoot_player = item['fieldGoalAttempt']['shootingPlayer']['FirstName']+' '+item['fieldGoalAttempt']['shootingPlayer']['LastName']
                        player_position = item['fieldGoalAttempt']['shootingPlayer']['Position']
                        data_single_shot['shoot player'] = shoot_player
                        data_single_shot['player position'] = player_position
                        #print item['fieldGoalAttempt']['shotType']
                        data_single_shot['shot type'] = item['fieldGoalAttempt']['shotType']
                        data_single_shot['points'] = item['fieldGoalAttempt']['Points']
                        try:
                            data_single_shot['location x'] = item['fieldGoalAttempt']['shotLocation']['x']
                            data_single_shot['location y'] = item['fieldGoalAttempt']['shotLocation']['y']
                        except KeyError:
                            #print [m,i]
                            data_single_shot['location x'] = None
                            data_single_shot['location y'] = None
                        data_single_shot['current shot outcome'] = item['fieldGoalAttempt']['outcome']
                        if i == 0:
                            data_single_shot['opponent previous shot'] = None
                            data_single_shot['self previous shot'] = None
                        else:
                            search_flag_opp = 0
                            search_flag_self = 0
                            for k in range(i-1,0,-1):
                                if 'fieldGoalAttempt' in temp_play[k].keys() and temp_play[k]['fieldGoalAttempt']['teamAbbreviation'] == oppteam:
                                    data_single_shot['opponent previous shot'] = temp_play[k]['fieldGoalAttempt']['outcome']
                                    search_flag_opp = 1
                                    break
                            if search_flag_opp == 0:
                                data_single_shot['opponent previous shot'] = None
                                
                            for k in range(i-1,0,-1):
                                if 'fieldGoalAttempt' in temp_play[k].keys() and temp_play[k]['fieldGoalAttempt']['teamAbbreviation'] == team:
                                    data_single_shot['self previous shot'] = temp_play[k]['fieldGoalAttempt']['outcome']
                                    time_now = data_single_shot['time'].split(':')
                                    time_previous = temp_play[k]['time'].split(':')
                                    data_single_shot['time from last shot'] = 60*(int(time_now[0])-int(time_previous[0]))+(int(time_now[1])-int(time_previous[1]))
                                    search_flag_self = 1
                                    break
                            if search_flag_self == 0:
                                data_single_shot['self previous shot'] = None
                                data_single_shot['time from last shot'] = None
                            if data_single_shot['time from last shot']<0:
                                data_single_shot['time from last shot'] = None
                        data_single_game.append(data_single_shot)
        data_shot.append(data_single_game)

    newpath = cdir_init+'\Shot data'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    os.chdir(newpath)



    datafile = 'shot log' + ' '+ team + '.csv'
    flag = 0
    with open(datafile, 'wb') as filename:
        w = csv.writer(filename, delimiter = ',')
        for i, item in enumerate(data_shot):
            for item1 in item:
                if flag == 0:
                    flag = 1
                    w.writerow(item1.keys())
                w.writerow(item1.values())
            
            
    os.chdir(cdir_init)


