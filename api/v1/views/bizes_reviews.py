#!/usr/bin/python3
""" objects that handle all default RestFul API actions for Reviews """
from models.review import Review
from models.biz import Biz
from models.user import User
from models import storage
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request


@app_views.route('/bizes/<biz_id>/reviews', methods=['GET'],
                 strict_slashes=False)
def get_reviews(biz_id):
    """
    Retrieves the list of all Review objects of a business
    """
    biz = storage.get(Biz, biz_id)

    if not biz:
        abort(404)

    reviews = [review.to_dict() for review in biz.reviews]

    return jsonify(reviews)


@app_views.route('/reviews/<review_id>', methods=['GET'], strict_slashes=False)
def get_review(review_id):
    """
    Retrieves a Review object
    """
    review = storage.get(Review, review_id)
    if not review:
        abort(404)

    return jsonify(review.to_dict())


@app_views.route('/reviews/<review_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_review(review_id):
    """
    Deletes a Review Object
    """

    review = storage.get(Review, review_id)

    if not review:
        abort(404)

    storage.delete(review)
    storage.save()

    return make_response(jsonify({}), 200)


@app_views.route('/bizes/<biz_id>/reviews', methods=['POST'],
                 strict_slashes=False)
def post_review(biz_id):
    """
    Creates a Review
    """
    biz = storage.get(Biz, biz_id)

    if not biz:
        print("Invalid biz_id (does not exist)")
        abort(404)

    if not request.get_json():
        abort(400, description="Not a JSON")

    if 'user_id' not in request.get_json():
        abort(400, description="Missing user_id")

    data = request.get_json()
    user = storage.get(User, data['user_id'])

    if not user:
        print("No such user")
        abort(404)

    if 'text' not in request.get_json():
        abort(400, description="Missing text")

    data['biz_id'] = biz_id
    instance = Review(**data)
    instance.save()
    storage.save()
    print(user.reviews) # check if review was added to user reviews list
    return make_response(jsonify(instance.to_dict()), 201)


@app_views.route('/reviews/<review_id>', methods=['PUT'], strict_slashes=False)
def put_review(review_id):
    """
    Updates a Review
    """
    review = storage.get(Review, review_id)

    if not review:
        abort(404)

    if not request.get_json():
        abort(400, description="Not a JSON")

    ignore = ['id', 'user_id', 'biz_id', 'created_at', 'updated_at']

    data = request.get_json()
    for key, value in data.items():
        if key not in ignore:
            setattr(review, key, value)
    storage.save()
    return make_response(jsonify(review.to_dict()), 200)
