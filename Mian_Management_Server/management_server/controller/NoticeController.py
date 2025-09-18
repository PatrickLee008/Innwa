from management_server import app, db, auth, user_opt
from flask import jsonify, Blueprint, request, g
from management_server.model.NoticeModel import Notice
from sqlalchemy import or_, func
from management_server.utils import OrmUttil
from datetime import datetime
import time

r_notice = Blueprint('notice', __name__)


@r_notice.route('/get', methods=['GET'])
@auth.login_required
def get_notices():
    """
                    @@@
                    #### Args:
                           {
                                current_page: "",
                                limit: "",
                                key_word: "",
                                start_time: "",
                                end_time: "",
                            }
                    #### Returns::
                            {
                                'code': 20000,
                                'items': [u.to_dict() for u in notice_list],
                            }
                """
    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)
    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    notice_list = Notice.query
    if key_word:
        notice_list = notice_list.filter(or_(Notice.MNOTICE_ID.like('%{}%'.format(key_word)), Notice.TITLE.like('%{}%'.format(key_word)), Notice.CONTENT.like('%{}%'.format(key_word))))

    if start_time:
        notice_list = notice_list.filter(Notice.CREATE_TIME >= start_time)

    if end_time:
        end_time += ' 23:59:59'
        notice_list = notice_list.filter(Notice.CREATE_TIME <= end_time)

    notice_list = notice_list.offset((current_page - 1) * limit).limit(limit).all()

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in notice_list],
    })


@r_notice.route('/edit', methods=['POST'])
@auth.login_required
def edit_notice():
    """
    @@@
    #### Args:
            {
               "MNOTICE_ID": '1553335644871',
               "TITLE": "",
               "CONTENT": "",
            }
    #### Returns::
            {'code': 20000, 'message': "修改成功"}
            {'code': 50001, 'message': "未知错误"}
    """
    args = request.get_json()
    edit_id = args.get('MNOTICE_ID')
    try:
        notice = Notice.query.filter_by(MNOTICE_ID=edit_id).one_or_none()
        OrmUttil.set_field(notice, args)
        notice.UPDATOR = g.user.NAME
        db.session.commit()
        user_opt.send({
            "operate": "修改公告",
            "route": "公告管理",
            "key_word": edit_id,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "修改成功"})
    except Exception as e:
        print(e)
        return jsonify({
            'code': 50001,
            'message': "未知错误"
        })


@r_notice.route('/add', methods=['POST'])
@auth.login_required
def add_notice():
    """
    @@@
    #### Args:
            {
               "TITLE": "",
               "CONTENT": "",
            }
    #### Returns::
            {'code': 20000, 'message': "添加成功"}
            {'code': 50001, 'message': "未知错误"}
    """

    args = request.get_json()

    try:
        notice_id = int(round(time.time() * 1000))
        notice = Notice(MNOTICE_ID=notice_id)
        OrmUttil.set_field(notice, args)
        notice.CREATOR = g.user.NAME
        db.session.add(notice)
        db.session.commit()
        user_opt.send({
            "operate": "添加公告",
            "route": "公告管理",
            "key_word": notice_id,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "添加成功"})
    except Exception as e:
        print("add match error:", e)

    return jsonify({'code': 50001, 'message': "未知错误"})


@r_notice.route('/remove', methods=['POST'])
@auth.login_required
def remove_notice():
    """
        @@@
        #### Args:
                {
                   "MNOTICE_ID": '1553335644871',
                }
        #### Returns::
                {'code': 20000, 'message': "删除成功"}
                {'code': 50001, 'message': "未知错误"}
        """
    args = request.get_json()
    remove_id = args.get('MNOTICE_ID')
    try:
        Notice.query.filter_by(MNOTICE_ID=remove_id).delete()
        db.session.commit()
        user_opt.send({
            "operate": "删除公告",
            "route": "公告管理",
            "key_word": remove_id,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "删除成功"})
    except Exception as e:
        print(e)
        return jsonify({
            'code': 50001,
            'message': "未知错误"
        })
