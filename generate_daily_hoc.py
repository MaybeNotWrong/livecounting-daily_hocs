import praw
import time
import datetime
import re
import os
import json

agent = 'REDACTED'
r = praw.Reddit(client_id='REDACTED',
                client_secret="REDACTED",password='REDACTED',
                user_agent=agent,username='REDACTED')

config = {
    'thread': 'ta535s1hq2je',
    'batch_size': 100,
    'from': None,
    'date': None,
    'all': False,
    'counts': False,
    '000': False,
    '999': False,
    '333': False,
    '666': False,
    'notd': False,
    'drome': False,
    'even': False,
    'odd': False,
    'folder':None
}

livecounting = r.live(config['thread'])
livecounting._fetch()

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

def update_json(hoc):
    oldjson = ''
    with open('./daily_hocs_json/hoc.json') as f:
        oldjson = f.read()
    os.rename('./daily_hocs_json/hoc.json','./daily_hocs_json/~hoc.json')
    newjson = oldjson[:-2]
    newjson += ',\n    "{0}": '.format(hoc['date'])
    newjson += json.dumps(hoc)
    newjson += '\n}'
    with open('./daily_hocs_json/hoc.json','x') as f:
        f.write(newjson)

def write_day_hoc(day_hoc):
    sorted_hoc = sorted(day_hoc['counts'].items(),key=lambda a:a[1],reverse=True)
    filepath = './{0}/{1}.txt'.format(config['folder'],day_hoc['date'])
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(filepath,'x') as w:
        w.write("#Daily Hoc For {0}\n*Todays Counts: {1}*\n\n".format(day_hoc['date'],day_hoc['total']))
        w.write("\\#|Username{}{}{}{}{}{}{}{}{}\n".format(
            '|No. of Counts' if config['counts'] else '',
            '|Gets' if config['000'] else '',
            '|Assists' if config['999'] else '',
            '|666' if config['666'] else '',
            '|333' if config['333'] else '',
            '|NotD' if config['notd'] else '',
            '|Drome' if config['drome'] else '',
            '|Evens' if config['even'] else '',
            '|Odds' if config['odd'] else ''                    
        ))
        w.write("-|-{}{}{}{}{}{}{}{}{}\n".format(
            '|-' if config['counts'] else '',
            '|-' if config['000'] else '',
            '|-' if config['999'] else '',
            '|-' if config['666'] else '',
            '|-' if config['333'] else '',
            '|-' if config['notd'] else '',
            '|-' if config['drome'] else '',
            '|-' if config['even'] else '',
            '|-' if config['odd'] else ''                    
        ))
        index = 1

        wrc = "N/A"
        checked_wrc = False

        for user in sorted_hoc:
            w.write('{0}|/u/{1}|{2}'.format(index, user[0], user[1]))
            if config['000']:
                if user[0] in day_hoc['000']:
                    w.write('|{0}'.format(day_hoc['000'][user[0]]))
                else:
                    w.write('|')
            if config['999']:
                if user[0] in day_hoc['999']:
                    w.write('|{0}'.format(day_hoc['999'][user[0]]))
                else:
                    w.write('|')
            if config['666']:
                if user[0] in day_hoc['666']:
                    w.write('|{0}'.format(day_hoc['666'][user[0]]))
                else:
                    w.write('|')
            if config['333']:
                if user[0] in day_hoc['333']:
                    w.write('|{0}'.format(day_hoc['333'][user[0]]))
                else:
                    w.write('|')
            if config['notd']:
                if user[0] in day_hoc['notd']:
                    w.write('|{0}'.format(day_hoc['notd'][user[0]]))
                else:
                    w.write('|')
            if config['drome']:
                if user[0] in day_hoc['drome']:
                    w.write('|{0}'.format(day_hoc['drome'][user[0]]))
                else:
                    w.write('|')
            if config['even']:
                if user[0] in day_hoc['even']:
                    w.write('|{0}'.format(day_hoc['even'][user[0]]))
                else:
                    w.write('|')
            if config['odd']:
                if user[0] in day_hoc['odd']:
                    w.write('|{0}'.format(day_hoc['odd'][user[0]]))
                else:
                    w.write('|')
            w.write('\n')
            if checked_wrc==False and user[0] in day_hoc['000'] and user[0] in day_hoc['333'] and user[0] in day_hoc['666'] and user[0] in day_hoc['999'] and user[0] in day_hoc['notd'] and user[0] in day_hoc['drome']:
                wrc = user[0]
            checked_wrc = True
            index+=1
        
        w.write('\n\n{0} has achieved WRC today.'.format(wrc)) 

def update_hocs(hoc):
    config['folder'] = 'daily_hocs'
    config['counts'] = True
    config['000'] = True
    config['999'] = True
    config['666'] = True
    config['333'] = True
    config['notd'] = True
    config['drome'] = True
    write_day_hoc(hoc)
    config['folder'] = None
    config['counts'] = False
    config['000'] = False
    config['999'] = False
    config['666'] = False
    config['333'] = False
    config['notd'] = False
    config['drome'] = False
def update_simple(hoc):
    config['folder'] = 'daily_hocs_simple'
    config['counts'] = True
    write_day_hoc(hoc)
    config['folder'] = None
    config['counts'] = False
def update_ga(hoc):
    config['folder'] = 'daily_hocs_ga'
    config['counts'] = True
    config['000'] = True
    config['999'] = True
    write_day_hoc(hoc)
    config['folder'] = None
    config['counts'] = False
    config['000'] = False
    config['999'] = False
def update_eo(hoc):
    config['folder'] = 'daily_hocs_eo'
    config['counts'] = True
    config['even'] = True
    config['odd'] = True
    write_day_hoc(hoc)
    config['folder'] = None
    config['counts'] = False
    config['even'] = False
    config['odd'] = False

def generate_hoc():
    livecounting.contrib.add('#Generating Daily HoC\n\nDepending on todays counts this may take a while\n\n***\n\nPlease note that the HoC will be cut off at #100 to stay within Reddits character limit')

    start_time = time.time()
    day_end = start_time - (start_time - 4 * 3600) % 86400
    day_start = day_end - 86400

    start_message = get_old_updates(None)['data']['children'][0]['data']

    end_message = start_message
    for update_wrapper in get_old_updates(start_message['name'])['data']['children']:
        update = update_wrapper['data']
        if name2date(update) < day_end:
            break
        end_message = update
    current_count = end_message
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
    config['date'] = hoc['date']
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

        if(batch_index%10==0):print('Day: {0}-{1}-{2} | Batch: {3:4d} | Total Counts: {4:>5} | Total Users: {5}'
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
    print('Updating JSON')
    update_json(hoc)
    time.sleep(5)
    print('Updating HoCs')
    update_hocs(hoc)
    update_simple(hoc)
    update_ga(hoc)
    print('Sending HoC')
    with open('./daily_hocs_simple/{}.txt'.format(hoc['date'])) as f:
        hoc_text = ''
        index=0
        lines = f.readlines()
        if(len(lines) > 108):
            for line in lines:
                index+=1
                if index <= 105:
                    hoc_text += line
            hoc_text += '\n\n{}'.format(lines[-1])
            livecounting.contrib.add(hoc_text)
        else:
            for line in lines:
                index+=1
                hoc_text += line
            livecounting.contrib.add(hoc_text)
    
    # get link of daily hoc
    print('Finding HoC message')
    hoc_update = {}
    for update_wrapper in get_old_updates(None)['data']['children']:
        update = update_wrapper['data']
        if update['author'] == 'b66b' and update['body'][:5] == '#Dail':
            hoc_update = update
            break
    print('Generating sidebar')
    new_sidebar_text = '[Daily HoC for {0}](https://www.reddit.com/live/{1}/updates/{2}) as part of the [Counter of the Day Olympics](/r/livecounting/wiki/counteroftheday)\n\n'.format(hoc['date'],config['thread'],hoc_update['id'])
    with open('./daily_hocs_simple/{}.txt'.format(hoc['date'])) as f:
        index=0
        lines = f.readlines()
        for line in lines:
            index+=1
            if 4 <= index <= 8:
                new_sidebar_text += line
        new_sidebar_text += '\n\n{}'.format(lines[-1])
    print('Getting old sidebar')
    old_sidebar = livecounting.resources
    new_sidebar = list(old_sidebar.rpartition('######'))
    sidebar_hoc = list(new_sidebar[2].partition('**'))
    print('Preparing sidebar update')
    sidebar_hoc[0] = new_sidebar_text
    new_sidebar[2] = ''.join(sidebar_hoc)
    new_sidebar = ''.join(new_sidebar)
    print('Updating sidebar')
    livecounting.contrib.update(resources=new_sidebar)
    

while True:
    now = time.time()
    again = now - (now - 4 * 3600) % 86400 + 86415
    waittime = again-now
    time.sleep(waittime)
    try:
        generate_hoc()
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        print("ERROR")
    time.sleep(10)