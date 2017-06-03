import csv, os, math
cdir_init = os.getcwd()
os.chdir(cdir_init+'\Parsed Shot data')
shot_type = []
dic = {}
count = 0

for m, filename in enumerate(os.listdir(os.getcwd())):
    with open(filename) as f:
        f = csv.DictReader(f, delimiter = ',')
        headers = f.fieldnames
        for i, line in enumerate(f):
            count += 1
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
                         'Pull-Up Jump Shot','Bank Shot'
                         ]
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
              
            if line['shot type'] not in shot_type:
                shot_type.append(line['shot type'])
                dic[line['shot type']] = 1
            else:
                dic[line['shot type']] += 1



print 'total shot count = '+ str(count)
os.chdir(cdir_init)
datafile = 'shot type count.csv'
with open(datafile, 'wb') as filename:
    w = csv.writer(filename, delimiter = ',')
    for key in dic.keys():
        w.writerow([key, dic[key]])


