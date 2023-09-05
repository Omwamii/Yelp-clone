#!/usr/bin/python3
""" objects that handle all default RestFul API actions for Place - Amenity """
from models.biz import Biz
from models.amenity import Amenity
from models import storage
from api.v1.views import app_views
from os import environ
from flask import abort, jsonify, make_response, request


@app_views.route('bizes/<biz_id>/amenities', methods=['GET'],
                 strict_slashes=False)
def get_biz_amenities(biz_id):
    """
    Retrieves the list of all Amenity objects of a business
    """
    biz = storage.get(Biz, biz_id)

    if not biz:
        abort(404)

    if environ.get('HBNB_TYPE_STORAGE') == "db":
        amenities = [amenity.to_dict() for amenity in biz.amenities]
    else:
        amenities = [storage.get(Amenity, amenity_id).to_dict()
                     for amenity_id in biz.amenity_ids]

    return jsonify(amenities)


@app_views.route('/bizes/<biz_id>/amenities/<amenity_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_biz_amenity(biz_id, amenity_id):
    """
    Deletes a Amenity object of a Place
    """
    biz = storage.get(Biz, biz_id)

    if not biz:
        abort(404)

    amenity = storage.get(Amenity, amenity_id)

    if not amenity:
        abort(404)

    if environ.get('HBNB_TYPE_STORAGE') == "db":
        if amenity not in biz.amenities:
            abort(404)
        biz.amenities.remove(amenity)
    else:
        if amenity_id not in biz.amenity_ids:
            abort(404)
        biz.amenity_ids.remove(amenity_id)

    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route('/bizes/<biz_id>/amenities/<amenity_id>', methods=['POST'],
                 strict_slashes=False)
def post_biz_amenity(biz_id, amenity_id):
    """
    Link a Amenity object to biz
    """
    biz = storage.get(Biz, biz_id)

    if not biz:
        abort(404)

    amenity = storage.get(Amenity, amenity_id)

    if not amenity:
        abort(404)

    if environ.get('HBNB_TYPE_STORAGE') == "db":
        if amenity in biz.amenities:
            return make_response(jsonify(amenity.to_dict()), 200)
        else:
            biz.amenities.append(amenity)
    else:
        if amenity_id in biz.amenity_ids:
            return make_response(jsonify(amenity.to_dict()), 200)
        else:
            biz.amenity_ids.append(amenity_id)

    storage.save()
    return make_response(jsonify(amenity.to_dict()), 201)
