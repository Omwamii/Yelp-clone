#!/usr/bin/python3
""" objects that handle all default RestFul API actions for Places """
from models.county import County
from models.city import City
from models.biz import Biz
from models.user import User
from models.amenity import Amenity
from models import storage
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request


@app_views.route('/cities/<city_id>/bizes', methods=['GET'],
                 strict_slashes=False)
def get_bizes(city_id):
    """
    Retrieves the list of all Biz objects of a City
    """
    city = storage.get(City, city_id)

    if not city:
        abort(404)

    bizes = [biz.to_dict() for biz in city.bizes]

    return jsonify(bizes)


@app_views.route('/bizes/<biz_id>', methods=['GET'], strict_slashes=False)
def get_biz(biz_id):
    """
    Retrieves a Biz object
    """
    biz = storage.get(Biz, biz_id)
    if not biz:
        abort(404)

    return jsonify(biz.to_dict())


@app_views.route('/bizes/<biz_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_biz(biz_id):
    """
    Deletes a Biz Object
    """

    biz = storage.get(Biz, biz_id)

    if not biz:
        abort(404)

    storage.delete(biz)
    storage.save()

    return make_response(jsonify({}), 200)


@app_views.route('/cities/<city_id>/bizes', methods=['POST'],
                 strict_slashes=False)
def post_biz(city_id):
    """
    Creates a Biz
    """
    city = storage.get(City, city_id)

    if not city:
        abort(404)

    if not request.get_json():
        abort(400, description="Not a JSON")

    if 'user_id' not in request.get_json():
        abort(400, description="Missing user_id")

    data = request.get_json()
    user = storage.get(User, data['user_id'])

    if not user:
        abort(404)

    if 'name' not in request.get_json():
        abort(400, description="Missing name")

    data["city_id"] = city_id
    instance = Biz(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@app_views.route('/bizes/<biz_id>', methods=['PUT'], strict_slashes=False)
# @swag_from('documentation/place/put_place.yml', methods=['PUT'])
def put_biz(biz_id):
    """
    Updates a Biz
    """
    biz = storage.get(Biz, biz_id)

    if not biz:
        abort(404)

    data = request.get_json()
    if not data:
        abort(400, description="Not a JSON")

    ignore = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']

    for key, value in data.items():
        if key not in ignore:
            setattr(biz, key, value)
    storage.save()
    return make_response(jsonify(biz.to_dict()), 200)


# edit !!!
@app_views.route('/bizes_search', methods=['POST'], strict_slashes=False)
def bizes_search():
    """
    Retrieves all Biz objects depending of the JSON in the body
    of the request
    """

    if request.get_json() is None:
        abort(400, description="Not a JSON")

    data = request.get_json()

    if data and len(data):
        counties = data.get('counties', None)
        cities = data.get('cities', None)
        amenities = data.get('amenities', None)

    if not data or not len(data) or (
            not states and
            not cities and
            not amenities):
        places = storage.all(Place).values()
        list_places = []
        for place in places:
            list_places.append(place.to_dict())
        return jsonify(list_places)

    list_places = []
    if states:
        states_obj = [storage.get(State, s_id) for s_id in states]
        for state in states_obj:
            if state:
                for city in state.cities:
                    if city:
                        for place in city.places:
                            list_places.append(place)

    if cities:
        city_obj = [storage.get(City, c_id) for c_id in cities]
        for city in city_obj:
            if city:
                for place in city.places:
                    if place not in list_places:
                        list_places.append(place)

    if amenities:
        if not list_places:
            list_places = storage.all(Place).values()
        amenities_obj = [storage.get(Amenity, a_id) for a_id in amenities]
        list_places = [place for place in list_places
                       if all([am in place.amenities
                               for am in amenities_obj])]

    places = []
    for p in list_places:
        d = p.to_dict()
        d.pop('amenities', None)
        places.append(d)

    return jsonify(places)
