from flask import jsonify, Blueprint
from management_server import auth, user_opt
from management_server.model.RouteModel import Route

menu = Blueprint('menu', __name__)


@menu.route('/get', methods=['GET'])
@auth.login_required
def get_routes():
    route_list = Route.query.filter_by(parent_id=0)

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in route_list],
    })


@menu.route('/get_list', methods=['GET'])
@auth.login_required
def get_routes_list():
    route_list = Route.query.filter_by(parent_id=0)

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in route_list],
    })
