import os

import pyotp
import qrcode

from management_server import app, auth, db, user_opt
from management_server.model.SysUserModel import SysUser
from management_server.model.LoginRecordModel import LoginRecord
from management_server.model.RouteModel import Route
from management_server.model.RoleModel import Role
from management_server.model.DeviceModel import Device
from management_server.utils.OrmUttil import PERMISSION
from sqlalchemy import and_
from flask import g, request, jsonify, make_response, Blueprint, current_app
from management_server.utils import OrmUttil
import datetime
import time

admin = Blueprint('admin', __name__)


@auth.verify_token
def verify_token(token):
    if not token:
        return False

    user = SysUser.verify_auth_token(token)
    if not user:
        return False
    g.user = user
    return True


@auth.error_handler
def unauthorized():
    return jsonify({
        'code': 401,
        'message': "Unauthorized access"
    })

@admin.route('/setup_2fa', methods=['GET'])
@auth.login_required
def setup_2fa():
    if g.user.GOOGLE_SECRET:
        return jsonify({
            'code': 20000,
            "item": g.user.to_dict()
        })
    # 为用户生成唯一的 Secret Key
    secret = pyotp.random_base32()

    g.user.GOOGLE_SECRET = secret

    # 创建绑定到 Google Authenticator 的二维码
    totp = pyotp.TOTP(secret)
    otp_url = totp.provisioning_uri(name=g.user.ACCOUNT)
    print(f"OTP URL: {otp_url}")

    # 使用 qrcode 生成二维码
    qr = qrcode.make(otp_url)

    # 获取当前项目的 static 文件夹路径
    static_folder = os.path.join(current_app.root_path, 'static', 'google_code')

    # 确保 static 文件夹存在
    if not os.path.exists(static_folder):
        os.makedirs(static_folder)

    # 为每个用户生成唯一的二维码文件名，避免文件名冲突
    qr_filename = f"{g.user.ACCOUNT}_qrcode.png"
    qr_path = os.path.join(static_folder, qr_filename)

    # 保存二维码图片到 static 文件夹
    qr.save(qr_path)
    db.session.commit()

    return jsonify({
        'code': 20000,
        'message': "操作成功",
        "item":g.user.to_dict()
    })


@admin.route('/login', methods=['POST'])
def login():
    args = request.get_json()
    account = args.get('username')
    psw = args.get('password')
    otp = args.get("otp")
    ip = request.remote_addr
    try:
        user = SysUser.query.filter(SysUser.ACCOUNT == account).first()

        if user is None or not user.check_psw(psw):
            return jsonify({
                'code': 50001,
                'message': "用户名或密码错误"
            })
        mac = ""
        if user.need_mac_check():
            mac = args.get("mac")
            if not mac:
                return {
                    'code': 50002,
                    'message': "Cannot find mac address, Please make sure the Integrated.exe is running."
                }
            mac = mac.replace(" ", "")

            device = Device.query.filter_by(MacAddress=mac).one_or_none()
            if not device or not device.Enable:
                return {
                    'code': 50003,
                    'message': "Mac Permission error"
                }
            # 设备登录日志
            device.LastLoginTime = datetime.datetime.now()

        user.LAST_LOGIN = datetime.datetime.now()

        # if user.GOOGLE_SECRET:
        #     totp = pyotp.TOTP(user.GOOGLE_SECRET)
        #
        #     print(f"Generated OTP: {totp.now()}")
        #     print(f"User OTP: {otp}")
        #
        #     if not totp.verify(otp):
        #         return {
        #             'code': 50003,
        #             'message': "Google verification code error"
        #         }

        if ip:
            user.IP = ip
        # 记录登录日志
        login_record = LoginRecord(USER_ACCOUNT=user.ACCOUNT, IP=ip)
        db.session.add(login_record)

        db.session.commit()

        g.user = user
        token = user.generate_auth_token(mac=mac)

        print("the token", token.decode())

        return jsonify({
            'code': 20000,
            "token": "JWT %s" % token.decode()
        })

    except Exception as e:
        print("login error", e)
        return jsonify({
            'code': 50001,
            'message': "未知错误"
        })


@admin.route('/logout', methods=['POST'])
@auth.login_required
def logout():
    g.user = None
    return jsonify({
        'code': 20000,
        "message": "logout success"
    })


@admin.route('/info', methods=['GET'])
@auth.login_required
def admin_info():
    """
                @@@
                #### Args:

                #### Returns::
                        'code': 20000,
                         'data': {
                             'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
                             'introduction': "I am a super administrator",
                             'name': 'Super Admin',
                             'is_agent': False,
                             'agent_info': {
                                 'AGENT_CODE': '',
                                 'AGENT_NAME': "",
                                 'LEVEL': '',
                                 'SEX': '',
                                 'PHONE_NO': '',
                                 'STATUS': "",
                                 'TOTAL_MONEY': '',
                                 'CASH_MONEY': '',
                                 'SURPLUS_MONEY': '',
                                 'PROFIT': "",
                                 'CREATOR': '',
                                 'CREATOR_TIME': '',
                                 'UPDATOR': "",
                                 'REMARK': '',
                             },
                             "routes": [route.to_dict_with_permission(route_permissions) for route in top_routes if route.to_dict_with_permission(route_permissions)],
                             'roles': [role.to_dict() for role in user.ROLES]
                         }
                """
    user = g.user

    roles = user.ROLES
    role_routes = []
    for role in roles:
        role_routes += role.ROLE_ROUTES.all()
    # print(user.role)
    #
    # role_routes = user.role.ROLE_ROUTES.all()

    route_permissions = {}
    for role_route in role_routes:
        route_id = role_route.ROUTE_ID
        permission = role_route.PERMISSION
        if route_id in route_permissions:
            route_permissions[route_id] |= permission
        else:
            route_permissions[route_id] = permission

    for key, value in route_permissions.items():
        route_permissions[key] = PERMISSION.crud(value)

    top_routes = Route.query.filter(and_(Route.ID.in_(route_permissions), Route.parent_id == "0")).all()

    return jsonify({
        'code': 20000,
        'data': {
            'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
            'introduction': "I am a super administrator",
            'name': 'Super Admin',
            'info': g.user.to_dict(),
            'is_agent': True if g.user.AGENT_CODE else False,
            'agent_info': g.user.AGENT.to_dict() if g.user.AGENT_CODE else None,
            "routes": [route.to_dict_with_permission(route_permissions) for route in top_routes if
                       route.to_dict_with_permission(route_permissions)],
            'roles': [role.to_dict() for role in user.ROLES]
        }
    })


# 获取管理员列表
@admin.route('/get', methods=['GET'])
@auth.login_required
def get_admins():
    """
            @@@
            #### Args:
                key_word: 搜索关键字，搜索账号、用户名、手机号
                start_time: 开始时间
                end_time: 结束时间 
                role: 角色ID筛选
                page: 页码
                limit: 每页数量

            #### Returns::
                    {
                        "code": 20000,
                        "items": [
                          {
                            "ACCOUNT": "admin",
                            "AGENT_CODE": null,
                            "AGENT_NAME": null,
                            "CREATE_TIME": "2020-01-04 17:45:05",
                            "CREATOR": null,
                            "ID": 2,
                            "IP": null,
                            "LAST_LOGIN": "2020-01-05 16:10:01",
                            "NAME": null,
                            "PHONE": null,
                            "ROLES": [
                              {
                                "DESCRIPTION": null,
                                "ID": 2,
                                "NAME": "admin"
                              }
                            ],
                            "SKIN": null,
                            "STATUS": null,
                            "UPDATER": null,
                            "UPDATE_TIME": "None"
                          },
                          ...
                          ]
                    }
            """
    # 获取查询参数
    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    role = request.args.get('role')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 99))
    
    # 构建查询
    query = SysUser.query
    
    # 关键字搜索：搜索账号、用户名、手机号
    if key_word:
        query = query.filter(
            (SysUser.ACCOUNT.like(f'%{key_word}%')) |
            (SysUser.NAME.like(f'%{key_word}%')) |
            (SysUser.PHONE.like(f'%{key_word}%'))
        )
    
    # 时间范围筛选
    if start_time:
        start_date = datetime.datetime.strptime(start_time, '%Y-%m-%d')
        query = query.filter(SysUser.CREATE_TIME >= start_date)
    
    if end_time:
        end_date = datetime.datetime.strptime(end_time, '%Y-%m-%d')
        # 结束时间包含当天，所以加一天
        end_date = end_date + datetime.timedelta(days=1)
        query = query.filter(SysUser.CREATE_TIME < end_date)
    
    # 角色筛选
    if role:
        query = query.join(SysUser.ROLES).filter(Role.ID == int(role))
    
    users = query.all()
    print("someone querying with filters:", {
        'key_word': key_word, 
        'start_time': start_time, 
        'end_time': end_time, 
        'role': role,
        'results_count': len(users)
    })

    return jsonify({
        'code': 20000,
        'items': [user.to_dict() for user in users]
    })


@admin.route('/edit', methods=['POST'])
@auth.login_required
def edit_admin():
    """
        @@@
        #### Args:
                {
                   ID = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
                   ACCOUNT = Column(String(255), comment="账号")
                   NAME = Column(String(255), comment="用户名称")
                   STATUS = Column(String(32))
                   SKIN = Column(String(100))
                   PHONE = Column(String(32))
                   AGENT_CODE = Column(String(255), comment="所属代理ID")
                   AGENT_NAME = Column(String(255), comment="所属代理名称")
                   ROLES = [1, 2, ...]
                   PASSWORD = Column(String(255), comment="密码")

                   # 以下参数不需要传
                   IP = Column(String(100), comment="IP")
                   LAST_LOGIN = Column(TIMESTAMP, comment="最后登录时间")
                   UPDATER = Column(String(255), comment="修改人")
                }
        #### Returns::
                {'code': 20000, 'message': "修改成功"}
                {'code': 50001, 'message': "未知错误"}
        """
    args = request.get_json()
    edit_id = args.get('ID')
    role_ids = args.get('ROLES')
    password = args.get('PASSWORD')
    try:
        user = SysUser.query.filter_by(ID=edit_id).one_or_none()

        args['UPDATER'] = g.user.NAME
        args.pop('ROLES')
        if password:
            args.pop('PASSWORD')
            user.set_psw(password)
        OrmUttil.set_field(user, args)

        [user.ROLES.remove(u) for u in user.ROLES]

        for role_id in role_ids:
            role = Role.query.get(role_id)
            if role:
                user.ROLES.append(role)

        db.session.commit()
        user_opt.send({
            "operate": "修改管理员",
            "route": "系统管理",
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


@admin.route('/add', methods=['POST'])
@auth.login_required
def add_admin():
    """
        @@@
        #### Args:
                {
                   ACCOUNT = Column(String(255), comment="账号")
                   PASSWORD = Column(String(255), comment="密码")
                   NAME = Column(String(255), comment="用户名称")
                   STATUS = Column(String(32))
                   SKIN = Column(String(100))
                   PHONE = Column(String(32))
                   AGENT_CODE = Column(String(255), comment="所属代理ID")
                   AGENT_NAME = Column(String(255), comment="所属代理名称")
                   ROLES = [1, 2, ...]

                   # 以下参数不需要传
                   CREATOR = Column(String(255), comment="创建人")
                   IP = Column(String(100), comment="IP")
                   LAST_LOGIN = Column(TIMESTAMP, comment="最后登录时间")
                   UPDATER = Column(String(255), comment="修改人")
                }
        #### Returns::
                {'code': 20000, 'message': "添加成功"}
                {'code': 50001, 'message': "未知错误"}
        """

    args = request.get_json()
    account = args.get('ACCOUNT')
    password = args.get('PASSWORD')
    role_ids = args.get('ROLES')
    print("adding admin:", args)

    try:
        user = SysUser.query.filter_by(ACCOUNT=account).one_or_none()
        if user:
            return jsonify({
                'code': 50001,
                'message': 'account repeated!'
            })
        user = SysUser(ACCOUNT=account)

        args['CREATOR'] = g.user.NAME

        db.session.add(user)
        args.pop('ROLES')
        args.pop('PASSWORD')
        args.pop('AGENT_CODE')
        OrmUttil.set_field(user, args)
        user.set_psw(password)

        for role_id in role_ids:
            role = Role.query.get(role_id)
            print("got role?", role)
            if role:
                user.ROLES.append(role)

        db.session.commit()
        user_opt.send({
            "route": "系统管理",
            "operate": "添加管理员",
            "key_word": user.ACCOUNT,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "添加成功"})
    except Exception as e:
        print("add_admin error:", e)

    return jsonify({'code': 50001, 'message': "未知错误"})


@admin.route('/remove', methods=['POST'])
@auth.login_required
def remove_admin():
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
    args = request.get_json()
    remove_id = args.get('ID')
    try:

        user = SysUser.query.filter_by(ID=remove_id).one_or_none()
        # 删除关联roles将被动删除
        db.session.delete(user)
        db.session.commit()
        user_opt.send({
            "operate": "删除管理员",
            "route": "系统管理",
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
