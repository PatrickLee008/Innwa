from management_server import db, auth, user_opt
from management_server.model.WithDrawGroupModel import WithDrawGroup
from sqlalchemy import func
from flask import g, request, jsonify, Blueprint
from management_server.utils import OrmUttil

withdraw_group = Blueprint('withdraw_group', __name__)


# 获取订单列表
@withdraw_group.route('/get', methods=['GET'])
@auth.login_required
def get_group_list():
    """
                @@@
                #### Args:
                        current_page = request.args.get('page', type=int, default=1)
                        limit = request.args.get('limit', type=int, default=20)
                #### Returns::
                        {
                            'code': 20000,
                            'items': [u.to_dict() for u in order_list],
                            'total': total,
                            'total_amount': total_amount
                        }
            """

    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)

    withdraw_group_list = WithDrawGroup.query.offset((current_page - 1) * limit).limit(limit).all()

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in withdraw_group_list],
        'total': len(withdraw_group_list),
    })


@withdraw_group.route('/remove', methods=['POST'])
@auth.login_required
def remove_group():
    """
        @@@
        #### Args:
                {
                   "ID": 1,
                }
        #### Returns::
                {'code': 20000, 'message': "删除成功"}
                {'code': 50001, 'message': "未知错误"}
        """
    remove_id = request.get_json().get('ID')
    print("remove_withdraw_group args", remove_id)
    try:
        the_withdraw_group = WithDrawGroup.query.filter_by(ID=remove_id).one_or_none()
        if not the_withdraw_group:
            return jsonify({'code': 50002, 'message': "WithDrawGroup not exist."})
        withdraw_count = WithDrawGroup.query.with_entities(func.count(WithDrawGroup.ID)).scalar()
        if withdraw_count < 2:
            return jsonify({'code': 50002, 'message': "cannot delete the last withdraw group."})
        db.session.delete(the_withdraw_group)
        db.session.commit()

        user_opt.send({
            "operate": "删除提现组",
            "route": "提现组管理",
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


@withdraw_group.route('/edit', methods=['POST'])
@auth.login_required
def edit_group():
    """
    @@@
    #### Args:
            GROUP_NAME = Column(String(255), server_default="", nullable=False, comment="组名称")
            REMARK = Column(String(255), nullable=False, server_default="", comment="备注")
    #### Returns::
            {'code': 20000, 'message': "添加成功"}
            {'code': 50001, 'message': "未知错误"}
    """
    args = request.get_json()
    edit_id = args.get('ID')

    try:
        group = WithDrawGroup.query.filter_by(ID=edit_id).one_or_none()
        if not group:
            return {'code': 50003, 'message': "WithDrawGroup not exist."}
        OrmUttil.set_field(group, args)

        user_opt.send({
            "operate": "修改提现组",
            "route": "提现组管理",
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


@withdraw_group.route('/add', methods=['POST'])
@auth.login_required
def add_group():
    """
    @@@
    #### Args:
            GROUP_NAME = Column(String(255), server_default="", nullable=False, comment="组名称")
            REMARK = Column(String(255), nullable=False, server_default="", comment="备注")
    #### Returns::
            {'code': 20000, 'message': "添加成功"}
            {'code': 50001, 'message': "未知错误"}
    """

    args = request.get_json()
    name = args.get('GROUP_NAME')
    print("args.....", args)

    try:
        group = WithDrawGroup.query.filter_by(GROUP_NAME=name).one_or_none()
        if group:
            return jsonify({
                'code': 50001,
                'message': 'group name repeated!'
            })
        group = WithDrawGroup()

        db.session.add(group)
        OrmUttil.set_field(group, args)
        db.session.commit()

        user_opt.send({
            "operate": "添加提现组",
            "route": "提现组管理",
            "key_word": group.ID,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "添加成功"})
    except Exception as e:
        print("add match error:", e)

    return jsonify({'code': 50001, 'message': "未知错误"})
