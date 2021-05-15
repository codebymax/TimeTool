from flask import Blueprint, render_template, request, redirect, url_for, g, session
from database import mongo
import utils

auth = Blueprint('auth', __name__, template_folder='templates')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    usersDB = mongo.db.users
    error = None
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']
        user = usersDB.find({'name': name, 'password': password})
        if user.count() != 0:
            session['_id'] = user[0]['_id']
            session['username'] = user[0]['name']
            g.user = {'_id': session['_id'], 'username': session['username']}
            return redirect(url_for('home'))
        error = 'Invalid credentials'
        return render_template('login_page.html', error=error)
    return render_template('login_page.html')


@auth.route('/auth/logout')
def logout():
    if g.user:
        g.user = {}
        return utils.build_response('Success!', 200)
    return utils.build_response('Not logged in.', 404)


@auth.route('/auth/add')
def add_user():
    usersDB = mongo.db.users
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
