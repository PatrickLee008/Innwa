from management_server import app, db, auth, user_opt
from flask import jsonify, Blueprint, request, g
from management_server.model.ContactFuncModel import ContactFunc
from sqlalchemy import or_, func
from management_server.utils import OrmUttil
from datetime import datetime
import time

r_contact_fun = Blueprint('contact_fun', __name__)


@r_contact_fun.route('/get', methods=['GET'])
@auth.login_required
def get_contact_funs():
    """
                    @@@
                    #### Args:
                           {
                                current_page: "",
                                limit: "",
                            }
                    #### Returns::
                            {
                                'code': 20000,
                                'items': [u.to_dict() for u in contact_fun_list],
                            }
                """
    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)

    contact_fun_list = ContactFunc.query

    contact_fun_list = contact_fun_list.offset((current_page - 1) * limit).limit(limit).all()

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in contact_fun_list],
    })


@r_contact_fun.route('/edit', methods=['POST'])
@auth.login_required
def edit_contact_fun():
    """
    @@@
    #### Args:
            {
               "ID": '3',
               "TYPE": "",
               "CONTENT": "",
            }
    #### Returns::
            {'code': 20000, 'message': "修改成功"}
            {'code': 50001, 'message': "未知错误"}
    """
    args = request.get_json()
    edit_id = args.get('ID')
    try:
        contact_fun = ContactFunc.query.filter_by(ID=edit_id).one_or_none()
        OrmUttil.set_field(contact_fun, args)
        db.session.commit()
        user_opt.send({
            "operate": "修改联系方式",
            "route": "配置管理",
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


@r_contact_fun.route('/add', methods=['POST'])
@auth.login_required
def add_contact_fun():
    """
    @@@
    #### Args:
            {
               "TYPE": "",
               "CONTENT": "",
            }
    #### Returns::
            {'code': 20000, 'message': "添加成功"}
            {'code': 50001, 'message': "未知错误"}
    """

    args = request.get_json()

    try:
        contact_fun = ContactFunc()
        OrmUttil.set_field(contact_fun, args)
        db.session.add(contact_fun)
        db.session.commit()
        user_opt.send({
            "operate": "添加联系方式",
            "route": "配置管理",
            "key_word": contact_fun.ID,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "添加成功"})
    except Exception as e:
        print("add match error:", e)

    return jsonify({'code': 50001, 'message': "未知错误"})


@r_contact_fun.route('/remove', methods=['POST'])
@auth.login_required
def remove_contact_fun():
    """
        @@@
        #### Args:
                {
                   "ID": '1553335644871',
                }
        #### Returns::
                {'code': 20000, 'message': "删除成功"}
                {'code': 50001, 'message': "未知错误"}
        """
    args = request.get_json()
    remove_id = args.get('ID')
    try:
        ContactFunc.query.filter_by(ID=remove_id).delete()
        db.session.commit()
        user_opt.send({
            "operate": "删除联系方式",
            "route": "配置管理",
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
