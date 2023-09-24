#!/usr/bin/python3
""" Starts a Flask Web Application """
from models import storage
from models.county import County
from models.city import City
from models.amenity import Amenity
from models.biz import Biz
from models.user import User
from models.review import Review
from models.category import Category
from os import environ
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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
app.config['MESSAGE_FLASHING_OPTIONS'] = {'duration': 5} # not working?
# bcrypt = Bcrypt(app)

# app.jinja_env.trim_blocks = True
# app.jinja_env.lstrip_blocks = True


@app.teardown_appcontext
def close_db(error):
    """ Remove the current SQLAlchemy Session """
    storage.close()


@app.route('/', methods=['GET', 'POST'], strict_slashes=False)
def index():
    """ Home page """
    # fetch the most recent reviews made
    if request.method == "POST":
        if request.form.get('like'):
            if not current_user.is_authenticated:
                print("User Not authenticated")
                flash("Please login to complete action", category="warning")
                return redirect(url_for('login'))
            res = update_likes(request.form['like'])
            if res != 200:
                flash("Action was unsuccessful", category="danger") # error occured
            else:
                flash("Action was successful", category="success")
        return redirect(url_for('index'))
    else:
        rev_dict = storage.all(Review)
        reviews = list()
        for review in rev_dict.values():
            if len(reviews) == 6:
                break; # render only 10 latest reviews, load more in page
            reviews.append(review)
        # fetch business categories
        cat_dict = storage.all(Category)
        categories = list()
        for category in cat_dict.values():
            categories.append(category)
        return render_template('index.html',
                               reviews=reviews,
                               categories=categories,
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
            flash("Wrong username or password", category="danger")
            return redirect(url_for('login'))

        # if bcrypt.check_password_hash(user.password, passwd):
        if sha256_crypt.verify(passwd, user.password):
            print("---- Passwords match! Auth successful ----")
            flash("Logged in successfuly", category="success")
            login_user(user) # passwords match
            return redirect(url_for('dashboard'))
        else:
            flash("Wrong username or password")
            return redirect(url_for('login'))
    else:
        return render_template('log_user.html', cache_id=uuid.uuid4())

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
            flash("Passwords dont match!", category="danger")
            return redirect(url_for('register_user'))

        all_users = storage.all(User)
        for obj_id, u_obj in all_users.items():
            if u_obj.user_name == u_name:
                # flash error: user not unique
                flash("Username already exists!", category="warning")
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
        return render_template('register_user.html', cache_id=uuid.uuid4())

@app.route('/regBiz', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def register_biz():
    """ register a business account """
    if request.method == "POST":
        form_data = request.form
        city_id = form_data['city']
        user_id = current_user.id
        name = form_data['bizname']
        description = form_data['description']
        lat = form_data['latitude']
        long = form_data['longitude']
        category_id = form_data['category']

        data = {'city_id': city_id, 'user_id': user_id, 'name': name, 
                'description': description, 'latitude': lat, 
                'longitude': long, 'category_id': category_id}

        url = f'http://192.168.100.100:5000/api/v1/cities/{city_id}/bizes'
        res = requests.post(url, json=data)
        if res.status_code > 201:
            print(f"Error creating business account: {res.status_code}")
        else:
            print("Business account created successfuly")
        return redirect(url_for('goto_biz', biz_id=2)) # redirect to biz pg
    else:
        # make request to get all biz categories
        category_dict = storage.all(Category)  # list of categories to select
        categories = list()
        for cat_id, cat_obj in category_dict.items():
            categories.append(cat_obj)
        city_dict = storage.all(City)
        cities = list()
        for city_id, city_obj in city_dict.items():
            cities.append(city_obj)
        return render_template('register_biz.html', categories=categories,
                               cities=cities, cache_id=uuid.uuid4())

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
        # implement adding business to favorite & liking reviews
        if not current_user.is_authenticated:
            flash("PLease Login to complete action", category="warning")
            return redirect(url_for('login'))
        if request.form.get('like'):
            if not current_user.is_authenticated:
                print("User Not authenticated")
                flash("Please login to complete action", category="warning")
                return redirect(url_for('login'))
            res = update_likes(request.form['like'])
            if res != 200:
                flash("Action was unsuccessful", category="danger") # error occured
            else:
                flash("Action was successful", category="success")
        if request.form.get('like-biz'):
            # implement adding business to collection
            biz_id = request.form['like-biz']
            user = storage.get(User, current_user.id)
            if biz_id in user.fav_bizes:
                # remove business from collection
                user.fav_bizes.remove(biz_id)
            else:
                # add business to collection
                user.fav_bizes.append(biz_id)
            user.save()
            storage.save()
        return redirect(url_for('goto_biz', biz_id=biz_id))
    else:
        biz_obj = storage.get(Biz, biz_id)
        amenities = list()
        print("Biz amenities ")
        print(biz_obj.amenity_ids)
        for amenity in biz_obj.amenity_ids:
            amen_obj = storage.get(Amenity, amenity)
            if amen_obj:
                amenities.append(amen_obj)
        print("Business reviews list ids")
        print(biz_obj.reviews)
        reviews = list()
        count = 0
        rating = 0
        rates = {'5': 0, '4': 0, '3': 0, '2': 0, '1': 0}
        for review in biz_obj.reviews:
            count += 1
            rating += int(review.rating)
            rates[review.rating] += 1
            reviews.append(review)
        print(rates)
        if len(reviews) == 0:
            count = 1
        avg = rating/count
        round_rating = round(avg)
            
        return render_template('business.html', biz=biz_obj,
                               reviews=reviews,
                               rating=round_rating,
                               avg_rating=avg,
                               amenities=amenities,
                               rates=rates,
                               cache_id=uuid.uuid4())

@app.route('/bizes', strict_slashes=False)
def show_bizes():
    """ Show businesses """
    bizes_dict = storage.all(Biz)
    bizes = list()
    for biz_id, biz_obj in bizes_dict.items():
        bizes.append(biz_obj)
    return render_template('bizes.html', bizes=bizes, cache_id=uuid.uuid4())

@app.route('/reviews', methods=['GET', 'POST'], strict_slashes=False)
def show_reviews():
    """ Show general reviews """
    if request.method == "POST":
        if request.form.get('like'):
            if not current_user.is_authenticated:
                print("User Not authenticated")
                flash("Please login to complete action", category="warning")
                return redirect(url_for('login'))
            res = update_likes(request.form['like'])
            if res != 200:
                flash("Action was unsuccessful", category="danger") # error occured
            else:
                flash("Action was successful", category="success")
        return redirect(url_for('show_reviews'))
    else:
        rev_dict = storage.all(Review)
        reviews = list()
        for review in rev_dict.values():
            reviews.append(review)
        return render_template('reviews.html', reviews=reviews, 
                               cache_id=uuid.uuid4())

@app.route('/dashboard', strict_slashes=False)
@login_required
def dashboard():
    """ render dashboard """
    print("printing reviews")
    print(current_user.reviews)
    # fetch number of reviews (to display)
    rev_objs = storage.all(Review)
    revs = list()
    for rev in rev_objs.values():
        if rev.user_id == current_user.id:
            revs.append(rev)
    num_reviews = len(revs)
    revs.clear() # clear list
    return render_template('dashboard.html', num_reviews=num_reviews,
                           cache_id=uuid.uuid4())

@app.route('/mybizes', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def my_bizes():
    """ show businesses listed by logged in user """
    if request.method == "POST":
        # Handle business deletion, for now
        biz_id = request.form.get('id')
        biz_obj = storage.get(Biz, biz_id)
        # first start by deleting all reviews related to the biz
        biz_reviews = list()
        rev_list = storage.all(Review).values()
        for rev in rev_list:
            if rev.biz_id == biz_id:
                biz_reviews.append(rev)
        for review in biz_reviews:
            storage.delete(review)
        storage.delete(biz_obj)
        storage.save()
        flash("Business deleted successfully", category="success")
        return redirect(url_for('my_bizes'))
        # make api call to drop the business
    else:
        biz_dict = storage.all(Biz)
        bizes = list()
        for biz in biz_dict.values():
            if biz.user_id == current_user.id:
                bizes.append(biz)
        return render_template('my_bizes.html', bizes=bizes, 
                               cache_id=uuid.uuid4())

@app.route('/myreviews', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def my_reviews():
    """ show reviews posted by logged in user """
    if request.method == "POST":
        # Handle Review deletion, for now
        rev_id = request.form.get('id')
        rev_obj = storage.get(Review, rev_id)
        storage.delete(rev_obj) # delete the review object
        storage.save()
        return redirect(url_for('my_reviews'))
        # make api call to drop the Review (from jquery)
    else:
        rev_dict = storage.all(Review)
        reviews = list()
        for rev in rev_dict.values():
            if rev.user_id == current_user.id:
                reviews.append(rev)
        return render_template('my_reviews.html', reviews=reviews, 
                               cache_id=uuid.uuid4())


@app.route('/review/<biz_id>', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def write_review(biz_id):
    """ go to a business """
    if request.method == "POST":
        form_data = request.form
        text = form_data['review']
        if form_data.get('rate'):
            rating = form_data['rate']
        else:
            rating = 1
        user_id = current_user.id
        biz_id = biz_id

        data = {'user_id': user_id, 'biz_id': biz_id,
                'rating': rating, 'text': text}
        # create review obj using api
        url = f"http://192.168.99.101:5000/api/v1/bizes/{biz_id}/reviews"

        res = requests.post(url, json=data)

        if res.status_code <= 201:
            print("Review posted successfully")
            flash("Review posted!", "success")
        else:
            print("Error creating review")
            flash("There was an error processing your review", "danger")
        return redirect(url_for('goto_biz', biz_id=biz_id))
    else:
        biz_obj = storage.get(Biz,biz_id)
        return render_template('write_review.html', biz=biz_obj,
                               cache_id=uuid.uuid4())


def update_likes(rev_id):
    """ update review likes """
    # url = f"http://192.168.100.100:5000/api/v1/reviews/{rev_id}
    user = storage.get(User, current_user.id)
    review = storage.get(Review, rev_id)
    old_likes = review.found_useful
    print(f"-----User {current_user.user_name}'s Favorite reviews ----")
    print(user.fav_reviews)
    print(f"Likes: {old_likes}")
    likes = int(review.found_useful)
    if rev_id in user.fav_reviews:
        # User unliked, remove review from user's favs
        print("Removing review from liked reviews")
        user.fav_reviews.remove(rev_id)
        likes -= 1
    else:
        # user liked review
        print("Review added to user's favorites")
        user.fav_reviews.append(rev_id)
        if review.found_useful:
            likes += 1
        else:
            likes = 1
    review.found_useful = likes # update
    print()
    print(f"New user fav reviews: {user.fav_reviews}")
    print(f"New likes: {review.found_useful}")
    print()
    review.save()
    user.save()
    storage.save()
    upd_review = storage.get(Review, rev_id)
    if old_likes == upd_review.found_useful:
        # likes not updated successfully
        return 500
    else:
        return 200


@app.route('/update_review/<rev_id>', methods=['GET', 'POST'], strict_slashes=False)
# @login_required # to like, need to login
def update_review(rev_id):
    """ update a review object """
    if not current_user.is_authenticated:
        print("Not authenticated")
        flash("Please login to complete action", category="warning")
        return redirect(url_for('login'))
    url = f"http://192.168.100.100:5000/api/v1/reviews/{rev_id}"
    data = request.json
    print(data)

    if 'found_useful' in data:
        # user has liked a review, add review to fav_reviews
        user = storage.get(User, current_user.id)
        review = storage.get(Review, rev_id)
        print("----- Favorite reviews ----")
        print(user.fav_reviews)
        print(f"Likes: {review.found_useful}")
        if rev_id in user.fav_reviews:
            # User unliked, remove review from user's favs
            print("Removing review from liked reviews")
            user.fav_reviews.remove(rev_id)
        else:
            # likes increased
            print("Review added to user's favorites")
            user.fav_reviews.append(rev_id)
        user.save()
        storage.save()

    res = requests.put(url, json=data)
    if res.status_code <= 201:
        print("---- Review updated succesfully ----")
    else:
        print("Error updating review")
        flash("There was an error updating your review", "danger")
    return jsonify({"status_code": res.status_code})

@app.route('/fav_reviews', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def fav_reviews():
    """ show reviews liked by user """
    if request.method == "POST":
        rev_id = request.form.get('id') # get review id from form
        res = update_likes(rev_id)
        if res == 200:
            flash("Review removed successfully", category="success")
        else:
            flash("Action failed", category="danger")
        return redirect(url_for('fav_reviews'))
        # make api call to drop the Review (from jquery)
    else:
        reviews = list()
        print("User's fav reviews")
        print(current_user.fav_reviews)
        for rev in current_user.fav_reviews:
            review = storage.get(Review, rev)
            reviews.append(review)

        return render_template('fav_reviews.html', reviews=reviews,
                               cache_id=uuid.uuid4())

@app.route('/fav_bizes', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def fav_bizes():
    """ show businesses added to collection by user """
    if request.method == "POST":
        biz_id = request.form.get('id')
        user = storage.get(User, current_user.id)
        print("---- FAV BIZES BEFORE DELETE ----")
        print(user.fav_bizes)
        user.fav_bizes.remove(biz_id)
        user.save()
        storage.save()
        print("--- AFTER DELETE ---")
        print(user.fav_bizes)
        return redirect(url_for('fav_bizes'))
        # make api call to drop the Review (from jquery)
    else:
        bizes = list()
        print("User's fav businesses")
        print(current_user.fav_bizes)
        for biz in current_user.fav_bizes:
            business = storage.get(Biz, biz)
            bizes.append(business)

        return render_template('fav_bizes.html', bizes=bizes,
                               cache_id=uuid.uuid4())

@app.route('/edit_bizes', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def edit_bizes():
    """ show businesses listed by logged in user """
    if request.method == "POST":
        return redirect(url_for('edit_bizes'))
        # make api call to drop the business
    else:
        biz_dict = storage.all(Biz)
        bizes = list()
        for biz in biz_dict.values():
            if biz.user_id == current_user.id:
                bizes.append(biz)
        return render_template('edit_bizes.html', bizes=bizes,
                               cache_id=uuid.uuid4())


def are_dicts_identical(dict1, dict2):
    """ check if 2 dicts are identical """
    if len(dict1) != len(dict2):
        return False

    for key, value in dict1.items():
        if key not in dict2 or dict2[key] != value:
            return False

    return True
@app.route('/hrs/<biz_id>', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def edit_hrs(biz_id):
    """ Edit business opening hrs """
    biz = storage.get(Biz, biz_id)
    if request.method == "POST":
        form = request.form
        old_time = biz.operating_hrs
        hrs = {'Monday': {'from': form['mon-from'], 'to': form['mon-to']}, 
               'Tuesday': {'from': form['tue-from'], 'to': form['tue-to']},
               'Wednesday': {'from': form['wed-from'], 'to': form['wed-to']},
               'Thursday': {'from': form['thurs-from'], 'to': form['thurs-to']},
               'Friday': {'from': form['fri-from'], 'to': form['fri-to']},
               'Saturday': {'from': form['sat-from'], 'to': form['sat-to']},
               'Sunday': {'from': form['sun-from'], 'to': form['sun-to']}
               }

        print("--- Time changes ---")
        print(hrs)
        print("--------------------")

        biz.operating_hrs = hrs
        biz.save()
        storage.save()
        print
        if not are_dicts_identical(old_time, hrs):
            # changes were made
            flash("Operating hours updated", category="success")
        return redirect(url_for('edit_hrs', biz_id=biz_id))
    else:
        return render_template('edit_hours.html', biz=biz)

@app.route('/amenities/<biz_id>', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def edit_amen(biz_id):
    """ Edit business opening hrs """
    biz_obj = storage.get(Biz, biz_id)
    if request.method == "POST":
        add_amens = request.form.getlist('available')
        for amen in add_amens:
            biz_obj.amenity_ids.append(amen) # add to list of amenities

        to_remove = request.form.getlist('biz-amens')
        for amenity in to_remove:
            biz_obj.amenity_ids.remove(amenity) # remove from list of amens
        biz_obj.save()
        storage.save()
        return redirect(url_for('edit_amen', biz_id=biz_id))
    else:
        amens = storage.all(Amenity).values()
        # Create a list of amenity IDs associated with the business
        biz_amenity_ids = biz_obj.amenity_ids
        biz_amenities = list()
        for amen_id in biz_amenity_ids:
            amen = storage.get(Amenity, amen_id)
            biz_amenities.append(amen)
        print(biz_amenities)
        
        # Filter out amenities that are already associated with the business
        available_amenities = [amenity for amenity in amens if amenity.id not in biz_amenity_ids]
        return render_template('edit_amen.html',
                               biz=biz_obj,
                               amenities=available_amenities, 
                               biz_amenities=biz_amenities)

@app.route('/desc/<biz_id>', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def edit_desc(biz_id):
    """ Edit business description """
    if request.method == "POST":
        text = request.form['description']
        biz = storage.get(Biz, biz_id)
        biz.description = text
        biz.save()
        storage.save()
        flash("Description updated!", category="success")
        return redirect(url_for('edit_desc', biz_id=biz_id))
    else:
        biz_obj = storage.get(Biz, biz_id)
        return render_template('edit_desc.html', biz=biz_obj)


if __name__ == "__main__":
    """ Main Function """
    app.run(host='0.0.0.0', port=5500, debug=True)
