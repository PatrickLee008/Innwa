from sqlalchemy import or_
from management_server import auth
from management_server.model.LoginRecordModel import LoginRecord
from flask import g, request, jsonify, Blueprint
from datetime import datetime

login_record = Blueprint('login_records', __name__)


@login_record.route('/get', methods=['GET'])
@auth.login_required
def get_login_records():
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

    record_list = LoginRecord.query.order_by(LoginRecord.LOGIN_TIME.desc())
    if key_word:
        record_list = record_list.filter(
            or_(LoginRecord.USER_ACCOUNT.like('%{}%'.format(key_word)), LoginRecord.IP.like('%{}%'.format(key_word))))

    if start_time:
        record_list = record_list.filter(LoginRecord.LOGIN_TIME >= start_time)

    if end_time:
        end_time += ' 23:59:59'
        record_list = record_list.filter(LoginRecord.LOGIN_TIME <= end_time)

    total = record_list.count()

    record_list = record_list.offset((current_page - 1) * limit).limit(limit).all()

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in record_list],
        'total': total
    })
