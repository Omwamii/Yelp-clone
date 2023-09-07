#!/usr/bin/python3
""" Starts a Flask Web Application """
from models import storage
from models.county import County
from models.city import City
from models.amenity import Amenity
from models.biz import Biz
from models.user import User
from models.review import Review
from os import environ
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask import session
from models import storage
import requests
# from flask_bcrypt import Bcrypt
from passlib.hash import sha256_crypt
import uuid

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
app.secret_key = b'd_~!H|-%^#@lM])*$/<'
# bcrypt = Bcrypt(app)

# app.jinja_env.trim_blocks = True
# app.jinja_env.lstrip_blocks = True


@app.teardown_appcontext
def close_db(error):
    """ Remove the current SQLAlchemy Session """
    storage.close()


@app.route('/', strict_slashes=False)
def index():
    """ Home page """
    if 'username' in session:
        print(f'Logged in as {session["username"]}')
    print('You are not logged in')
    counties = storage.all(County).values()
    counties = sorted(counties, key=lambda k: k.name)
    county_cities = []

    for county in counties:
        county_cities.append([county, sorted(county.cities, key=lambda k: k.name)])

    amenities = storage.all(Amenity).values()
    amenities = sorted(amenities, key=lambda k: k.name)

    bizes = storage.all(Biz).values()
    bizes = sorted(bizes, key=lambda k: k.name)

    return render_template('index.html',
                           counties=county_cities,
                           amenities=amenities,
                           bizes=bizes,
                           cache_id=uuid.uuid4())


@login_manager.user_loader
def load_user(user_id):
    return storage.get(User, user_id)

@app.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
    """ Authenticate user account """
    if request.method == "POST":
        form_data = request.form
        u_name = form_data['username']
        passwd = form_data['password']

        all_users = storage.all(User)
        user = None
        for u_id, u_obj in all_users.items():
            if u_obj.user_name == u_name:
                user = u_obj
        if user is None:
            # error -> no such user
            flash("Wrong username or password")
            return redirect(url_for('login'))

        # if bcrypt.check_password_hash(user.password, passwd):
        if sha256_crypt.verify(passwd, user.password):
            print("---- Passwords match! Auth successful ----")
            login_user(user) # passwords match
            return render_template('login_success.html')
        else:
            flash("Wrong username or password")
            return redirect(url_for('login'))
    else:
        return render_template('log_user.html')

@app.route('/regUser', methods=['GET', 'POST'], strict_slashes=False)
def register_user():
    """ register a user account """
    if request.method == "POST":
        form_data = request.form
        fname = form_data['fname']
        lname = form_data['lname']
        u_name = form_data['username']
        email = form_data['email']
        passwd = str(form_data['password'])
        confirm_pass = str(form_data['confirmation'])

        if confirm_pass != passwd:
            # return error, passwords dont match
            flash("Passwords dont match!")
            return redirect(url_for('register_user'))

        all_users = storage.all(User)
        for obj_id, u_obj in all_users.items():
            if u_obj.user_name == u_name:
                # flash error: user not unique
                flash("Username already exists!")
                return redirect(url_for('register_user'))

        # encrypt password and create user
        # hashed_p = bcrypt.generate_password_hash(passwd).decode('utf-8')
        hashed_pass = sha256_crypt.hash(passwd)
        data = {'first_name': fname, 'last_name': lname,
                'user_name': u_name, 'email': email,
                'password': hashed_pass}
        url = "http://192.168.100.100:5000/api/v1/users/" # app API

        res = requests.post(url, json=data)
        if res.status_code > 201:
            print(f"An error occured: {res.status_code}")
        else:
            print(f"User {u_name} created successfuly")
        return redirect(url_for('login'))
    else:
        return render_template('register_user.html')

@app.route('/regBiz', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def register_biz():
    """ register a business account """
    if request.method == "POST":
        form_data = request.form
        city_id = int(form_data['city'])
        user_id = current_user.id
        name = form_data['bizname']
        description = form_data['description']
        lat = form_data['latitude']
        long = form_data['longitude']
        category_id = form_data['category']

        data = {'city_id': city_id, 'user_id': user_id, 'name': name, 
                'description': description, 'latitude': lat, 
                'longitude': long, 'category_id': category_id}

        url = f'http://192.168.100.100:5000/api/v1/bizes/cities/{city_id}/bizes'
        res = requests.post(url, json=data)
        if res.status_code > 201:
            print(f"Error creating business account: {res.status_code}")
        else:
            print("Business account created successfuly")
        return redirect(url_for('goto_business', biz_id=2)) # redirect to biz pg
    else:
        # make request to get all biz categories
        categories = storage.all(Category)  # list of categories to select
        cities = storage.all(City)
        return render_template('register_biz.html', categories=categories,
                               cities=cities)

@app.route('/logout', strict_slashes=False)
@login_required
def logout():
    """ logout user """
    logout_user()
    return redirect(url_for('login'))

@app.route('/business/<biz_id>', methods=['GET', 'POST'], strict_slashes=False)
def goto_biz(biz_id):
    """ go to a business """
    if request.method == "POST":
        form_data = request.form
        text = form_data['review']
        user_id = current_user.id
        biz_id = biz_id

        data = {'user_id': user_id, 'biz_id': biz_id,
                'text': text}
        # create review obj & save
        new_review = Review(**data)
        new_review.save
        if new_review:
            print(new_review.to_dict()) # confirm
            flash("Review posted!")
        else:
            flash("There was an error processing your review")
        return redirect(url_for('goto_biz', biz_id=biz_id))
    else:
        biz_obj = storage.get(Biz, biz_id)
        return render_template('business.html', biz=biz_obj)

@app.route('/review/<rev_id>', strict_slashes=False)
def goto_review(rev_id): # edit?
    """ go to a review """
    # get review with api and render with page
    pass

@app.route('/bizes', strict_slashes=False)
def show_bizes():
    """ Show businesses """
    bizes_dict = storage.all(Biz)
    bizes = list()
    for biz_id, biz_obj in bizes_dict.items():
        bizes.append(biz_obj)
        print(biz_obj.get_category)
    return render_template('bizes.html', bizes=bizes)

@app.route('/reviews', strict_slashes=False)
def show_reviews():
    """ Show general reviews """
    reviews = storage.all(Review)
    return render_template('reviews.html', reviews=reviews)


if __name__ == "__main__":
    """ Main Function """
    app.run(host='0.0.0.0', port=5500, debug=True)
