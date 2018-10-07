import json
import os

config = {
    'date': '2018-10-6',
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

def write_hoc(day_hoc):
    sorted_hoc = sorted(day_hoc['counts'].items(),key=lambda a:a[1],reverse=True)
    filepath = './{0}/{1}.txt'.format(config['folder'],day_hoc['date'])
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(filepath,'x') as w:
        w.write("#Daily Hoc For {0}\n*Todays Counts: {1}*\n\n".format(day_hoc['date'],day_hoc['total']))
        w.write("\#|Username{}{}{}{}{}{}{}{}{}\n".format(
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
        
        w.write('{0} has achieved WRC today\n\n'.format(wrc)) 

with open('./daily_hocs_json/hoc.json') as f:
    hoc = json.load(f)

    if config['all']:
        for day_hoc_key in hoc:
            day_hoc = hoc[day_hoc_key]
            write_hoc(day_hoc)

            
    else:
        day_hoc = hoc[config['date']]
        write_hoc(day_hoc)