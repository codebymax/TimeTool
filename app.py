from flask import Flask, request, jsonify, Response
from flask_pymongo import PyMongo
import time, datetime, json

app = Flask(__name__)
app.config[
    'MONGO_URI'] = 'mongodb+srv://rootUser:iowastatemongo@main-xz1r5.mongodb.net/timeDB?retryWrites=true&w=majority'
mongo = PyMongo(app)
usersDB = mongo.db.users
timesDB = mongo.db.times


# This endpoint will allow users to check in to start tracking time.
@app.route('/<int:uid>/in')
def check_in(uid):
    user = usersDB.find({'_id': uid})
    if user[0]['status'] != 'out':
        return Response(response='User is already checked in', status=409, mimetype='application/json')

    weeks = update_weeks(uid, 0)

    updated_user = {'$set': {'status': 'in'}}
    updated_times = {'$set': {'weeks': weeks}}
    timesDB.update_one({'_id': uid}, updated_times)
    usersDB.update_one({'_id': uid}, updated_user)

    return Response(response='Success!', status=200, mimetype='application/json')


@app.route('/<int:uid>/out')
def check_out(uid):
    user = usersDB.find({'_id': uid})
    if user.count() == 0:
        return Response(response='User not found', status=404, mimetype='application/json')
    if user[0]['status'] != 'in':
        return Response(response='User is not checked in', status=409, mimetype='application/json')

    weeks = update_weeks(uid, 1)

    updated_user = {'$set': {'status': 'out'}}
    updated_times = {'$set': {'weeks': weeks}}
    timesDB.update_one({'_id': uid}, updated_times)
    usersDB.update_one({'_id': uid}, updated_user)

    return Response(response='Success!', status=200, mimetype='application/json')


@app.route('/<int:uid>/status')
def user_status(uid):
    user = usersDB.find({'_id': uid})
    if user.count == 0:
        return Response(response='User not found', status=404, mimetype='application/json')
    else:
        result = {'Username': user[0]['name'], 'Status': user[0]['status']}
        return Response(response=json.dumps(result), status=200, mimetype='application/json')


@app.route('/<int:uid>/hours')
def user_hours(uid):
    start, end = find_current_week()
    user = usersDB.find({'_id': uid})
    user_data = timesDB.find({'_id': uid})
    if user.count == 0:
        return Response(response='User not found', status=404, mimetype='application/json')
    else:
        if user_data.count() == 0:
            return Response(response='User has no times', status=404, mimetype='application/json')

        for week in user_data[0]['weeks']:
            if week['start'] == start and week['end'] == end:
                result = {'Username': user[0]['name'], 'Hours': week['hours']}
                return Response(response=json.dumps(result), status=200, mimetype='application/json')


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


# Function to update a users weeks in the database. The original
# weeks array must be input along with a switch denoting if the user
# is clocking in or out.
# switch == 0 -> clocking in
# switch == 1 -> clocking out
def update_weeks(uid, switch):
    start, end = find_current_week()
    weeks = get_weeks(uid)
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


def get_weeks(uid):
    times = timesDB.find({'_id': uid})
    if times.count() == 0:
        timesDB.insert_one({'_id': uid, 'weeks': []})
    weeks = []
    for week in times[0]['weeks']:
        weeks.append({'start': week['start'], 'end': week['end'], 'hours': week['hours'], 'times': week['times']})

    return weeks


def find_current_week():
    months = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    today = datetime.datetime.today()

    start = {'year': today.year, 'month': today.month, 'day': today.day}

    if today.weekday() > 4:
        raise Exception('It\'s not a weekday!')
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
