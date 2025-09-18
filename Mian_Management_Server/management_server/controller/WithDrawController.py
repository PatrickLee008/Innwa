from sqlalchemy import or_, func, and_
from management_server import Redis, db, auth, user_opt, app_opt
from management_server.utils.OrmUttil import AppOpType
from management_server.model.AppUserModel import AppUser
from management_server.model.AgentModel import Agent
from management_server.model.WithDrawModel import WithDraw
from management_server.model.WithDrawGroupModel import WithDrawGroup
from flask import g, request, jsonify, Blueprint
import json
import uuid

withdraw = Blueprint('withdraw', __name__)


# 获取订单列表
@withdraw.route('/get', methods=['GET'])
@auth.login_required
def get_withdraw_list():
    """
                @@@
                #### Args:
                        current_page = request.args.get('page', type=int, default=1)
                        limit = request.args.get('limit', type=int, default=20)

                        pay_type = request.args.get('pay_type', default="2")      //提现类型 1: 代理    2:玩家

                        key_word = request.args.get('key_word')
                        start_time = request.args.get('start_time')
                        end_time = request.args.get('end_time')
                        is_pay = request.args.get('is_pay') 是否付款 0未付款 1已付款 不传此参数则表示全部
                        group_id
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

    pay_type = request.args.get('pay_type', default="2")
    group_id = request.args.get('group_id', type=int, default=0)

    withdraw_list = WithDraw.query.filter_by(PAY_TYPE=pay_type).order_by(WithDraw.CREATE_TIME.desc())

    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    is_pay = request.args.get('is_pay')

    print("fu request:", request.args)

    if g.user.AGENT_CODE:
        if pay_type == "2":
            users_under = AppUser.query.filter_by(AGENT_ID=g.user.AGENT_CODE).all()
            users_under = set([u.USER_ID for u in users_under])
            withdraw_list = withdraw_list.filter(WithDraw.USER_ID.in_(users_under))
        else:
            withdraw_list = withdraw_list.filter(WithDraw.USER_ID == g.user.AGENT_CODE)
    elif 'admin' not in {r.NAME for r in g.user.ROLES}:
        # 如果不是管理员， 过滤出未处理的提现 ， 以及自己处理过的提现
        withdraw_list = withdraw_list.filter(or_(WithDraw.OPERATOR == g.user.ACCOUNT, WithDraw.IS_PAY == '0'), WithDraw.Work_Group == g.user.Withdraw_Group)

    if key_word:
        withdraw_list = withdraw_list.filter(
            or_(WithDraw.USER_ID.like('%{}%'.format(key_word)), WithDraw.WITHDRAWAL_ID.like('%{}%'.format(key_word)),
                WithDraw.NICK_NAME.like('%{}%'.format(key_word))))

    if is_pay:
        withdraw_list = withdraw_list.filter(WithDraw.IS_PAY == is_pay)

    if start_time:
        start_time += " 00:00:00"
        withdraw_list = withdraw_list.filter(WithDraw.CREATE_TIME >= start_time)

    if end_time:
        end_time += " 23:59:59"
        withdraw_list = withdraw_list.filter(WithDraw.CREATE_TIME <= end_time)

    if group_id:
        withdraw_list = withdraw_list.filter(WithDraw.Work_Group == group_id)

    total_amount = withdraw_list.with_entities(func.sum(WithDraw.MONEY)).scalar() or 0

    total = withdraw_list.count()

    withdraw_list = withdraw_list.offset((current_page - 1) * limit).limit(limit).all()

    # 修改提现组名称
    all_group_names = WithDrawGroup.query.all()
    name_dict = {u.ID: u.GROUP_NAME for u in all_group_names}
    items = []
    for wd in withdraw_list:
        wd = wd.to_dict()
        if wd['Work_Group'] in name_dict:
            wd['Work_Group'] = name_dict[wd['Work_Group']]
        items.append(wd)

    # print("---------", request.args, withdraw_list)

    return jsonify({
        'code': 20000,
        'items': items,
        'total': total,
        'total_amount': total_amount
    })


@withdraw.route('/latest_list', methods=['GET'])
def latest_list():
    page_size = request.args.get("pageSize")
    withdraw_list = WithDraw.query.order_by(WithDraw.CREATE_TIME).limit(page_size).all()

    return jsonify({'code': 20000, 'items': [u.to_dict() for u in withdraw_list]})


@withdraw.route('/remove', methods=['POST'])
@auth.login_required
def remove_withdraw():
    """
        @@@
        #### Args:
                {
                   "remove_id": 1,
                }
        #### Returns::
                {'code': 20000, 'message': "删除成功"}
                {'code': 50001, 'message': "未知错误"}
        """
    args = request.get_json()
    remove_id = args.get('remove_id')
    print("remove_withdraw args", args)
    try:
        the_withdraw = WithDraw.query.filter_by(WITHDRAWAL_ID=remove_id).one_or_none()
        if not the_withdraw:
            return jsonify({'code': 50002, 'message': "WithDraw not exist."})
        db.session.delete(the_withdraw)
        db.session.commit()

        user_opt.send({
            "operate": "删除提现",
            "route": "提现管理",
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


@withdraw.route('/get_total_withdraw', methods=['GET'])
@auth.login_required
def get_total_withdraw():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    try:
        withdraw_list = WithDraw.query

        if start_time:
            withdraw_list = withdraw_list.filter(WithDraw.CREATE_TIME >= start_time)
        if end_time:
            withdraw_list = withdraw_list.filter(WithDraw.CREATE_TIME <= end_time)
        if g.user.AGENT_CODE:
            withdraw_list = withdraw_list.filter(WithDraw.OPERATOR == g.user.AGENT_CODE)

        withdraw_sum = 0
        for withdraw_obj in withdraw_list:
            withdraw_sum += float(withdraw_obj.MONEY)

        return jsonify({'code': 20000, 'result': withdraw_sum})
    except Exception as e:
        print("user info error:", e)


@withdraw.route('/agent_withdraw', methods=['POST'])
@auth.login_required
def add_agent_withdraw():
    """
            代理发起提现
            @@@
            #### Args:
                    edit_id = request.args.get('agent_id')
                    money = request.args.get('MONEY')
            #### Returns::
                    {'code': 20000, 'message': "修改成功"}
                    {'code': 50001, 'message': "未知错误"}
        """
    money = request.get_json().get('MONEY')
    try:
        agent = Agent.query.filter(Agent.AGENT_CODE == g.user.AGENT_CODE).with_for_update().first()
        before_amount = float(agent.SURPLUS_MONEY or 0)
        if before_amount < float(money):
            return jsonify({'code': 50002, 'message': "agent money not enough."})

        from management_server.model.MDictModel import MDict
        from management_server.model.WithDrawGroupModel import WithDrawGroup
        cur_work_group = MDict.query.filter_by(MDICT_ID='28').with_for_update().first()
        cur_group_id = int(cur_work_group.CONTENT)
        next_group = WithDrawGroup.query.filter(WithDrawGroup.ID > cur_group_id).first()
        if not next_group:
            next_group = WithDrawGroup.query.first()
        if not next_group:
            return jsonify({'code': 50002, 'message': "withdraw error, please contact the manager."})
        next_group_id = next_group.ID

        agent.SURPLUS_MONEY = float(agent.SURPLUS_MONEY or 0) - float(money)

        the_withdraw = WithDraw(WITHDRAWAL_ID=str(uuid.uuid4()).replace("-", ""), USER_ID=g.user.AGENT_CODE,
                                NICK_NAME=agent.AGENT_NAME, MONEY=money, IS_PAY="0", CREATOR=g.user.ACCOUNT,
                                PAY_TYPE="1", Work_Group=next_group_id)
        db.session.add(the_withdraw)

        the_withdraw.BEFORE_MONEY = before_amount
        the_withdraw.AFTER_MONEY = float(agent.SURPLUS_MONEY)
        db.session.commit()

        app_opt.send({
            "user_account": agent.AGENT_CODE,
            "user_name": agent.AGENT_NAME,
            "type": AppOpType.WITHDRAW,
            "amount": before_amount,
            "balance": float(agent.SURPLUS_MONEY),
            "source_id": the_withdraw.WITHDRAWAL_ID
        })

        user_opt.send({
            "operate": "发起代理提现",
            "route": "结算管理",
            "key_word": the_withdraw.WITHDRAWAL_ID,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "提交成功"})
    except Exception as e:
        print("add_agent_withdraw error", e)
        return jsonify({'code': 50001, 'message': "未知错误"})


@withdraw.route('/agent_deal', methods=['POST'])
@auth.login_required
def deal_agent_withdraw():
    """
            提现处理
            @@@
            #### Args:
                    withdraw_id = ""
                    deal_opt = 1:结算 0:否决
            #### Returns::
                    {'code': 20000, 'message': "修改成功"}
                    {'code': 50001, 'message': "未知错误"}
        """
    args = request.get_json()
    withdraw_id = args.get('withdraw_id')
    deal_opt = args.get('deal_opt')
    print("<<<调用代理提现功能>>> 参数为:", request.args, "用户id:", g.user.ID)
    the_withdraw = WithDraw.query.filter_by(WITHDRAWAL_ID=withdraw_id).one_or_none()
    if not the_withdraw:
        return jsonify({'code': 50002, 'message': "withdraw not exist."})
    if not the_withdraw.PAY_TYPE == "1":
        return jsonify({'code': 50002, 'message': "This is not a agent withdraw."})
    if the_withdraw.IS_PAY != "0":
        return jsonify({'code': 50002, 'message': "This withdraw has been dealt."})
    agent = Agent.query.get({'AGENT_CODE': the_withdraw.USER_ID})

    repeat_key = "agent_withdraw_%s" % json.dumps(args)
    if Redis.get(repeat_key):
        return jsonify({'code': 50002, 'message': "Too many operations. Please wait."})
    Redis.set(repeat_key, 1, ex=2)

    if deal_opt == 1:
        agent.CASH_MONEY = float(agent.CASH_MONEY or 0) + float(the_withdraw.MONEY)
        the_withdraw.IS_PAY = 1
        db.session.commit()
    else:
        # 退回提现时 需要将扣掉的钱退回
        before_amount = float(agent.SURPLUS_MONEY or 0)
        agent.SURPLUS_MONEY = float(agent.SURPLUS_MONEY or 0) + float(the_withdraw.MONEY)
        the_withdraw.IS_PAY = 2
        # 重置提现的after_money
        the_withdraw.AFTER_MONEY = the_withdraw.BEFORE_MONEY

        db.session.commit()

        app_opt.send({
            "user_account": agent.AGENT_CODE,
            "user_name": agent.AGENT_NAME,
            "type": AppOpType.WITHDRAW,
            "amount": before_amount,
            "balance": float(agent.SURPLUS_MONEY),
            "source_id": the_withdraw.WITHDRAWAL_ID
        })

    user_opt.send({
        "operate": "结算提现",
        "route": "结算管理",
        "key_word": the_withdraw.WITHDRAWAL_ID,
        "user": g.user.ACCOUNT
    })

    return jsonify({'code': 20000, 'message': "修改成功", 'info': agent.to_dict()})


@withdraw.route('/app_user_deal', methods=['POST'])
@auth.login_required
def deal_app_user_withdraw():
    """
            提现处理
            @@@
            #### Args:
                    withdraw_id = ""
                    deal_opt = 1:结算 0:否决
                    remark = ""
            #### Returns::
                    {'code': 20000, 'message': "修改成功"}
                    {'code': 50001, 'message': "未知错误"}
        """
    args = request.get_json()
    withdraw_id = args.get('withdraw_id')
    deal_opt = args.get('deal_opt')
    remark = args.get("remark")
    print("<<<调用用户提现功能>>> 参数为:", request.get_json(), "用户id:", g.user.ID)
    the_withdraw = WithDraw.query.filter_by(WITHDRAWAL_ID=withdraw_id).one_or_none()
    if not the_withdraw:
        return jsonify({'code': 50002, 'message': "withdraw not exist."})
    if not the_withdraw.PAY_TYPE == "2":
        return jsonify({'code': 50002, 'message': "This is not a app user withdraw."})
    if the_withdraw.IS_PAY != "0":
        return jsonify({'code': 50002, 'message': "This withdraw has been dealt."})

    db.session.commit()
    user = AppUser.query.filter_by(OPENID=the_withdraw.USER_ID).one_or_none()
    if not user:
        return jsonify({'code': 50002, 'message': "App user not exist."})
    main_id = user.MAJUSER_ID
    del user
    user = AppUser.query.filter_by(MAJUSER_ID=main_id).with_for_update().first()
    the_withdraw.OPERATOR = g.user.ACCOUNT
    the_withdraw.REMARK = remark

    repeat_key = "user_withdraw_%s" % json.dumps(args)
    if Redis.get(repeat_key):
        return jsonify({'code': 50002, 'message': "Too many operations. Please wait."})
    Redis.set(repeat_key, 1, ex=2)

    if deal_opt == 1:
        if user.AGENT_ID:
            if not g.user.AGENT_CODE or user.AGENT_ID != g.user.AGENT_CODE:
                return jsonify({'code': 50003, 'message': "You are not the agent of this user."})
            # 代理处理会员提现时 需要增加代理余额(若有)
            agent = Agent.query.filter(Agent.AGENT_CODE == g.user.AGENT_CODE).with_for_update().first()
            agent_before = agent.SURPLUS_MONEY
            agent.SURPLUS_MONEY = float(agent.SURPLUS_MONEY) + float(the_withdraw.MONEY)

            app_opt.send({
                "user_account": agent.AGENT_CODE,
                "user_name": agent.AGENT_NAME,
                "type": AppOpType.WITHDRAW,
                "amount": agent_before,
                "balance": float(agent.SURPLUS_MONEY),
                "source_id": the_withdraw.WITHDRAWAL_ID
            })
        the_withdraw.IS_PAY = 1
        user.CASH_MONEY = float(user.CASH_MONEY) + float(the_withdraw.MONEY)
        db.session.commit()
    else:

        if user.AGENT_ID:
            if not g.user.AGENT_CODE or user.AGENT_ID != g.user.AGENT_CODE:
                return jsonify({'code': 50003, 'message': "You are not the agent of this user."})

        # 退回提现时 需要将扣掉的钱退回
        before_amount = float(user.TOTAL_MONEY or 0)

        after_amount = before_amount + float(the_withdraw.MONEY)
        user.TOTAL_MONEY = after_amount

        # 重置提现的after_money
        the_withdraw.AFTER_MONEY = the_withdraw.BEFORE_MONEY

        the_withdraw.IS_PAY = 2
        db.session.commit()

        app_opt.send({
            "user_account": user.OPENID,
            "user_name": user.NICK_NAME,
            "work_group": the_withdraw.Work_Group,
            "type": AppOpType.WITHDRAW,
            "amount": before_amount,
            "balance": float(user.TOTAL_MONEY),
            "source_id": the_withdraw.WITHDRAWAL_ID
        })

    user_opt.send({
        "operate": "结算提现",
        "route": "结算管理",
        "key_word": the_withdraw.WITHDRAWAL_ID,
        "user": g.user.ACCOUNT
    })

    return jsonify({'code': 20000, 'message': "修改成功", 'info': user.to_dict()})
