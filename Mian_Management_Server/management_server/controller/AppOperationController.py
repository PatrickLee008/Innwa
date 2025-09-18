from sqlalchemy import or_, func
from management_server import app, db, auth, user_opt
from management_server.model.AppOperationModel import AppOperation
from flask import g, request, jsonify, Blueprint
from datetime import datetime

app_operation = Blueprint('app_operation', __name__)


@app_operation.route('/get', methods=['GET'])
@auth.login_required
def get_app_operations():
    """
                @@@
                #### Args:
                        current_page = request.args.get('page', type=int, default=1)
                        limit = request.args.get('limit', type=int, default=20)

                        key_word = request.args.get('key_word') ex:USER_ACCOUNT\ SOURCE_ID\ DESC
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
    opt_type = request.args.get('type')

    #opt_list = AppOperation.query.order_by(AppOperation.CREATE_TIME.desc(), AppOperation.ID.desc())
    opt_list = AppOperation.query.order_by(AppOperation.ID.desc())
    if opt_type:
        opt_list = opt_list.filter(AppOperation.TYPE == opt_type)

    if key_word:
        opt_list = opt_list.filter(
            or_(AppOperation.USER_ACCOUNT.like('%{}%'.format(key_word)), AppOperation.SOURCE_ID.like('%{}%'.format(key_word)), AppOperation.DESC.like('%{}%'.format(key_word))))

    if start_time:
        opt_list = opt_list.filter(AppOperation.CREATE_TIME >= start_time)

    if end_time:
        end_time += ' 23:59:59'
        opt_list = opt_list.filter(AppOperation.CREATE_TIME <= end_time)

    total = opt_list.count()

    opt_list = opt_list.offset((current_page - 1) * limit).limit(limit).all()

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in opt_list],
        'total': total
    })
