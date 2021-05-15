from flask import Response
import time, datetime


# Function to update a users weeks in the database. The original
# weeks array must be input along with a switch denoting if the user
# is clocking in or out.
# switch == 0 -> clocking in
# switch == 1 -> clocking out
def update_weeks(uid, switch, timesDB):
    start, end = find_current_week()
    weeks = get_weeks(uid, timesDB)
    print(weeks)
    for week in weeks:
        if week['start'] == start and week['end'] == end:
            cur_time = time.time()
            if switch == 0:
                week['times'].append({'start': cur_time, 'end': 0.0, 'hours': 0.0})
            else:
                for item in week['times']:
                    if item['end'] == 0.0:
                        item['end'] = cur_time
                        item['hours'] = round(((item['end'] - item['start']) / 3600.0), 2)
                        week['hours'] = round(week['hours'] + item['hours'], 2)
            return weeks

    weeks.append({'start': start, 'end': end, 'hours': 0, 'times': [{'start': time.time(), 'end': 0.0, 'hours': 0.0}]})

    return weeks


def get_weeks(uid, timesDB):
    times = timesDB.find({'_id': uid})
    if times.count() == 0:
        timesDB.insert_one({'_id': uid, 'weeks': []})
    weeks = []
    for week in times[0]['weeks']:
        weeks.append({'start': week['start'], 'end': week['end'], 'hours': week['hours'], 'times': week['times']})

    return weeks


def current_week(weeks):
    start, end = find_current_week()

    for week in weeks:
        if week['start'] == start and week['end'] == end:
            return week

    return None



def find_current_week():
    months = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    today = datetime.datetime.today()

    start = {'year': today.year, 'month': today.month, 'day': today.day}

    for num in range(today.weekday()):
        if start['day'] == 1:
            if start['month'] == 1:
                start['day'] = months[12]
                start['month'] = 12
                start['year'] -= 1
            else:
                start['day'] = months[start['month'] - 1]
                start['month'] -= 1
        else:
            start['day'] -= 1

    end = start.copy()

    for num in range(4):
        if end['day'] + 1 > months[end['month']]:
            if end['month'] == 12:
                end['day'] = 1
                end['month'] = 1
            else:
                end['day'] = 1
                end['month'] += 1
        else:
            end['day'] += 1

    str_start = date_str(start)
    str_end = date_str(end)

    return str_start, str_end


def date_str(date):
    return str(date['year']) + '-' + str(date['month']) + '-' + str(date['day'])


def build_response(response, code):
    return Response(response=response, status=code, mimetype='application/json')
