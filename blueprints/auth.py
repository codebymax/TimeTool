from flask import Blueprint, render_template, request, redirect, url_for, g, session
from database import mongo
import utils

auth = Blueprint('auth', __name__, template_folder='templates')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usersDB = mongo.db.users
        name = request.form['username']
        password = request.form['password']

        user = usersDB.find({'name': name, 'password': password})
        if user.count() != 0:
            session['_id'] = user[0]['_id']
            session['username'] = user[0]['name']
            session['status'] = user[0]['status']
            weeks = mongo.db.times.find({'_id': session['_id']})[0]['weeks']
            data = utils.current_week(weeks)
            if data is not None:
                session['start'] = data['start']
                session['end'] = data['end']
                session['hours'] = data['hours']
            return redirect(url_for('home'))

        return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


@auth.route('/auth/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        usersDB = mongo.db.users
        name = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            return render_template('sign_up.html', error='Passwords do not match.')
        users = usersDB.find()
        output = [{'_id': user['_id'], 'name': user['name']} for user in users]
        uid = -1
        for user in output:
            if user['_id'] > uid:
                uid = user['_id']
        uid += 1
        usersDB.insert_one({'_id': uid, 'name': name, 'password': password, 'status': 'out'})
        session['_id'] = uid
        session['username'] = name
        session['status'] = 'out'
        return redirect(url_for('home'))
    return render_template('sign_up.html')


@auth.route('/auth/logout')
def logout():
    try:
        if g.user:
            g.user = None
            return render_template('home.html')
    except AttributeError:
        render_template('home.html')
