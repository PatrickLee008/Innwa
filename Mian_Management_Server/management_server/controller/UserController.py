import time
from sqlalchemy import or_, func
from management_server import app, db, auth, user_opt
from management_server.model.AppUserModel import AppUser
from flask import g, request, jsonify, Blueprint
from management_server.utils import OrmUttil
from datetime import datetime

user = Blueprint('user', __name__)


@user.route('/list', methods=['GET'])
@auth.login_required
def get_user_list():
    """
                @@@
                #### Args:
                        current_page = request.args.get('page', type=int, default=1)
                        limit = request.args.get('limit', type=int, default=20)
                        key_word = request.args.get('key_word')
                #### Returns::
                        {
                            'code': 20000,
                            'items': [u.to_dict() for u in user_list],
                            'total': total
                        }
            """

    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)
    key_word = request.args.get('key_word')

    user_list = AppUser.query
    if key_word:
        user_list = user_list.filter(
            or_(AppUser.USER_ID.like('%{}%'.format(key_word)), AppUser.NICK_NAME.like('%{}%'.format(key_word)),
                AppUser.PHONE.like('%{}%'.format(key_word))))

    total = user_list.count()

    user_list = user_list.offset((current_page - 1) * limit).limit(limit).all()

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in user_list],
        'total': total
    })


@user.route('/delete', methods=['POST'])
@auth.login_required
def delete_user():
    """
                   @@@
                   #### Args:
                           user_id = request.args.get('user_id')
                   #### Returns::
                           {
                               'code': 20000,
                               'msg': delete finished!
                           }
    """
    user_id = request.args.get('user_id')
    AppUser.query.filter_by(USER_ID=user_id).delete()
    db.session.commit()
    user_opt.send({
        "operate": "删除用户",
        "route": "用户管理",
        "key_word": user_id,
        "user": g.user.ACCOUNT
    })
    return jsonify({
        'code': 20000,
        'msg': 'delete finished!'
    })
