from management_server import app, db, auth, user_opt
from management_server.model.AppUserModel import AppUser
from management_server.model.ChargeModel import Charge
from flask import g, request, jsonify, Blueprint
from management_server.utils import OrmUttil
from sqlalchemy import or_, func, and_, cast,Numeric
from datetime import datetime
import uuid
import hashlib
import time
import calendar

app_user = Blueprint('app_user', __name__)


# 获取所有用户列表
@app_user.route('/get', methods=['GET'])
@auth.login_required
def get_app_user_list():
    """
                @@@
                #### Args:
                        current_page = request.args.get('page', type=int, default=1)
                        limit = request.args.get('limit', type=int, default=20)

                        key_word = request.args.get('key_word')
                        start_time = request.args.get('start_time')
                        end_time = request.args.get('end_time')

                        agent_id = request.args.get('agent_id')

                        status = request.args.get('status')            状态（ 0：正常 1：禁用） 无参表示全部
                #### Returns::
                        {
                            'code': 20000,
                            'items': [u.to_dict() for u in user_list],
                            'total': total,
                            'total_amount': total_amount,             总金额
                            'total_cash': total_cash                  总提现
                        }
            """

    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)

    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    agent_id = request.args.get('agent_id')

    status = request.args.get('status')
    cash_code = request.args.get('cash_code')

    order_by_select = request.args.get('order_by_select')

    order_by_options = {
        'total_money': cast(AppUser.TOTAL_MONEY, Numeric),
        'cash_code': AppUser.CASH_CODE,
        'create_time': AppUser.CREAT_TIME,
        'login_time': AppUser.OPT_TIME
    }

    user_list = AppUser.query

    if g.user.AGENT_CODE:
        users_under = AppUser.query.filter_by(AGENT_ID=g.user.AGENT_CODE).all()
        users_under = set([u.USER_ID for u in users_under])
        user_list = user_list.filter(AppUser.USER_ID.in_(users_under))

    if key_word:
        user_list = user_list.filter(
            or_(AppUser.OPENID.like('%{}%'.format(key_word)), AppUser.USER_ID.like('%{}%'.format(key_word)),
                AppUser.NICK_NAME.like('%{}%'.format(key_word)), AppUser.BANK_CARD.like('%{}%'.format(key_word)),
                AppUser.PHONE.like('%{}%'.format(key_word)), AppUser.BANK_USER_NAME.like('%{}%'.format(key_word))))

    if status:
        user_list = user_list.filter(AppUser.STATUS == status)

    if cash_code:
        user_list = user_list.filter(AppUser.CASH_CODE == cash_code)

    if start_time:
        user_list = user_list.filter(AppUser.CREAT_TIME >= start_time)

    if end_time:
        end_time += ' 23:59:59'
        user_list = user_list.filter(AppUser.CREAT_TIME <= end_time)

    if agent_id:
        user_list = user_list.filter(AppUser.AGENT_ID == agent_id)

    if order_by_select:
        if order_by_select == 'cash_code':
            user_list = user_list.order_by(order_by_options[order_by_select].asc())
        else:
            user_list = user_list.order_by(order_by_options[order_by_select].desc())

    total_amount = user_list.with_entities(func.sum(AppUser.TOTAL_MONEY)).scalar() or 0
    total_cash = user_list.with_entities(func.sum(AppUser.CASH_MONEY)).scalar() or 0

    total = user_list.count()

    user_list = user_list.offset((current_page - 1) * limit).limit(limit).all()

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in user_list],
        'total': total,
        'total_amount': total_amount,
        'total_cash': total_cash
    })


# 获取所有未绑定代理的用户列表
@app_user.route('/get_unset_agent_users', methods=['GET'])
@auth.login_required
def get_unset_agent_users():
    """
                @@@
                #### Args:
                        current_page = request.args.get('page', type=int, default=1)
                        limit = request.args.get('limit', type=int, default=20)

                        key_word = request.args.get('key_word')
                        start_time = request.args.get('start_time')
                        end_time = request.args.get('end_time')

                        agent_id = request.args.get('agent_id')

                        status = request.args.get('status')            状态（ 0：正常 1：禁用） 无参表示全部
                #### Returns::
                        {
                            'code': 20000,
                            'items': [u.to_dict() for u in user_list],
                            'total': total,
                            'total_amount': total_amount,             总金额
                            'total_cash': total_cash                  总提现
                        }
            """

    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)

    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    # 根据充值时间筛选客户
    charge_list = Charge.query
    if start_time:
        charge_list = charge_list.filter(Charge.CREATOR_TIME >= start_time)

    if end_time:
        end_time += ' 23:59:59'
        charge_list = charge_list.filter(Charge.CREATOR_TIME <= end_time)

    # 把充值过的用户id加入列表
    user_id_list = []
    for item in charge_list:
        if item.USER_ID not in user_id_list:
            user_id_list.append(item.USER_ID)

    user_list = AppUser.query.filter(and_(AppUser.USER_ID.in_(user_id_list), AppUser.AGENT_ID.is_(None)))

    if key_word:
        user_list = user_list.filter(
            or_(AppUser.OPENID.like('%{}%'.format(key_word)), AppUser.USER_ID.like('%{}%'.format(key_word)),
                AppUser.NICK_NAME.like('%{}%'.format(key_word)), AppUser.BANK_CARD.like('%{}%'.format(key_word)),
                AppUser.PHONE.like('%{}%'.format(key_word)), AppUser.BANK_USER_NAME.like('%{}%'.format(key_word))))

    total = user_list.count()

    user_list = user_list.offset((current_page - 1) * limit).limit(limit).all()

    return jsonify({
        'code': 20000,
        'noAgentUserTotal': total,
        'items': [u.to_dict() for u in user_list],
    })


@app_user.route('/add', methods=['POST'])
@auth.login_required
def add_app_user():
    """
    @@@
    #### Args:
            NICK_NAME = Column(String(255), comment="昵称")               必填
            STATUS = Column(String(6), comment="状态（ 0：正常 1：禁用）")
            SEX = Column(String(2), comment="性别（0:男 1：女）")
            PROVINCE = Column(String(64), comment="省份(暂不用)")
            CITY = Column(String(64), comment="城市(暂不用)")
            PHONE = Column(String(40), comment="手机号码")               必填
            ROOM_CARD = Column(Integer)
            CREAT_TIME = Column(TIMESTAMP, default=datetime.datetime.now)
            OPT_TIME = Column(TIMESTAMP, comment="操作时间")

            LOGO_URL = Column(String(255), comment="头像路径")
            USER_PWD = Column(String(100), comment="用户密码")               必填
            BANK_CARD = Column(String(64), comment="银行卡")
            BANK_USER_NAME = Column(String(255), comment="用户真实姓名")
            AGENT_ID = Column(String(16), comment="代理商id,绑定代理商")
    #### Returns::
            {'code': 20000, 'message': "添加成功"}
            {'code': 50001, 'message': "未知错误"}
    """

    args = request.get_json()

    phone = args.get("PHONE")
    psw = args.get("USER_PWD")

    try:
        if not phone.isdigit():
            return jsonify({'code': 50002, 'message': "0မှ9သာဖြည့်ရန်."})
        old_user = AppUser.query.filter_by(OPENID=phone).one_or_none()
        if old_user:
            return jsonify({'code': 50002, 'message': "The phone num has exist."})

        user = AppUser(MAJUSER_ID=str(uuid.uuid4()).replace("-", ""), OPENID=phone, USER_ID=phone)
        user.CASH_CODE = user.generate_new_cash_code()
        db.session.add(user)

        # psw_md5 = hashlib.md5(psw.encode(encoding='utf-8')).hexdigest()
        psw_sha1 = hashlib.sha1((psw + phone).encode(encoding='utf-8')).hexdigest()
        args['USER_PWD'] = psw_sha1
        args['OPENID'] = phone
        args['USER_ID'] = phone

        # 判断当前系统用户是不是代理
        if g.user.AGENT_CODE:
            args['AGENT_ID'] = g.user.AGENT_CODE

        # OrmUttil.set_field(user, args)
        OrmUttil.set_field(user, args, exclude=['TOTAL_MONEY', 'CASH_MONEY', ])

        db.session.commit()

        user_opt.send({
            "operate": "Add New User",
            "route": "User Info",
            "key_word": user.USER_ID,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "添加成功"})
    except Exception as e:
        print("add match error:", e)

    return jsonify({'code': 50001, 'message': "未知错误"})


@app_user.route('/remove', methods=['GET'])
@auth.login_required
def remove_app_user():
    """
            @@@
            #### Args:
                    remove_id = request.args.get('match_id')
            #### Returns::
                    {'code': 20000, 'message': "删除成功"}
                    {'code': 50001, 'message': "未知错误"}
        """
    remove_id = request.args.get('USER_ID')

    if remove_id:
        try:
            AppUser.query.filter_by(OPENID=remove_id).delete()

            user_opt.send({
                "operate": "Delete User %s" % remove_id,
                "route": "User Info",
                "key_word": remove_id,
                "user": g.user.ACCOUNT
            })

            db.session.commit()
            return jsonify({'code': 20000, 'message': "删除成功"})
        except Exception as e:
            print("remove_bet_account del error: ", e)
    return jsonify({'code': 50001, 'message': "未知错误"})


@app_user.route('/edit', methods=['POST'])
@auth.login_required
def edit_app_user():
    """
            @@@
            #### Args:
                    NICK_NAME = Column(String(255), comment="昵称")
                    STATUS = Column(String(6), comment="状态（ 0：正常 1：禁用）")
                    SEX = Column(String(2), comment="性别（0:男 1：女）")
                    PROVINCE = Column(String(64), comment="省份(暂不用)")
                    CITY = Column(String(64), comment="城市(暂不用)")
                    ROOM_CARD = Column(Integer)
                    CREAT_TIME = Column(TIMESTAMP, default=datetime.datetime.now)
                    OPT_TIME = Column(TIMESTAMP, comment="操作时间")

                    LOGO_URL = Column(String(255), comment="头像路径")
                    BANK_CARD = Column(String(64), comment="银行卡")
                    BANK_USER_NAME = Column(String(255), comment="用户真实姓名")
                    AGENT_ID = Column(String(16), comment="代理商id,绑定代理商")
            #### Returns::
                    {'code': 20000, 'message': "修改成功"}
                    {'code': 50001, 'message': "未知错误"}
        """
    args = request.get_json()
    edit_id = args.get('USER_ID')
    phone = args.get("PHONE")

    if edit_id:
        if phone and not phone.isdigit():
            return jsonify({'code': 50002, 'message': "0မှ9သာဖြည့်ရန်."})
        user = AppUser.query.filter_by(USER_ID=edit_id).first_or_404()

        operate = "Edit User Info:"
        if args.get('USER_PWD'):
            operate += ', ' + 'USER_PWD'
            psw_sha1 = hashlib.sha1((args['USER_PWD'] + user.OPENID).encode(encoding='utf-8')).hexdigest()
            args['USER_PWD'] = psw_sha1

        if args.get('TOTAL_MONEY'):
            args.pop('TOTAL_MONEY')

        user_dict = user.to_dict()
        for key, value in args.items():
            if key != 'USER_PWD' and str(user_dict[key]) != str(value):
                operate += ', ' + key

        OrmUttil.set_field(user, args,
                           include={"NICK_NAME", "PHONE", "USER_PWD", "BANK_CARD", "BANK_USER_NAME", "AGENT_ID",
                                    "STATUS", "HIGHER_LIMIT", "IS_VIP"})

        user_opt.send({
            "operate": operate,
            "route": "User Info",
            "key_word": edit_id,
            "user": g.user.ACCOUNT
        })

        db.session.commit()
        return jsonify({'code': 20000, 'message': "修改成功"})
    else:
        return jsonify({'code': 50001, 'message': "未知错误"})
