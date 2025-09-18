import time
from _decimal import Decimal
from sqlalchemy import or_, func
from management_server import app, db, auth, user_opt, app_opt, Redis
from management_server.model.ChargeCallback import ChargeCallback, ChargeCallbackStatus
from management_server.model.SysBankcardModel import SysBankcard
from management_server.utils.OrmUttil import AppOpType
from management_server.model.ChargeModel import Charge
from management_server.model.AppUserModel import AppUser
from management_server.model.AgentModel import Agent
from management_server.model.SysUserModel import SysUser
from flask import g, request, jsonify, Blueprint
from management_server.utils import OrmUttil
from datetime import datetime, timedelta

charge = Blueprint('charge', __name__)


# 获取订单列表
@charge.route('/get', methods=['GET'])
@auth.login_required
def get_charge_list():
    print("get_charge_list called with args:", dict(request.args))
    """
                @@@
                #### Args:
                        current_page = request.args.get('page', type=int, default=1)
                        limit = request.args.get('limit', type=int, default=20)
                        key_word = request.args.get('key_word')
                        start_time = request.args.get('start_time')
                        end_time = request.args.get('end_time')
                        is_pay =
                        charge_type = 充值对象类型: 0:用户 1:代理
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
    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    charge_type = request.args.get('charge_type')
    charge_way = request.args.get("charge_way")

    charge_list = Charge.query

    # if g.user.AGENT_CODE:
    #     users_under = AppUser.query.filter_by(AGENT_ID=g.user.AGENT_CODE).all()
    #     users_under = set([u.USER_ID for u in users_under])
    #     charge_list = charge_list.filter(Charge.USER_ID.in_(users_under))
    #     # charge_list = charge_list.filter(Charge.CREATOR == g.user.AGENT_CODE)
    # elif 'admin' not in {r.NAME for r in g.user.ROLES}:
    #     charge_list = charge_list.filter(Charge.CREATOR == g.user.ACCOUNT)

    if g.user.is_agent():
        all_account = SysUser.query.filter_by(AGENT_CODE=g.user.AGENT_CODE).all()
        all_account = {a.ACCOUNT for a in all_account}
        charge_list = charge_list.filter(Charge.CREATOR.in_(all_account))
    elif g.user.is_agent_child():
        charge_list = charge_list.filter(Charge.CREATOR == g.user.ACCOUNT)
    elif 'admin' not in {r.NAME for r in g.user.ROLES}:
        charge_list = charge_list.filter(Charge.CREATOR == g.user.ACCOUNT)

    if charge_way:
        charge_list = charge_list.filter(Charge.CHARGE_WAY == charge_way)
    if charge_type:
        charge_list = charge_list.filter(Charge.CHARGE_TYPE == charge_type)

    if key_word:
        charge_list = charge_list.filter(
            or_(Charge.RECHARGE_ID.like('%{}%'.format(key_word)), Charge.USER_ID.like('%{}%'.format(key_word)),
                Charge.NICK_NAME.like('%{}%'.format(key_word)), Charge.REMARK.like('%{}%'.format(key_word))))

    if start_time:
        start_time += ' 00:00:00'
        charge_list = charge_list.filter(Charge.CREATOR_TIME >= start_time)

    if end_time:
        end_time += ' 23:59:59'
        charge_list = charge_list.filter(Charge.CREATOR_TIME <= end_time)

    total = charge_list.count()
    total_amount = charge_list.with_entities(func.sum(Charge.MONEY)).scalar() or 0

    charge_list = charge_list.offset((current_page - 1) * limit).limit(limit).all()
    
    print(f"Found {len(charge_list)} charges, total: {total}, total_amount: {total_amount}")
    for charge_item in charge_list[:3]:  # 只显示前3条记录的调试信息
        print(f"Charge: {charge_item.RECHARGE_ID}, User: {charge_item.USER_ID}, Amount: {charge_item.MONEY}")

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in charge_list],
        'total': total,
        'total_amount': total_amount
    })


@charge.route('/user_info', methods=['GET'])
def get_user_info():
    user_id = request.args.get("USER_ID")
    try:
        user = AppUser.query.filter_by(USER_ID=user_id).one_or_none()
        if user:
            return jsonify({'code': 20000, 'info': user.to_dict()})
        else:
            return jsonify({'code': 20000, 'info': ''})
    except Exception as e:
        print("user info error:", e)
    return jsonify({'code': 50001, 'message': "未知错误"})


@charge.route('/get_charge_total', methods=['GET'])
@auth.login_required
def get_charge_total():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    try:
        charge_list = Charge.query
        if start_time:
            charge_list = charge_list.filter(Charge.CREATOR_TIME >= start_time)
        if end_time:
            charge_list = charge_list.filter(Charge.CREATOR_TIME <= end_time)
        if g.user.AGENT_CODE:
            charge_list = charge_list.filter(Charge.CREATOR == g.user.AGENT_CODE)

        charge_sum = 0
        for charge_obj in charge_list:
            charge_sum += float(charge_obj.MONEY)

        return jsonify({'code': 20000, 'result': charge_sum})

    except Exception as e:
        print("user info error:", e)
    return jsonify({'code': 50001, 'message': "未知错误"})


@charge.route('/get_charge_report', methods=['GET'])
def get_charge_report():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    try:
        charge_list = Charge.query
        if start_time:
            charge_list = charge_list.filter(Charge.CREATOR_TIME >= start_time)

        if end_time:
            charge_list = charge_list.filter(Charge.CREATOR_TIME <= end_time)

        charge_list = charge_list.all()
        agent_list = Agent.query.all()
        result = []
        for agent_obj in agent_list:
            temp = {'agent_name': agent_obj.AGENT_NAME, 'agent_charge_sum': 0}
            for charge_obj in charge_list:
                if agent_obj.AGENT_CODE == charge_obj.CREATOR:
                    temp['agent_charge_sum'] += float(charge_obj.MONEY)
            result.append(temp)

        return jsonify({'code': 20000, 'info': result})

    except Exception as e:
        print("user info error:", e)
    return jsonify({'code': 50001, 'message': "未知错误"})


@charge.route('/latest_list', methods=['GET'])
def latest_list():
    page_size = request.args.get("pageSize")
    charge_list = Charge.query.order_by(Charge.CREATOR_TIME).limit(page_size).all()

    return jsonify({'code': 20000, 'items': [u.to_dict() for u in charge_list]})


@charge.route('/add_to_agent', methods=['POST'])
@auth.login_required
def add_to_agent():
    """

                @@@
                #### Args:
                        AGENT_CODE : String(64) "用户游戏ID"
                        MONEY : String(64) "金额"
                        REMARK : String(256) "备注：（代给代冲卡）"

                #### Returns::
                        {'code': 20000, 'message': "添加成功"}
                        {'code': 50001, 'message': "未知错误"}
            """
    args = request.get_json()
    agent_code = args.get("AGENT_CODE")
    money = float(args.get("MONEY"))
    remark = args.get('REMARK')

    try:
        charge_id = int(round(time.time() * 1000))
        recharge = Charge(RECHARGE_ID=charge_id)

        OrmUttil.set_field(recharge, request.args)

        agent = Agent.query.filter(Agent.AGENT_CODE == agent_code).with_for_update().first()
        before_amount = float(agent.SURPLUS_MONEY or 0)
        agent.SURPLUS_MONEY = before_amount + money

        recharge.BEFORE_MONEY = before_amount
        recharge.AFTER_MONEY = before_amount + money
        recharge.USER_ID = agent_code
        recharge.NICK_NAME = agent.AGENT_NAME
        recharge.MONEY = money
        if remark:
            recharge.REMARK = remark

        recharge.CREATOR = g.user.ACCOUNT
        # if g.user.AGENT_CODE:
        #     recharge.CREATOR = g.user.AGENT_CODE
        recharge.CHARGE_TYPE = "1"

        db.session.add(recharge)
        db.session.commit()
        app_opt.send({
            "user_account": g.user.ACCOUNT,
            "user_name": agent.AGENT_NAME,
            "type": AppOpType.CHARGE,
            "amount": before_amount,
            "balance": float(before_amount + money),
            "source_id": charge_id
        })
        return jsonify({'code': 20000, 'message': "添加成功", "info": agent.to_dict()})
    except Exception as e:
        print("add match error:", e)

    return jsonify({'code': 50001, 'message': "未知错误"})


@charge.route('/add', methods=['POST'])
@auth.login_required
def add_charge():
    """

                @@@
                #### Args:
                        CHARGE_TYPE : String(10)
                        USER_ID : String(64) "用户游戏ID"
                        NICK_NAME : String(64) "用户昵称"
                        CHARGE_NUM : String(8) "冲卡数量"
                        CHARGE_NAME : String(255)
                        MONEY : String(64) "金额"
                        REMARK : String(256) "备注：（代给代冲卡）"
                        CREATOR : String(64) "所属代理商id"
                        CREATOR_TIME : TIMESTAMP "冲卡时间"

                #### Returns::
                        {'code': 20000, 'message': "添加成功"}
                        {'code': 50001, 'message': "未知错误"}
            """
    args = request.get_json()
    user_id = args.get("USER_ID")
    money_str = args.get("MONEY")
    remark = args.get('REMARK')
    
    # 验证必填字段
    if not user_id or not user_id.strip():
        return jsonify({'code': 50001, 'message': "USER_ID is required"})
    
    if not money_str or not str(money_str).strip():
        return jsonify({'code': 50001, 'message': "MONEY is required"})
    
    try:
        money = float(money_str)
        if money <= 0:
            return jsonify({'code': 50001, 'message': "Amount must be greater than 0"})
    except (ValueError, TypeError):
        return jsonify({'code': 50001, 'message': "Invalid amount format"})

    try:
        app_user = AppUser.query.filter_by(OPENID=user_id).one_or_none()
        if not app_user:
            return jsonify({'code': 50003, 'message': "user not exist."})

        # 2021/05/22 防止重复提现
        repeat_key = "user_charge_%s_%s" % (app_user.USER_ID, str(money))
        if Redis.get(repeat_key):
            return jsonify({'code': 50002, 'message': "Too many operations. Please wait"})
        Redis.set(repeat_key, 1, ex=10)

        db.session.commit()
        main_id = app_user.MAJUSER_ID
        del app_user
        app_user = AppUser.query.filter_by(MAJUSER_ID=main_id).with_for_update().first()

        # if app_user.AGENT_ID:
        #     if not g.user.AGENT_CODE or app_user.AGENT_ID != g.user.AGENT_CODE:
        #         return jsonify({'code': 50003, 'message': "You are not the agent of this user."})
        # elif g.user.AGENT_CODE:
        agent_equal = not app_user.AGENT_ID and not g.user.AGENT_CODE

        if app_user.AGENT_ID != g.user.AGENT_CODE and not agent_equal:
            return jsonify({'code': 50003, 'message': "You are not the agent of this user."})

        charge_id = int(round(time.time() * 1000))
        recharge = Charge(RECHARGE_ID=charge_id)
        recharge.CREATOR = g.user.ACCOUNT
        agent_before = 0
        agent_after = 0
        agent_name = ""
        if g.user.AGENT_CODE:
            # 2021/05/22 防止重复充值
            repeat_key = "a2u_charge%s_%s_%s" % (g.user.AGENT_CODE, user_id, money)
            print("about to add key:", repeat_key)
            print("redis---", Redis.get(repeat_key))
            if Redis.get(repeat_key):
                return jsonify({'code': 50002, 'message': "Too many same operations. Please wait."})
            Redis.set(repeat_key, 1, ex=15)

            # 代理处理会员提现时 需要扣除代理余额
            agent = Agent.query.filter(Agent.AGENT_CODE == g.user.AGENT_CODE).with_for_update().first()
            if float(agent.SURPLUS_MONEY or 0) < float(money):
                return jsonify({'code': 50002, 'message': "Agent money not enough."})
            agent_before = agent.SURPLUS_MONEY
            agent.SURPLUS_MONEY = float(agent.SURPLUS_MONEY) - float(money)
            agent_after = float(agent.SURPLUS_MONEY)
            agent_name = agent.AGENT_NAME
        # OrmUttil.set_field(recharge, request.args)
        recharge.CHARGE_TYPE = "0"

        before_amount = float(app_user.TOTAL_MONEY)
        after_amount = before_amount + money
        app_user.TOTAL_MONEY = after_amount

        recharge.BEFORE_MONEY = before_amount
        recharge.AFTER_MONEY = after_amount
        recharge.USER_ID = user_id
        recharge.NICK_NAME = g.user.NAME
        recharge.MONEY = money

        if remark:
            recharge.REMARK = remark

        db.session.add(recharge)
        db.session.commit()
        app_opt.send({
            "user_account": app_user.OPENID,
            "user_name": app_user.NICK_NAME,
            "type": AppOpType.CHARGE,
            "amount": before_amount,
            "balance": float(app_user.TOTAL_MONEY),
            "source_id": charge_id
        })

        if g.user.AGENT_CODE:
            app_opt.send({
                "user_account": g.user.ACCOUNT,
                "user_name": agent_name,
                "type": AppOpType.CHARGE,
                "amount": agent_before,
                "balance": agent_after,
                "source_id": charge_id
            })
        return jsonify({'code': 20000, 'message': "添加成功", "info": app_user.to_dict()})
    except Exception as e:
        print("add match error:", e)

    return jsonify({'code': 50001, 'message': "未知错误"})


def is_valid_date_time(str_date):
    try:
        time.strptime(str_date, "%d/%m/%Y %H:%M:%S")
        time.strptime(str_date, "%Y%m%d %H:%M:%S")
        time.strptime(str_date, "%Y-%m-%d %H:%M:%S")
        return True
    except Exception as e:
        return False


@charge.route('/pay_callback', methods=['POST'])
def pay_callback():
    print("calling charge pay_callback:", request.form, request.get_json())
    ""
    # args = {'transactionID': '01002791020079524252', 'customerBankCode': 'KBZ', 'customerBankAccount': 'THIHA (******2241)',
    # 'receiverBankAccount': '09942471306', 'dateTime': '23/08/2022 12:28:28', 'amount': '20.00', 'signature': '0335b1ddbac1809386c0c9df6db01490'}
    args = request.get_json() or request.form
    transaction_id = args.get('transactionID')
    amount = Decimal(args.get('amount'))
    receiver_bank_account = args.get('receiverBankAccount')
    receiver_bank_code = args.get('customerBankCode')
    transaction_datetime = args.get('dateTime')
    cash_code = args.get('remark')

    try:
        getter_key = "transaction%s_%s" % (receiver_bank_code, transaction_id)

        # 使用nx=True确保只在键不存在时设置键
        if not Redis.set(getter_key, 1, nx=True, ex=2):
            return "transaction callback repeated"

        # 这段代码的防止并发效果不好
        # if not Redis.exists(getter_key):
        #     Redis.set(getter_key, 0, ex=2)
        # else:
        #     return "transaction callback repeated"

        # 校验数据合法性
        if not transaction_id.isdigit():
            return "transaction id not valid"
        # if not is_valid_date_time(transaction_datetime):
        #     return "transaction datetime not valid"

        # 校验md5
        from hashlib import md5
        secret_key = "BPXzUzneHUqivnkvq3qc"
        data_str = args.get('transactionID') + args.get('customerBankCode') + args.get(
            'customerBankAccount') + args.get('receiverBankAccount') + args.get('dateTime') + str(
            args.get('amount')) + secret_key
        md5_encrypt = md5(data_str.encode("utf-8")).hexdigest()
        if md5_encrypt != args.get('signature'):
            return "transaction not valid"

        old_tran = ChargeCallback.query.filter(ChargeCallback.TRANSACTION_ID == transaction_id).first()
        if old_tran:
            return "success"
        transaction = ChargeCallback(TRANSACTION_ID=args.get('transactionID'), CUSTOMER_BANK_CODE=receiver_bank_code,
                                     CUSTOMER_BANK_ACCOUNT=args.get('customerBankAccount'),
                                     RECEIVER_BANK_ACCOUNT=receiver_bank_account,
                                     TRANSACTION_DATETIME=transaction_datetime, AMOUNT=args.get('amount'),
                                     SIGNATURE=args.get('signature'))
        db.session.add(transaction)

        # 银行卡操作
        sys_bankcard = SysBankcard.query.filter(SysBankcard.ACCOUNT == receiver_bank_account,
                                                SysBankcard.BANK_CODE == receiver_bank_code).first()
        if sys_bankcard:

            sys_bankcard.INCOME += amount
            today_charge = sys_bankcard.get_today_charge()

            if today_charge > sys_bankcard.DAILY_LIMIT:
                # 取消此卡的启用状态
                if sys_bankcard.ENABLE:
                    sys_bankcard.ENABLE = False
                other_cards = SysBankcard.query.filter(SysBankcard.ENABLE.is_(False),
                                                       SysBankcard.BANK_CODE == sys_bankcard.BANK_CODE,
                                                       SysBankcard.ID != sys_bankcard.ID).all()
                for other_card in other_cards:
                    card_charge = other_card.get_today_charge()
                    if card_charge < other_card.DAILY_LIMIT:
                        other_card.ENABLE = True
                        break

        # 查找用户，并且写入充值记录，写入帐变
        if not cash_code:

            if receiver_bank_code == 'KBZ':
                transaction.STATUS = ChargeCallbackStatus.Invalid
                print("args can't find remark by this transaction:", transaction_id)
            db.session.commit()
            return "success"

        cash_code = cash_code.strip()
        app_user = AppUser.query.filter_by(CASH_CODE=cash_code).with_for_update().first()

        if not app_user:
            transaction.STATUS = ChargeCallbackStatus.Invalid
            print("can't find app user by this cash code:", cash_code)
            db.session.commit()
            return "success"

        if not app_user.USER_ID:
            transaction.STATUS = ChargeCallbackStatus.Invalid
            print("can't find USERID this app user:", app_user.MAJUSER_ID)
            db.session.commit()
            return "success"

        charge_id = int(round(time.time() * 1000))
        recharge = Charge(RECHARGE_ID=charge_id, CHARGE_WAY=1)

        recharge.CHARGE_TYPE = "0"

        money = float(amount)
        if money >= 5000:
            before_amount = float(app_user.TOTAL_MONEY)
            after_amount = before_amount + money
            app_user.TOTAL_MONEY = after_amount

            recharge.BEFORE_MONEY = before_amount
            recharge.AFTER_MONEY = after_amount
            recharge.USER_ID = app_user.USER_ID
            recharge.NICK_NAME = app_user.NICK_NAME
            recharge.MONEY = money

            db.session.add(recharge)

            transaction.USER_ID = app_user.USER_ID
            transaction.NICK_NAME = app_user.NICK_NAME
            transaction.STATUS = ChargeCallbackStatus.Confirm
        else:
            transaction.STATUS = ChargeCallbackStatus.Invalid

        app_opt.send({
            "user_account": app_user.OPENID,
            "user_name": app_user.NICK_NAME,
            "type": AppOpType.CHARGE,
            "amount": before_amount,
            "balance": float(app_user.TOTAL_MONEY),
            "source_id": charge_id
        })

        db.session.commit()
        return "success"
    except Exception as e:
        print("pay_callback error:", e)
    return "error"
