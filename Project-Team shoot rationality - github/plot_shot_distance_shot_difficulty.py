def shot_distance_difference_from_previous_shot(team):
    from pymongo import MongoClient
    import numpy as np
    import matplotlib.pyplot as plt
    import os
    client = MongoClient("mongodb://localhost:27017")
    db = client.NBA_shot_log2
    collection = db[team]
    data_miss = []
    data_made = []
    shots = collection.find({'self previous shot':1, 'shot distance (feet)':{'$ne':''},
                             'time from last shot':{'$gte':6}})
    for shot in shots:
        data_made.append(float(shot['shot distance difference from previous']))
    shots = collection.find({'self previous shot':0, 'shot distance (feet)':{'$ne':''},
                             'time from last shot':{'$gte':6}})
    for shot in shots:
        data_miss.append(float(shot['shot distance difference from previous']))
        
    Hist, distDiffBins = np.histogram(data_made+data_miss,bins=300,density=False)
    barWidth = 0.999*(distDiffBins[1]-distDiffBins[0])
    data_hist_made, b = np.histogram(data_made,bins=distDiffBins)
    data_hist_miss, b = np.histogram(data_miss,bins=distDiffBins)
    data_hist_made = data_hist_made.astype(float)
    data_hist_miss = data_hist_miss.astype(float)

    plt.figure()
    plt.bar(distDiffBins[:-1], data_hist_made*100/(len(data_made)+1), width=barWidth)
    plt.xlim((-40,40))
    plt.ylim((0,max([max(data_hist_made*100/(len(data_made)+1)),max(data_hist_miss*100/(len(data_made)+1))])))
    plt.title(team+' shot distance current-shot distance previous (feet) after '+'made last shot')
    plt.xlabel('shot distance current-shot distance previous (feet)')
    plt.ylabel('percentage (%)')
    cdir_init = os.getcwd()
    newpath = cdir_init+'\Shot distance difference distribution'+'\\'+'effect of self previous shot'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    os.chdir(newpath)
    plt.savefig(team+' shot distance after made '+'hist diagram'+'.jpg')
    plt.close()
    #plt.show()

    plt.figure()
    plt.bar(distDiffBins[:-1], data_hist_miss*100/(len(data_miss)+1), width=barWidth)
    plt.xlim((-40,40))
    plt.ylim((0,max([max(data_hist_made*100/(len(data_made)+1)),max(data_hist_miss*100/(len(data_made)+1))])))
    plt.title(team+' shot distance current-shot distance previous (feet) after '+'missed last shot')
    plt.xlabel('shot distance current-shot distance previous (feet)')
    plt.ylabel('percentage (%)')
    plt.savefig(team+' shot distance difference after miss '+'hist diagram'+'.jpg')
    plt.close()

    Hist, distDiffBins = np.histogram(data_made+data_miss,bins=300,density=False)
    barWidth = 0.999*(distDiffBins[1]-distDiffBins[0])
    data_hist_made, b = np.histogram(data_made,bins=distDiffBins)
    data_hist_miss, b = np.histogram(data_miss,bins=distDiffBins)
    data_hist_made = data_hist_made.astype(float)
    data_hist_miss = data_hist_miss.astype(float)
    cdf_data_made = np.cumsum(data_hist_made).astype(float)
    cdf_data_made = cdf_data_made/max(cdf_data_made)

    cdf_data_miss = np.cumsum(data_hist_miss).astype(float)
    cdf_data_miss = cdf_data_miss/max(cdf_data_miss)

    plt.figure();
    madePrev = plt.plot(distDiffBins[:-1], cdf_data_made, label='made Prev'); plt.xlim((-40,40))
    missedPrev = plt.plot(distDiffBins[:-1], cdf_data_miss, label='missed Prev'); plt.xlim((-40,40)); plt.ylim((0,1))
    plt.title('cumulative density function - CDF'); plt.xlabel('shot distance current-shot distance previous (feet)'); plt.legend(loc='lower right');plt.ylabel('shot distance CDF');
    plt.savefig(team+' shot distance change CDF '+'.jpg')
    plt.close()

    os.chdir(cdir_init)
    
def shot_difficulty_difference(team):
    from predicting_shot_difficulty import shot_make_probablity
    from pymongo import MongoClient
    import numpy as np
    import matplotlib.pyplot as plt
    import os
    import pandas as pd
    client = MongoClient("mongodb://localhost:27017")
    db = client.NBA_shot_log2
    collection = db[team]
    data_miss = []
    data_made = []
    shots = collection.find({'self previous shot':1, 'shot distance (feet)':{'$ne':''},
                             'time from last shot':{'$gte':6}})
    for shot in shots:
        data_made.append(shot['shot difficulty difference from previous'])
    shots = collection.find({'self previous shot':0, 'shot distance (feet)':{'$ne':''},
                             'time from last shot':{'$gte':6}})
    for shot in shots:
        data_miss.append(shot['shot difficulty difference from previous'])
    normalizer = max([max(map(abs,data_miss)),max(map(abs,data_made))])
    #data_miss = [data/normalizer for data in data_miss]
    #data_made = [data/normalizer for data in data_made]


        
    Hist, distDiffBins = np.histogram(data_made+data_miss,bins=100,density=False)
    barWidth = 0.999*(distDiffBins[1]-distDiffBins[0])
    data_hist_made, b = np.histogram(data_made,bins=distDiffBins)
    data_hist_miss, b = np.histogram(data_miss,bins=distDiffBins)
    data_hist_made = data_hist_made.astype(float)
    data_hist_miss = data_hist_miss.astype(float)

    plt.figure()
    plt.bar(distDiffBins[:-1], data_hist_made*100/(len(data_made)+1), width=barWidth, color = 'blue')
    plt.xlim((min([min(data_made),min(data_miss)]),max([max(data_made),max(data_miss)])))
    plt.ylim((0,max([max(data_hist_made*100/(len(data_made)+1)),max(data_hist_miss*100/(len(data_made)+1))])))
    plt.title(team+' shot difficulty change after '+'made last shot')
    plt.xlabel('shot difficulty current - shot difficulty previous')
    plt.ylabel('percentage (%)')
    cdir_init = os.getcwd()
    newpath = cdir_init+'\Shot difficulty distribution'+'\\'+'effect of self previous shot'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    os.chdir(newpath)
    plt.savefig(team+' shot difficulty change after made '+'hist diagram'+'.jpg')
    plt.close()
    #plt.show()

    plt.figure()
    plt.bar(distDiffBins[:-1], data_hist_miss*100/(len(data_miss)+1), width=barWidth, color = 'blue')
    plt.xlim((min([min(data_made),min(data_miss)]),max([max(data_made),max(data_miss)])))
    plt.ylim((0,max([max(data_hist_made*100/(len(data_made)+1)),max(data_hist_miss*100/(len(data_made)+1))])))
    plt.title(team+' shot difficulty change after '+'made last shot')
    plt.xlabel('shot difficulty current - shot difficulty previous')
    plt.ylabel('percentage (%)')
    plt.savefig(team+' shot difficulty change after miss '+'hist diagram'+'.jpg')
    plt.close()

    Hist, distDiffBins = np.histogram(data_made+data_miss,bins=100,density=False)
    barWidth = 0.999*(distDiffBins[1]-distDiffBins[0])
    data_hist_made, b = np.histogram(data_made,bins=distDiffBins)
    data_hist_miss, b = np.histogram(data_miss,bins=distDiffBins)
    data_hist_made = data_hist_made.astype(float)
    data_hist_miss = data_hist_miss.astype(float)

    cdf_data_made = np.cumsum(data_hist_made).astype(float)
    cdf_data_made = cdf_data_made/max(cdf_data_made)

    cdf_data_miss = np.cumsum(data_hist_miss).astype(float)
    cdf_data_miss = cdf_data_miss/max(cdf_data_miss)

    plt.figure();
    madePrev = plt.plot(distDiffBins[:-1], cdf_data_made, label='made Prev'); plt.xlim((0,1))
    missedPrev = plt.plot(distDiffBins[:-1], cdf_data_miss, label='missed Prev'); plt.ylim((0,1))
    plt.xlim((min([min(data_made),min(data_miss)]),max([max(data_made),max(data_miss)])))
    plt.title('cumulative density function - CDF'); plt.xlabel('shot difficulty current - shot difficulty previous')
    plt.legend(loc='lower right');plt.ylabel('shot difficulty change CDF');
    plt.savefig(team+'  shot difficulty change CDF '+'.jpg')
    plt.close()

    os.chdir(cdir_init)

def shot_rationality_percentage(team):
    from pymongo import MongoClient
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    import math
    client = MongoClient("mongodb://localhost:27017")
    db = client.NBA_shot_log2
    collection = db[team]
    shots = collection.find({})
    gameID = []
    for shot in shots:
        if shot['date'] not in gameID:
            gameID.append(shot['date'])

    plot_data = []
    for i,date in enumerate(gameID):
        shots_made = collection.find({'date':date,'shot difficulty difference from previous':{'$exists':1},
                                      'self previous shot':1})
        shots_missed = collection.find({'date':date,'shot difficulty difference from previous':{'$exists':1},
                                      'self previous shot':0})
        rationality_made = []
        for i, shot in enumerate(shots_made):
            shot = shot
            rationality_made.append(float(shot['shot distance difference from previous']))
            percent_2pt = shot['percentage 2pt']
            percent_3pt = shot['percentage 3pt']
            percent_all = shot['percentage all']
        rationality_made = np.mean(rationality_made)
        rationality_missed = []
        for i, shot in enumerate(shots_missed):
            shot = shot
            rationality_missed.append(float(shot['shot distance difference from previous']))
        rationality_missed = np.mean(rationality_missed)
        rationality = rationality_made-rationality_missed
        plot_data.append([rationality,percent_all*100, percent_2pt*100, percent_3pt*100 ])

    plot_data_new = []
    for e in plot_data:
        if math.isnan(e[0]):
            continue
        plot_data_new.append(e)

    plot_data = np.array(plot_data_new)


    #plot 2pt distance ratio vs. shooting percentage
    #linear regression model
    from scipy import stats
    slope, intercept, r_value, p_value, std_err = stats.linregress(plot_data[:,2],plot_data[:,3])
    plt.figure()
    percent_2pt = plt.scatter(plot_data[:,0],plot_data[:,2], color = 'r')
    plt.title('shooting irrationality v.s. 2pt shooting percentage')
    plt.xlabel('shooting irrationality')
    plt.ylim(20,80)
    plt.ylabel('2pt shooting percentage (%)')
    cdir_init = os.getcwd()
    newpath = cdir_init+'\shot distance irrationality vs shot percentage-2pt'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    os.chdir(newpath)
    plt.savefig(team+' 2pt shot distance vs shot percentage '+'.jpg')
    #plt.show()
    plt.close()
    os.chdir(cdir_init)
    #plot 3pt distance ratio vs. shooting percentage
    plt.figure()
    percent_3pt = plt.scatter(plot_data[:,0],plot_data[:,3], color = 'g')
    plt.title('shooting irrationality v.s. 3pt shooting percentage')
    plt.xlabel('shooting irrationality')
    plt.ylim(10,70)
    plt.ylabel('3pt shooting percentage (%)')
    cdir_init = os.getcwd()
    newpath = cdir_init+'\shot distance irrationality vs shot percentage-3pt'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    os.chdir(newpath)
    plt.savefig(team+' 3pt shot distance vs shot percentage '+'.jpg')
    #plt.show()
    plt.close()
    os.chdir(cdir_init)

    #plot overall distance ratio vs. shooting percentage
    plt.figure()
    percent_all = plt.scatter(plot_data[:,0],plot_data[:,1], color = 'b')
    plt.title('shooting irrationality v.s. overall shooting percentage')
    plt.xlabel('shooting irrationality')
    plt.ylim(20,80)
    plt.ylabel('overall shooting percentage (%)')
    cdir_init = os.getcwd()
    newpath = cdir_init+'\shot distance irrationality vs shot percentage-overall'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    os.chdir(newpath)
    plt.savefig(team+' overall shot distance vs shot percentage '+'.jpg')
    #plt.show()
    plt.close()
    os.chdir(cdir_init)

def shot_rationality_percentage_all_team():
    from pymongo import MongoClient
    import matplotlib.pyplot as plt
    import numpy as np
    import os, csv, math
    import pandas as pd
    filename = 'NBA team name vs abbreviation.csv'
    client = MongoClient("mongodb://localhost:27017")
    db = client.NBA_shot_log2
    plot_data = []
    plt.figure()
    with open(filename, "r") as f:
        f = csv.DictReader(f, delimiter = ',')
        for i, line in enumerate(f):
            if i >= 0:
                team = line['Abbreviation/Acronym']
            collection = db[team]
            shots = collection.find({})
            gameID = []
            for shot in shots:
                if shot['date'] not in gameID:
                    gameID.append(shot['date'])
            for i,date in enumerate(gameID):
                shots_made = collection.find({'date':date,'shot difficulty difference from previous':{'$exists':1},
                                              'self previous shot':1})
                shots_missed = collection.find({'date':date,'shot difficulty difference from previous':{'$exists':1},
                                              'self previous shot':0})
                rationality_made = []
                for i, shot in enumerate(shots_made):
                    shot = shot
                    rationality_made.append(float(shot['shot distance difference from previous']))
                    percent_2pt = shot['percentage 2pt']
                    percent_3pt = shot['percentage 3pt']
                    percent_all = shot['percentage all']
                rationality_made = np.mean(rationality_made)
                rationality_missed = []
                for i, shot in enumerate(shots_missed):
                    shot = shot
                    rationality_missed.append(float(shot['shot distance difference from previous']))
                rationality_missed = np.mean(rationality_missed)
                rationality = rationality_made-rationality_missed
                plot_data.append([rationality,percent_all*100, percent_2pt*100, percent_3pt*100 ])

    plot_data_new = []
    for e in plot_data:
        if math.isnan(e[0]):
            continue
        plot_data_new.append(e)
    
    plot_data = np.array(plot_data_new)    

    linewidth = 2
    #plot 2pt distance ratio vs. shooting percentage
    #linear regression model
    from scipy import stats
    slope, intercept, r_value, p_value, std_err = stats.linregress(plot_data[:,0],plot_data[:,2])
    plt.figure()
    percent_2pt = plt.scatter(plot_data[:,0],plot_data[:,2], color = 'b')
    x = np.linspace(min(plot_data[:,0]), max(plot_data[:,0]), 999)
    y = slope*x + intercept
    regression_line = plt.plot(x,y,color = 'r', linewidth = linewidth)
    plt.title('shooting irrationality v.s. 2pt shooting percentage ')
    markersize = 100
    plt.xlabel('shooting irrationality')
    plt.ylim(20,80)
    plt.ylabel('2pt shooting percentage (%)')
    cdir_init = os.getcwd()
    newpath = cdir_init+'\ all teams shot distance irrationality vs shot percentage'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    os.chdir(newpath)
    plt.savefig('all teams 2pt shot irrationality vs shot percentage '+'r_value is '+ str(r_value)
                +'p_value is '+ str(p_value)+'.jpg')
    #plt.show()
    plt.close()
    os.chdir(cdir_init)
    
    #plot 3pt distance ratio vs. shooting percentage
    slope, intercept, r_value, p_value, std_err = stats.linregress(plot_data[:,0],plot_data[:,3])
    plt.figure()
    percent_3pt = plt.scatter(plot_data[:,0],plot_data[:,3], color = 'b')
    x = np.linspace(min(plot_data[:,0]), max(plot_data[:,0]), 999)
    y = slope*x + intercept
    regression_line = plt.plot(x,y,color = 'r',linewidth = linewidth)
    plt.title('shooting irrationality v.s. 3pt shooting percentage ' )
    plt.xlabel('shooting irrationality')
    plt.ylim(10,70)
    plt.ylabel('3pt shooting percentage (%)')
    cdir_init = os.getcwd()
    newpath = cdir_init+'\ all teams shot distance irrationality vs shot percentage'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    os.chdir(newpath)
    plt.savefig('all teams 3pt shot irrationality vs shot percentage '+'r_value is '+ str(r_value)
                +'p_value is '+ str(p_value)+'.jpg')
    #plt.show()
    plt.close()
    os.chdir(cdir_init)

    #plot overall distance ratio vs. shooting percentage
    slope, intercept, r_value, p_value, std_err = stats.linregress(plot_data[:,0],plot_data[:,1])
    plt.figure()
    percent_all = plt.scatter(plot_data[:,0],plot_data[:,1], color = 'b')
    x = np.linspace(min(plot_data[:,0]), max(plot_data[:,0]), 999)
    y = slope*x + intercept
    regression_line = plt.plot(x,y,color = 'r',linewidth = linewidth)
    plt.title('shooting irrationality v.s. overall shooting percentage ' )
    plt.xlabel('shooting irrationality')
    plt.ylim(20,80)
    plt.ylabel('overall shooting percentage (%)')
    cdir_init = os.getcwd()
    newpath = cdir_init+'\ all teams shot distance irrationality vs shot percentage'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    os.chdir(newpath)
    plt.savefig('all teams overall shot irrationality vs shot percentage '+'r_value is '+ str(r_value)
                +'p_value is '+ str(p_value)+'.jpg')
    #plt.show()
    plt.close()
    os.chdir(cdir_init)
    
