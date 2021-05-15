import json, string, random

from flask import Flask, render_template, session, g

import utils
from blueprints.auth import auth
from database import mongo

uri = 'mongodb+srv://rootUser:iowastatemongo@main-xz1r5.mongodb.net/timeDB?retryWrites=true&w=majority'

app = Flask(__name__)
app.register_blueprint(auth)
app.secret_key = str(''.join(random.choice(string.ascii_letters)) for i in range(20))

mongo.init_app(app, uri=uri)
usersDB = mongo.db.users
timesDB = mongo.db.times


@app.before_request
def load_user():
    if "_id" in session:
        g.user = {'_id': session['_id'], 'username': session['username']}


@app.route('/home')
def home():
    return render_template('home.html')


# This endpoint will allow users to check in to start tracking time.
@app.route('/<int:uid>/in')
def check_in(uid):
    user = usersDB.find({'_id': uid})
    if user[0]['status'] != 'out':
        return utils.build_response('User is already checked in', 409)

    weeks = utils.update_weeks(uid, 0, timesDB)

    updated_user = {'$set': {'status': 'in'}}
    updated_times = {'$set': {'weeks': weeks}}
    timesDB.update_one({'_id': uid}, updated_times)
    usersDB.update_one({'_id': uid}, updated_user)

    return utils.build_response('Success!', 200)


@app.route('/<int:uid>/out')
def check_out(uid):
    user = usersDB.find({'_id': uid})
    if user.count() == 0:
        return utils.build_response('User not found', 404)
    if user[0]['status'] != 'in':
        return utils.build_response('User is not checked in', 409)

    weeks = utils.update_weeks(uid, 1, timesDB)

    updated_user = {'$set': {'status': 'out'}}
    updated_times = {'$set': {'weeks': weeks}}
    timesDB.update_one({'_id': uid}, updated_times)
    usersDB.update_one({'_id': uid}, updated_user)

    return utils.build_response('Success!', 200)


@app.route('/<int:uid>/status')
def user_status(uid):
    user = usersDB.find({'_id': uid})
    if user.count == 0:
        return utils.build_response('User not found', 404)
    else:
        result = {'Username': user[0]['name'], 'Status': user[0]['status']}
        return utils.build_response(json.dumps(result), 200)


@app.route('/<int:uid>/hours')
def user_hours(uid):
    start, end = utils.find_current_week()
    user = usersDB.find({'_id': uid})
    user_data = timesDB.find({'_id': uid})
    if user.count == 0:
        return utils.build_response('User not found', 404)
    else:
        if user_data.count() == 0:
            return utils.build_response('User has no times', 404)

        for week in user_data[0]['weeks']:
            if week['start'] == start and week['end'] == end:
                result = {'Username': user[0]['name'], 'Hours': week['hours']}
                return utils.build_response(json.dumps(result), 200)


if __name__ == '__main__':
    app.run()
