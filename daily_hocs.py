import praw
import re
import datetime
import time
import json
agent = 'REDACTED'
r = praw.Reddit(client_id='REDACTED',
                client_secret="REDACTED",password='REDACTED',
                user_agent=agent,username='REDACTED')

config = {
    'thread': 'ta535s1hq2je',
    'batch_size': 100,
    'from':None
}

#initiate notd
NotDs = {}

def generateNotDs():
    with open('NotD.txt','r') as f:
        for line in f:
            date = re.match('([0-9]+)(/)([0-9]+)(/)([0-9]+)',line).group(5,1,3)
            date = '{0}-{1}-{2}'.format(date[0],date[1],date[2])
            num = re.findall('([0-9]+)',line)[3]
            NotDs[date] = '{0:03d}'.format(int(num))
generateNotDs()

def get_old_updates(cur_update):
    return r.request(
        method = 'GET',
        path = 'live/' + config['thread'],
        params = {
            'after' : cur_update,
            'limit' : config['batch_size']
        }
    )

def checknum(body):
    num = ''
    for char in body:
        if char.isdigit():
            num += char
            continue

        elif (char == ' ' or char == ',' or char == '.' or char == '+' or char == '-'):
            continue

        elif(char == '~' or char == '^' or char == '#' or
            char == '*' or char == '>' or char == '`' or
            char == '\n'):
            # special formatting characters, only at start of str
            if len(num) == 0:
                continue
            else:
                break

        else:
            break
    if len(num) <= 6 : return None
    if len(num) >= 9 : return None
    return num

def name2date(obj):
    id = obj['id']
    time = float((float(int('{0}'.format(id[0:8]),16))+float(int('{0}'.format(id[9:13]),16)*(16**8))+float(int('{0}'.format(id[15:18]),16)*(16**12)))/(10**7) - (86400 * 141427))
    return time


if config['from'] == None:
    day_start = (time.time() - ((time.time() - 4 * 3600)%86400))
else:
    day_start = (name2date({'id':config['from']}) - ((name2date({'id':config['from']}) - 4 * 3600)%86400))

#latest hoc is not a full day
part_hoc_time = datetime.timedelta(seconds=((time.time() - 4 * 3600)%86400))
hoc_part = True

current_count = get_old_updates(config['from'])['data']['children'][0]['data']
#get_old_updates(None)['data']['children'][0]['data']

# starting from time where script starts
# as 'after' returns all later than the current count,
# the count closest to script start is ignored

while True: # Keep going through all days
    # initiate daily hoc
    day_obj = datetime.datetime.fromtimestamp(day_start)
    notd = NotDs['{0}-{1}-{2}'.format(day_obj.year,day_obj.month,day_obj.day)]
    hoc = {
    'date':'{0}-{1}-{2}'.format(day_obj.year,day_obj.month,day_obj.day),
    'counts':{},
    '000':{},
    '333':{},
    '666':{},
    '999':{},
    'notd':{},
    'drome':{},
    'even':{},
    'odd':{},
    'total':0
    }
    batch_index = 1
    finished_hoc = False
    while not finished_hoc: # Keep going until day is finished
        for update_wrapper in get_old_updates(current_count['name'])['data']['children']: # Batchwise calling of counts
            update = update_wrapper['data']
            # if batch goes into the next day skip all further counts
            if name2date(update) < day_start:
                finished_hoc = True
                break
            # update last count so that the new batch starts at the last count
            current_count = update
            # check if relevant data exists
            if update['body'] == None:continue
            if update['author'] == None: continue
            # check if message is accepted count
            if update['stricken']: continue
            number = checknum(update['body'])
            if number == None:continue           

            
            # we got a valid count, add it to the daily hoc
            count_type = '{0:03d}'.format((int(number)%1000))
            even = (int(number)%2) == 0
            
            # handle 000,333,666,999
            if count_type in hoc:
                #check whether user is already in hoc
                if update['author'] in hoc[count_type]:
                    hoc[count_type][update['author']] += 1
                else:
                    hoc[count_type][update['author']] = 1
            # handle notd
            if count_type == notd:  
                if update['author'] in hoc['notd']:
                    hoc['notd'][update['author']] += 1
                else:
                    hoc['notd'][update['author']] = 1
            # handle dromes
            if number == number[::-1]:  
                if update['author'] in hoc['drome']:
                    hoc['drome'][update['author']] += 1
                else:
                    hoc['drome'][update['author']] = 1
            #handle even + odds
            if even:  
                if update['author'] in hoc['even']:
                    hoc['even'][update['author']] += 1
                else:
                    hoc['even'][update['author']] = 1
            else:
                if update['author'] in hoc['odd']:
                    hoc['odd'][update['author']] += 1
                else:
                    hoc['odd'][update['author']] = 1
            # add count to user
            if update['author'] in hoc['counts']:
                hoc['counts'][update['author']] += 1
            else:
                hoc['counts'][update['author']] = 1
            # add count to general counts
            hoc['total'] += 1
        # Batch done

        print('Day: {0}-{1}-{2} | Batch: {3:4d} | Total Counts: {4:>5} | Total Users: {5}'
        .format(
            day_obj.year,
            day_obj.month,
            day_obj.day,
            batch_index,
            hoc['total'],
            len(hoc['counts'])
        ))
        batch_index += 1
    #Day done

    #sort day hoc
    hoc_sorted = sorted(hoc['counts'].items(), key=lambda a : a[1], reverse=True)

    #include an indication for partial hocs
    if(hoc_part):
        hoc_part_extension = '_{0}_{1}_{2}'.format(part_hoc_time.seconds//3600,part_hoc_time.seconds//60%60,part_hoc_time.seconds%60)
        hoc_part_text = ' Up to {0}:{1}:{2}'.format(part_hoc_time.seconds//3600,part_hoc_time.seconds//60%60,part_hoc_time.seconds%60)
        hoc_part = False
    else:
        hoc_part_extension = ''
        hoc_part_text = ''

    with open('./daily_hocs/{0}-{1}-{2}{3}.txt'.format(day_obj.year,day_obj.month,day_obj.day,hoc_part_extension),mode='x') as f:
        f.write("#Daily Hoc For {0}-{1}-{2}{3}\n*Todays Counts: {4}*\n\n".format(day_obj.year,day_obj.month,day_obj.day,hoc_part_text,hoc['total']))
        f.write(" # |             User             | Counts | 000 | 333 | 666 | 999 | NotD | Drome\n")
        f.write("---|------------------------------|--------|-----|-----|-----|-----|------|------\n")
        index = 1

        wrc = "N/A"
        checked_wrc = False

        for user in hoc_sorted:
            f.write('{0:>3}|{1:>30}| {2:>6} '.format(index, user[0], user[1]))
            if user[0] in hoc['000']:
                f.write("| {0:>3} ".format(hoc['000'][user[0]]))
            else:
                f.write("|     ")
            if user[0] in hoc['333']:
                f.write("| {0:>3} ".format(hoc['333'][user[0]]))
            else:
                f.write("|     ")
            if user[0] in hoc['666']:
                f.write("| {0:>3} ".format(hoc['666'][user[0]]))
            else:
                f.write("|     ")
            if user[0] in hoc['999']:
                f.write("| {0:>3} ".format(hoc['999'][user[0]]))
            else:
                f.write("|     ")
            if user[0] in hoc['notd']:
                f.write("| {0:>4} ".format(hoc['notd'][user[0]]))
            else:
                f.write("|      ")
            if user[0] in hoc['drome']:
                f.write("| {0:>3} \n".format(hoc['drome'][user[0]]))
            else:
                f.write("|     \n")
            if checked_wrc==False and user[0] in hoc['000'] and user[0] in hoc['333'] and user[0] in hoc['666'] and user[0] in hoc['999'] and user[0] in hoc['notd'] and user[0] in hoc['drome']:
                wrc = user[0]
            checked_wrc = True
            index+=1
        
        f.write('{0} has achieved WRC today\n\n'.format(wrc))
        f.write('Debug: First message: {0}'.format(current_count))
        
    day_start -= 86400

    # write json to a file
    if hoc_part_text == '':
        with open('./daily_hocs_json/hoc.json','a') as f:
            f.write('"{0}-{1}-{2}"'.format(day_obj.year,day_obj.month,day_obj.day) + ': ' +json.dumps(hoc)+",\n    ")
            


            
