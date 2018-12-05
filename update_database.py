import datetime as dt
import pytz
from pymongo import MongoClient
from pymongo import errors as mdberr
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client.get_database('livecounting')
tz = pytz.timezone('US/Eastern')
utc = pytz.timezone('UTC')

search_offset = 0

# Get last inserted day


def get_last_day(offset=0):

    last_day = 0
    try:
        last_day = db.get_collection('counts_by_day').find().sort(
            'timestamp', -1).limit(1).next()['timestamp']
    except StopIteration:
        last_day = None

    if last_day == None:
        last_day = db.get_collection('counts').find().sort(
            'time', 1).limit(1).skip(1).next()['time'] - 86400

    # Try to get start of the day

    return (tz.localize(dt.datetime.combine(dt.datetime.fromtimestamp(last_day, tz).date() + dt.timedelta(1+offset), dt.time(0, 0)), is_dst=None),
            tz.localize(dt.datetime.combine(dt.datetime.fromtimestamp(last_day, tz).date() + dt.timedelta(2+offset), dt.time(0, 0)), is_dst=None))


def get_latest_day():
    return tz.localize(dt.datetime.combine(dt.datetime.now().date(), dt.time(0, 0)))


def run():
    global search_offset
    while get_latest_day() > get_last_day()[0]:
        succesful = False
        day = get_last_day(offset=search_offset)
        day_start = day[0].timestamp()
        day_end = day[1].timestamp()
        cursor = db.get_collection('counts').aggregate(
            [
                {
                    '$match':
                    {
                        'time':
                        {
                            '$gt': day_start,
                            '$lte': day_end
                        }
                    }
                },
                {
                    '$group':
                    {
                        '_id': '$author',
                        'counts': {'$sum': 1}
                    }
                },
                {
                    '$project':
                    {
                        '_id': 0,
                        'author': '$_id',
                        'counts': 1
                    }
                },
                {
                    '$addFields':
                    {
                        'year': day[0].year,
                        'month':day[0].month,
                        'day':day[0].day,
                        'timestamp':day_start
                    }
                }
            ]
        )
        try:
            res = db.get_collection('counts_by_day').insert_many(cursor)
            print('Succesfully inserted {} Documents'.format(len(res.inserted_ids)))
            succesful = True
        except mdberr.InvalidOperation:
            search_offset += 1
            succesful = False
        finally:
            if succesful:
                search_offset = 0
