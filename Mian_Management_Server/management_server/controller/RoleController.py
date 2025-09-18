from management_server import app, db, auth, user_opt
from flask import jsonify, Blueprint, request, g
from management_server.utils.OrmUttil import PERMISSION
from management_server.model.RoleModel import Role
from management_server.model.RoleRoute import RoleRoute
from management_server.utils import OrmUttil

r_role = Blueprint('role', __name__)


@r_role.route('/get', methods=['GET'])
@auth.login_required
def get_role_list():
    """
    @@@
    #### Returns::
            {'code': 20000, 'items': [{'role_id':xxx,'role_name':xxx,'description':xxx}]}
    """
    roles_list = Role.query.all()
    roles = []

    for role in roles_list:
        # 获取该角色所有的路由列表
        role_routes = [role_route.to_dict() for role_route in role.ROLE_ROUTES.all()]

        temp = {
            "role_id": role.ID,
            "role_name": role.NAME,
            "description": role.DESCRIPTION,
            "routes": role_routes
        }
        roles.append(temp)

    return jsonify({
        'code': 20000,
        'items': roles
    })


@r_role.route('/edit', methods=['POST'])
@auth.login_required
def edit_role():
    """
    @@@
    #### Args:
            {
               "role_id": 1,
               "NAME": "",
               "DESCRIPTION": "",
               "routes": {
                   1:[True, True, False, False],
                   ...
               ]
            }
    #### Returns::
            {'code': 20000, 'message': "添加成功"}
            {'code': 50001, 'message': "未知错误"}
    """
    args = request.get_json()
    edit_id = args.get('role_id')
    role_routes = args.get('routes')
    try:
        role = Role.query.filter_by(ID=edit_id).one_or_none()
        # 删除关联routes
        role.ROLE_ROUTES.delete()

        for key, value in role_routes.items():
            permission = PERMISSION.li_to_per(value)
            route_route = RoleRoute(ROLE_ID=edit_id, ROUTE_ID=key, PERMISSION=permission)
            db.session.add(route_route)
        db.session.commit()

        user_opt.send({
            "operate": "修改角色",
            "route": "角色管理",
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


@r_role.route('/add', methods=['POST'])
@auth.login_required
def add_role():
    """
    @@@
    #### Args:
            {
               "NAME": "",
               "DESCRIPTION": "",
               "routes": {
                   1:[0,1,0,1],
                   ...
               }
            }
    #### Returns::
            {'code': 20000, 'message': "添加成功"}
            {'code': 50001, 'message': "未知错误"}
    """

    args = request.get_json()
    name = args.get('NAME')
    description = args.get('DESCRIPTION')
    role_routes = args.get('routes')

    try:
        role = Role.query.filter_by(NAME=name).one_or_none()
        if role:
            return jsonify({
                'code': 50001,
                'message': 'role name repeated!'
            })
        role = Role(NAME=name)

        db.session.add(role)
        args.pop('routes')
        OrmUttil.set_field(role, args)
        db.session.commit()

        for key, value in role_routes.items():
            permission = PERMISSION.li_to_per(value)
            route_route = RoleRoute(ROLE_ID=role.ID, ROUTE_ID=key, PERMISSION=permission)
            db.session.add(route_route)

        db.session.commit()
        user_opt.send({
            "operate": "添加角色",
            "route": "角色管理",
            "key_word": role.ID,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "添加成功"})
    except Exception as e:
        print("add match error:", e)

    return jsonify({'code': 50001, 'message': "未知错误"})


@r_role.route('/remove', methods=['POST'])
@auth.login_required
def remove_role():
    """
        @@@
        #### Args:
                {
                   "role_id": 1,
                }
        #### Returns::
                {'code': 20000, 'message': "删除成功"}
                {'code': 50001, 'message': "未知错误"}
        """
    args = request.get_json()
    remove_id = args.get('role_id')
    print("args:", args)
    try:
        role = Role.query.filter_by(ID=remove_id).one_or_none()
        if not role:
            return {
                'code': 50002,
                'message': "Role not exist."
            }
        # 删除关联routes
        role.ROLE_ROUTES.delete()
        db.session.delete(role)
        db.session.commit()
        user_opt.send({
            "operate": "删除角色",
            "route": "角色管理",
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
