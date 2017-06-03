import os, csv
import numpy as np
import pandas as pd
from pymongo import MongoClient
import matplotlib.pyplot as plt
from download_data import Game_ID, download_play_by_play, parse_shot_log
from plot_shot_distance_shot_difficulty import shot_rationality_percentage
from plot_shot_distance_shot_difficulty import shot_distance_difference_from_previous_shot, shot_difficulty_difference
from plot_shot_distance_shot_difficulty import shot_rationality_percentage_all_team
from parse_data import parse_data, save_to_db_shot_log, save_to_db_16_17_regular
from parse_data import update_db_shot_distance_shot_percentage, update_shot_distance_difference_from_previous_shot
from parse_data import update_db_predicted_shot_difficulty
os.chdir(your directory)

########
#save the 16-17 regular season data into mongodb database
save_to_db_16_17_regular()

###############################
#download and parse the shotdata for all teams, then save the data into mongodb
#with the database name of 'NBA_shot_log2', collection name is team name abbreviation
filename = 'NBA team name vs abbreviation.csv'
with open(filename, "r") as f:
    f = csv.DictReader(f, delimiter = ',')
    for i, line in enumerate(f):
        if i >= 0:
        #the website might have issue if we download the data for all 30
        # teams in one run, so might need to download the data team by team,
        #by modifiying the value of i, I have downloaded and saved the data, you
        #you can also just run with the downloaded data
            Team_name = line['Abbreviation/Acronym']
            #print 'downloading data for ' + line['Abbreviation/Acronym']
            #Game_ID(Team_name)
            #download_play_by_play(Team_name)
            #parse_shot_log(Team_name)
            print 'parsing data for ' + line['Abbreviation/Acronym']
            parse_data(Team_name)
            print 'saving to mongodb for ' + line['Abbreviation/Acronym']
            save_to_db_shot_log(Team_name)
            update_db_shot_distance_shot_percentage(Team_name)


            

##########################
#predict the shot difficulty of making a shot(probablity of missing a shot). The training dataset is the shot data
#from the other 29 teams, and the testing dataset is the shot data for the target team
#the shot data is loaded from the database 'NBA_shot_log2'
from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client.NBA_shot_log2
shot_difficulty = {}
with open(filename, "r") as f:
    f = csv.DictReader(f, delimiter = ',')
    for i, line in enumerate(f):
        if i>=0:
            shots_team = []
            Team_name = line['Abbreviation/Acronym']
            collection = db[Team_name]
            shots_target = collection.find({})
            for shots in shots_target:
                shots_team.append(shots)
            shots_team = pd.DataFrame(shots_team)
            shots_team = shots_team[shots_team['shot distance (feet)']!= '']
            
            from predicting_shot_difficulty import shot_make_probablity
            print 'predicting shot difficulty for '+Team_name
            shot_difficulty[Team_name]=shot_make_probablity(Team_name,shots_team)
            update_db_predicted_shot_difficulty(Team_name)
            update_shot_distance_difference_from_previous_shot(Team_name)

##########################
#do some analysis with the shot distance and shot difficulty
from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client.NBA_shot_log2
filename = 'NBA team name vs abbreviation.csv'
with open(filename, "r") as f:
    f = csv.DictReader(f, delimiter = ',')
    for i, line in enumerate(f):
        if i >= 0:
            Team_name = line['Abbreviation/Acronym']
            print 'plotting for '+Team_name
            shot_distance_difference_from_previous_shot(Team_name)
            shot_difficulty_difference(Team_name)
            shot_rationality_percentage(Team_name)
shot_rationality_percentage_all_team()


    


