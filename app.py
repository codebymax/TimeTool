from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import time, datetime

app = Flask(__name__)
app.config[
    "MONGO_URI"] = "mongodb+srv://rootUser:iowastatemongo@main-xz1r5.mongodb.net/timeDB?retryWrites=true&w=majority"
mongo = PyMongo(app)
usersDB = mongo.db.users
timesDB = mongo.db.times


# This endpoint will allow users to check in to start tracking time.
@app.route('/<int:uid>/in')
def check_in(uid):
    result, weeks = check_week(uid)
    if result:
        if

    # timesDB.insert_one({'_id': uid, 'time_in': timestamp})
    return str(date)


@app.route('/add/user')
def add_user():
    name = request.args.get('name')
    password = request.args.get('password')
    users = usersDB.find()
    output = [{'_id': user['_id'], 'name': user['name']} for user in users]
    uid = -1
    for user in output:
        if user['_id'] > uid:
            uid = user['_id']
    uid += 1
    usersDB.insert_one({'_id': uid, 'name': name, 'password': password})
    return str(uid)


def update_weeks(uid):
    times = timesDB.find({'_id': uid})
    weeks = []
    for item in times:
        for week in item['weeks']:
            weeks.append({'start': week['start'], 'end': week['end'], 'hours': week['hours']})

    start, end = find_current_week()
    for week in weeks:
        if week['start'] == start and week['end'] == end:
            return weeks

    weeks.append({'start': start, 'end': end, 'hours': 0, 'status': 'out'})

    return weeks


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


if __name__ == '__main__':
    app.run()
