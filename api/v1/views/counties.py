#!/usr/bin/python3
""" objects that handle all default RestFul API actions for States """
from models.county import County
from models import storage
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request


@app_views.route('/counties', methods=['GET'], strict_slashes=False)
def get_counties():
    """
    Retrieves the list of all County objects
    """
    all_counties = storage.all(County).values()
    list_counties = []
    for county in all_counties:
        list_counties.append(county.to_dict())
    return jsonify(list_counties)


@app_views.route('/counties/<county_id>', methods=['GET'], strict_slashes=False)
def get_county(county_id):
    """ Retrieves a specific County eg. Uasin Gishu.. """
    county = storage.get(County, county_id)
    if not county:
        abort(404)

    return jsonify(county.to_dict())


@app_views.route('/counties/<county_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_county(county_id):
    """
    Deletes a County Object
    """
    county = storage.get(County, county_id)

    if not county:
        abort(404)

    storage.delete(county)
    storage.save()

    return make_response(jsonify({}), 200)


@app_views.route('/counties', methods=['POST'], strict_slashes=False)
def post_county():
    """
    Creates a County
    """
    if not request.get_json():
        abort(400, description="Not a JSON")

    if 'name' not in request.get_json():
        abort(400, description="Missing name")

    data = request.get_json()
    instance = County(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@app_views.route('/counties/<county_id>', methods=['PUT'], strict_slashes=False)
def put_county(county_id):
    """
    Updates a County
    """
    county = storage.get(County, county_id)

    if not county:
        abort(404)

    if not request.get_json():
        abort(400, description="Not a JSON")

    ignore = ['id', 'created_at', 'updated_at']

    data = request.get_json()
    for key, value in data.items():
        if key not in ignore:
            setattr(county, key, value)
    storage.save()
    return make_response(jsonify(county.to_dict()), 200)
