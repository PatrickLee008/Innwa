from management_server import app, db, auth, user_opt
from flask import jsonify, Blueprint, request, g
from management_server.model.BankTypeModel import BankType
from sqlalchemy import or_, func
from management_server.utils import OrmUttil
from datetime import datetime
import time

r_bank_type = Blueprint('bank_type', __name__)


@r_bank_type.route('/get', methods=['GET'])
@auth.login_required
def get_bank_types():
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
                                'items': [u.to_dict() for u in bank_type_list],
                            }
                """
    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)

    bank_type_list = BankType.query

    bank_type_list = bank_type_list.offset((current_page - 1) * limit).limit(limit).all()

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in bank_type_list],
    })


@r_bank_type.route('/edit', methods=['POST'])
@auth.login_required
def edit_bank_type():
    """
    @@@
    #### Args:
            {
               "ID": '3',
               "NAME": ""
            }
    #### Returns::
            {'code': 20000, 'message': "修改成功"}
            {'code': 50001, 'message': "未知错误"}
    """
    args = request.get_json()
    edit_id = args.get('ID')
    try:
        bank_type = BankType.query.filter_by(ID=edit_id).one_or_none()
        OrmUttil.set_field(bank_type, args)
        bank_type.UPDATOR = g.user.NAME
        db.session.commit()
        user_opt.send({
            "operate": "修改银行类型",
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


@r_bank_type.route('/add', methods=['POST'])
@auth.login_required
def add_bank_type():
    """
    @@@
    #### Args:
            {
               "NAME": ""
            }
    #### Returns::
            {'code': 20000, 'message': "添加成功"}
            {'code': 50001, 'message': "未知错误"}
    """

    args = request.get_json()

    try:
        bank_type = BankType()
        OrmUttil.set_field(bank_type, args)
        db.session.add(bank_type)
        db.session.commit()
        user_opt.send({
            "operate": "添加银行类型",
            "route": "配置管理",
            "key_word": bank_type.ID,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "添加成功"})
    except Exception as e:
        print("add match error:", e)

    return jsonify({'code': 50001, 'message': "未知错误"})


@r_bank_type.route('/remove', methods=['POST'])
@auth.login_required
def remove_bank_type():
    """
        @@@
        #### Args:
                {
                   "ID": '3',
                }
        #### Returns::
                {'code': 20000, 'message': "删除成功"}
                {'code': 50001, 'message': "未知错误"}
        """
    args = request.get_json()
    remove_id = args.get('ID')
    try:
        BankType.query.filter_by(ID=remove_id).delete()
        db.session.commit()
        user_opt.send({
            "operate": "删除银行类型",
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
