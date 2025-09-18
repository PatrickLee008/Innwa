from sqlalchemy import or_, func
from management_server import app, db, auth, user_opt
from management_server.model.OperationModel import Operation
from flask import g, request, jsonify, Blueprint
from datetime import datetime

operation = Blueprint('operation', __name__)


@operation.route('/get', methods=['GET'])
@auth.login_required
def get_operations():
    """
                @@@
                #### Args:
                        current_page = request.args.get('page', type=int, default=1)
                        limit = request.args.get('limit', type=int, default=20)

                        key_word = request.args.get('key_word')
                        start_time = request.args.get('start_time')
                        end_time = request.args.get('end_time')
                #### Returns::
                        {
                            'code': 20000,
                            'items': [u.to_dict() for u in opt_list],
                        }
            """

    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)
    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    opt_list = Operation.query.order_by(Operation.CREATE_TIME.desc())
    if key_word:
        opt_list = opt_list.filter(
            or_(Operation.USER_ACCOUNT.like('%{}%'.format(key_word)), Operation.TARGET.like('%{}%'.format(key_word)), Operation.OPERATION.like('%{}%'.format(key_word))))

    if start_time:
        opt_list = Operation.filter(Operation.CREATE_TIME >= start_time)

    if end_time:
        end_time += ' 23:59:59'
        opt_list = Operation.filter(Operation.CREATE_TIME <= end_time)

    total = opt_list.count()

    opt_list = opt_list.offset((current_page - 1) * limit).limit(limit).all()

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in opt_list],
        'total': total
    })
