from flask import (
    Flask, render_template, request, redirect, jsonify, url_for, flash)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, MenuItem
from database_setup_zb import Base, Alcohol, Cocktail, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///cocktailcatolog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
            app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    token = result.split(',')[0].split(':')[1].replace('"', '')
    url = 'https://graph.facebook.com/v2.8/me?access_token=%s' % token \
        + '&fields=name,id,email'
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s' % token \
        + '&redirect=0&height=200&width=200'
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: '
    output += '150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;">'

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<h2>Email:'
    output += login_session['email']
    output += '</h2>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Restaurant Information
@app.route('/alcohol/<int:alcohol_id>/list/JSON')
def listJSON(alcohol_id):
    alcohol = session.query(Alcohol).filter_by(id=alcohol_id).one()
    items = session.query(Cocktail).filter_by(
        alcohol_id=alcohol_id).all()
    return jsonify(alcohol_list=[i.serialize for i in items])


@app.route('/alcohol/<int:alcohol_id>/list/<int:cocktail_id>/JSON')
def cocktailJSON(alcohol_id, cocktail_id):
    item = session.query(Cocktail).filter_by(id=cocktail_id).one()
    return jsonify(item=item.serialize)


@app.route('/alcohol/JSON')
def alcoholJSON():
    alcohols = session.query(Alcohol).all()
    return jsonify(alcohols=[r.serialize for r in alcohols])


@app.route('/')
@app.route('/alcohol/')
def showAlcohols():
    alcohols = session.query(Alcohol).order_by(asc(Alcohol.name))
    if 'username' not in login_session:
        return render_template('publicalcohols.html', alcohols=alcohols)
    else:
        return render_template('alcohols.html', alcohols=alcohols)


# Create a new Spirit
@app.route('/alcohol/new/', methods=['GET', 'POST'])
def newAlcohol():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name'] == '':
            flash('Name is empty')
            return render_template('newAlcohol.html')
        newAlcohol = Alcohol(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newAlcohol)
        flash('New Alcohol %s Successfully Created' % newAlcohol.name)
        session.commit()
        return redirect(url_for('showAlcohols'))
    else:
        return render_template('newAlcohol.html')


# Edit a spirit if creater of the spirit
@app.route('/alcohol/<int:alcohol_id>/edit/', methods=['GET', 'POST'])
def editAlcohol(alcohol_id):
    editedAlcohol = session.query(
        Alcohol).filter_by(id=alcohol_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedAlcohol.user_id != login_session['user_id']:
        flash('Alcohol unsuccessfully edited must be author to edit')
        return redirect(url_for('showList', alcohol_id=alcohol_id))
    if request.method == 'POST':
        if request.form['name'] == '':
            flash('Name cannot be empty')
            return render_template('editAlcohol.html', alcohol=editedAlcohol)

        if request.form['name']:
            editedAlcohol.name = request.form['name']
            flash('Alcohol Successfully Edited %s' % editedAlcohol.name)
            return redirect(url_for('showAlcohols'))
    else:
        return render_template('editAlcohol.html', alcohol=editedAlcohol)


# Delete a spirit is creater of the spirit
@app.route('/alcohol/<int:alcohol_id>/delete/', methods=['GET', 'POST'])
def deleteAlcohol(alcohol_id):
    alcoholToDelete = session.query(
        Alcohol).filter_by(id=alcohol_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if alcoholToDelete.user_id != login_session['user_id']:
        flash('Spirit unsuccessfully deleted must be author to edit')
        return redirect(url_for('showList', alcohol_id=alcohol_id))
    if request.method == 'POST':
        # must delete connected cocktails
        cocktailsToDelete = session.query(
            Cocktail).filter_by(alcohol_id=alcohol_id).all()
        for i in cocktailsToDelete:
            session.delete(i)
        session.delete(alcoholToDelete)
        flash('%s Successfully Deleted' % alcoholToDelete.name)
        session.commit()
        return redirect(url_for('showAlcohols', alcohol_id=alcohol_id))
    else:
        return render_template('deleteAlcohol.html', alcohol=alcoholToDelete)


# Show a cocktails for spirit
@app.route('/alcohol/<int:alcohol_id>/')
@app.route('/alcohol/<int:alcohol_id>/list/')
def showList(alcohol_id):
    alcohol = session.query(Alcohol).filter_by(id=alcohol_id).one()
    creator = getUserInfo(alcohol.user_id)
    items = session.query(Cocktail).filter_by(
        alcohol_id=alcohol_id).all()
    if 'username' not in login_session:
        return render_template('publicList.html', items=items, alcohol=alcohol,
                               creator=creator)
    else:
        return render_template('list.html', items=items, alcohol=alcohol,
                               creator=creator)


# Create a new Cocktail
@app.route('/alcohol/<int:alcohol_id>/list/new/', methods=['GET', 'POST'])
def newCocktail(alcohol_id):
    if 'username' not in login_session:
        return redirect('/login')
    alcohol = session.query(Alcohol).filter_by(id=alcohol_id).one()

    if request.method == 'POST':
        if request.form['name'] != '' and request.form['ingredients'] != '':
            flash('Name and ingredients must not be empty')
            return render_template('newCocktail.html', alcohol_id=alcohol_id)

        newItem = Cocktail(name=request.form['name'],
                           ingredients=request.form['ingredients'],
                           picture=request.form['picture'],
                           alcohol_id=alcohol.id,
                           user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New Cocktail %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showList', alcohol_id=alcohol_id))
    else:
        return render_template('newCocktail.html', alcohol_id=alcohol_id)


# Edit a cocktail if creater of the the cocktail
@app.route('/alcohol/<int:alcohol_id>/list/<int:cocktail_id>/edit',
           methods=['GET', 'POST'])
def editCocktail(alcohol_id, cocktail_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Cocktail).filter_by(id=cocktail_id).one()
    alcohol = session.query(Alcohol).filter_by(id=alcohol_id).one()
    if login_session['user_id'] != editedItem.user_id:
        flash('Item unsuccessfully deleted must be author of cocktail to edit')
        return redirect(url_for('showList', alcohol_id=alcohol_id))
    if request.method == 'POST':
        if request.form['name'] != '' and request.form['ingredients'] != '':
            flash('Name and ingredients must not be empty')
            return render_template('editCocktail.html',
                                   alcohol_id=alcohol_id,
                                   cocktail_id=cocktail_id,
                                   item=editedItem)

        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['ingredients']:
            editedItem.ingredients = request.form['ingredients']
        if request.form['picture']:
            editedItem.picture = request.form['picture']
        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('showList', alcohol_id=alcohol_id))
    else:
        return render_template('editCocktail.html', alcohol_id=alcohol_id,
                               cocktail_id=cocktail_id, item=editedItem)


# Delete a cocktail if creator of cocktail
@app.route('/alcohol/<int:alcohol_id>/list/<int:cocktail_id>/delete',
           methods=['GET', 'POST'])
def deleteCocktail(alcohol_id, cocktail_id):
    if 'username' not in login_session:
        return redirect('/login')
    alcohol = session.query(Alcohol).filter_by(id=alcohol_id).one()
    itemToDelete = session.query(Cocktail).filter_by(id=cocktail_id).one()
    if login_session['user_id'] != itemToDelete.user_id:
        flash(
            'Item unsuccessfully deleted must be author of cocktail to delete')
        return redirect(url_for('showList', alcohol_id=alcohol_id))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showList', alcohol_id=alcohol_id))
    else:
        return render_template('deleteCocktail.html', item=itemToDelete)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showAlcohols'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showAlcohols'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
