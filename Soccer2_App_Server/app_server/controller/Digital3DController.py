from flask import g, request, jsonify, Blueprint
from app_server.utils.OrmUttil import AppOpType
from app_server.model.Digital3DModel import Digital3D, Digit3DStatus
from app_server.model.OrderModel import Order, OrderType
from app_server.utils.OrmUttil import set_field
from app_server import auth, db, app_opt
from sqlalchemy import func
import ipaddress
import datetime
import uuid
import math
import time

digital_3d = Blueprint('digital_3d', __name__)


# 获取订单列表
@digital_3d.route('', methods=['GET'])
# @auth.login_required
def get_digital_3d_list():
    """
                    @@@
                    #### Args:
                           {
                                page: 1,
                                limit: 20,
                                filter: {},
                                start_time: "2021-09-10",
                                end_time: "2021-09-12",
                            }
                    #### Returns::
                            {
                                'code': 20000,
                                'items': [u.to_dict() for u in digit3d_list],
                            }
                """
    page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)
    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    status = request.args.get('status')
    print("----", status)

    try:

        digit3d_list = Digital3D.query

        if start_time:
            digit3d_list = digit3d_list.filter(db.cast(Digital3D.CREATE_TIME, db.Date) >= start_time)

        if end_time:
            digit3d_list = digit3d_list.filter(db.cast(Digital3D.CREATE_TIME, db.Date) <= end_time)

        if key_word:
            digit3d_list = digit3d_list.filter(Digital3D.STAGE.like('%{}%'.format(key_word)))

        if status:
            digit3d_list = digit3d_list.filter(Digital3D.STATUS == status)

        total = digit3d_list.count()

        digit3d_list = digit3d_list.offset((page - 1) * limit).limit(limit).all()

        return jsonify({
            'code': 20000,
            'message': 'success',
            'items': [u.to_dict() for u in digit3d_list],
            'totalCount': total,
            'TotalPageCount': math.ceil(int(total / limit))
        })
    except Exception as e:
        print("get_digit_list error:", e)

    return jsonify({'code': 50001, 'message': "unknown error."})


# 获取订单列表
@digital_3d.route('/get_actvie_nper', methods=['GET'])
@auth.login_required
def get_active_stage():
    today_digit = Digital3D.query.filter(Digital3D.STATUS == Digit3DStatus.Opened,
                                         db.cast(Digital3D.OPEN_TIME, db.Date) == datetime.date.today()).order_by(
        Digital3D.STAGE.desc()).first()

    # 查询最近30期的开奖结果
    seven_day_pass = datetime.datetime.strptime(
        "%s 00:00:00" % (datetime.datetime.today() - datetime.timedelta(days=7)).date(), "%Y-%m-%d %H:%M:%S").date()
    digital_3d_list = Digital3D.query.filter(db.cast(Digital3D.OPEN_TIME, db.Date) >= seven_day_pass).order_by(
        Digital3D.CREATE_TIME.desc()).all()
    result = []
    if len(digital_3d_list) > 0:
        for temp in digital_3d_list:
            if temp.STATUS == 3:
                temp = temp.to_dict()
                result.append({
                    'OPEN_TIME': temp['OPEN_TIME'],
                    'RESULT': temp['RESULT'],
                    'STAGE': temp['STAGE'],
                })

    if today_digit:
        digit = today_digit.to_dict()
        digit = {
            'CLOSE_TIME': digit['CLOSE_TIME'],
            'ID': digit['ID'],
            'ODDS': digit['ODDS'],
            'SINGLE_MAX': digit['SINGLE_MAX'],
            'SINGLE_MIN': digit['SINGLE_MIN'],
            'STAGE': digit['STAGE'],
        }
        return jsonify({
            'code': 20000,
            'item': digit,
            'results': result,
        })
    else:
        return jsonify({
            'code': 50001,
            'results': result,
            'message': 'there is no active stage',
        })


# 获取订单列表
@digital_3d.route('/bet', methods=['POST'])
@auth.login_required
def digital_3d_bet():
    """
                @@@
                #### Args:
                        bets:[
                            {
                                matchId:
                                attrType:
                                betType:
                            }
                        ]
                        totalAmount
                #### Returns::
                        {'code': 20000, 'message': "Bet success!"}
                        {'code': 50001, 'message': "unknown error"}
            """
    args = request.get_json()
    bet_list = args.get('bets')
    match_id = int(args.get('match_id'))
    new_orders = []
    user_info = g.user
    try:
        order_id = "%s-%s" % (user_info.USER_ID, round(time.time() * 1000))
        digit_stage = Digital3D.query.filter_by(ID=match_id).one_or_none()

        if len(bet_list) == 0:
            return jsonify({
                'code': 50002, 'message': "Bet failed: no order."
            })
        if not digit_stage:
            return jsonify({
                'code': 50004, 'message': "Bet failed."
            })
        if digit_stage.STATUS != Digit3DStatus.Opened:
            return jsonify({
                'code': 50005, 'message': "Bet failed."
            })
        if digit_stage.CLOSE_TIME <= datetime.datetime.now():
            return jsonify({
                'code': 50006, 'message': "Bet failed."
            })

        # 统计总数字与总下注额
        limit_num = digit_stage.LIMIT_NUM
        num_user_limit = digit_stage.NUM_USER_LIMIT

        stage_total = Order.query.with_entities(func.sum(Order.BET_MONEY)).filter(
            Order.MATCH_ID == match_id,
            Order.ORDER_TYPE == OrderType.Digit).scalar() or 0

        # 此用户单数字下注额
        num_per_user_count = Order.query.with_entities(Order.BET_TYPE, func.sum(Order.BET_MONEY)).filter(
            Order.MATCH_ID == match_id, Order.USER_ID == g.user.OPENID,
            Order.ORDER_TYPE == OrderType.Digit).group_by(Order.BET_TYPE).all()
        num_per_user_count = {o[0]: int(o[1]) for o in num_per_user_count}

        # 单数字总下注额
        per_num_count = Order.query.with_entities(Order.BET_TYPE, func.sum(Order.BET_MONEY)).filter(
            Order.MATCH_ID == match_id, Order.ORDER_TYPE == OrderType.Digit).group_by(Order.BET_TYPE).all()
        per_num_count = {o[0]: int(o[1]) for o in per_num_count}

        total = 0
        for bet in bet_list:
            total += int(bet['BET_MONEY'])

        if total + stage_total >= digit_stage.LIMIT_CODE * limit_num:
            limit_num += digit_stage.EX_LIMIT

        code = 0
        message = ''
        error_bet = []
        limit_amount = 0
        for bet in bet_list:
            bet_money = int(bet['BET_MONEY'])

            n_p_u = num_per_user_count.get(bet['BET_TYPE']) or 0
            num_sum = per_num_count.get(bet['BET_TYPE']) or 0

            # 单个数字总限额
            if bet_money + num_sum > limit_num:
                code = 50003
                message = 'exceeded max bet limit'
                error_bet.append(bet['BET_TYPE'])
                continue

            # 单个数字单个用户总限额
            if bet_money + n_p_u > num_user_limit:
                code = 50003
                message = 'exceeded max bet per user'
                error_bet.append(bet['BET_TYPE'])
                continue

            # 限额相关
            if bet_money < digit_stage.SINGLE_MIN:
                code = 50006
                message = "min bet"
                limit_amount = digit_stage.SINGLE_MIN
                continue

            if bet_money > digit_stage.SINGLE_MAX:
                code = 50006
                message = "max bet"
                limit_amount = digit_stage.SINGLE_MAX
                continue

        if float(total) > float(user_info.TOTAL_MONEY):
            return jsonify({
                'code': 50006, 'message': "Sorry, your credit is not enough"
            })

        # 用户本场总额
        user_stage_total = Order.query.with_entities(func.sum(Order.BET_MONEY)).filter(
            Order.USER_ID == g.user.OPENID,
            Order.MATCH_ID == match_id, Order.ORDER_TYPE == OrderType.Digit).scalar() or 0

        if float(total) + user_stage_total > digit_stage.USER_MAX:
            code = 50006
            message = "exceeded max bet per stage"
            limit_amount = digit_stage.USER_MAX

        # 往上扩展后，仍旧大于限额
        if total + stage_total > digit_stage.LIMIT_CODE * limit_num:
            code = 50006
            message = "stage total limit exceeded"
            limit_amount = digit_stage.LIMIT_CODE * limit_num

        error_bet_str = ''
        for key, value in enumerate(error_bet):
            if key == 0:
                error_bet_str = value
            else:
                error_bet_str = error_bet_str + '-' + value

        if code != 0:
            result = {
                'code': code,
                'message': message,
                'error_bet': error_bet_str,
                'limit_amount': limit_amount
            }
            return jsonify(result)

        is_mix = len(bet_list) > 1
        for bet in bet_list:
            new_order = Order(ID=str(uuid.uuid4()).replace("-", ""), ORDER_ID=order_id, ORDER_TYPE='8', STATUS="1",
                              MATCH_ID=digit_stage.ID, USER_ID=user_info.OPENID, USER_NAME=user_info.NICK_NAME,
                              BET_ODDS=digit_stage.ODDS, IS_MIX=is_mix,
                              MATCH_TIME=digit_stage.CLOSE_TIME, ORDER_DESC=digit_stage.STAGE,
                              IP=int(ipaddress.IPv4Address(request.remote_addr)))
            set_field(new_order, bet)
            print(type(bet))
            db.session.add(new_order)
            new_orders.append(new_order)

            before_amount = float(g.user.TOTAL_MONEY)
            after_amount = before_amount - float(bet['BET_MONEY'])
            user = g.user
            main_id = user.MAJUSER_ID
            del user
            from app_server.model.AppUserModel import AppUser
            user = AppUser.query.filter_by(MAJUSER_ID=main_id).with_for_update().first()
            user.TOTAL_MONEY = after_amount
            db.session.commit()
            app_opt.send({
                "user_account": g.user.OPENID,
                "user_name": g.user.NICK_NAME,
                "type": AppOpType.BET,
                "amount": before_amount,
                "balance": float(g.user.TOTAL_MONEY),
                "source_id": order_id,
                "is_digit": True,
                "match_id": digit_stage.ID
            })
        digit_stage.BET_NUM += len(bet_list)
        digit_stage.BET_SUM += total

        # 提升限额
        digit_stage.LIMIT_NUM = limit_num

        db.session.commit()
        # print([u.to_dict() for u in new_orders])

        return jsonify({
            'code': 20000,
            'message': 'bet success!',
            'total_money': str(user.TOTAL_MONEY)
            # 'order': [u.to_dict() for u in new_orders],
            # 'match': digit_stage.to_dict(),
        })
    except Exception as e:
        print("digital_3d bet error", e)
        db.session.rollback()
        for order in new_orders:
            db.session.delete(order)
        db.session.commit()
        return jsonify({'code': 50001, 'message': "unknown error"})


@digital_3d.route('/get_detail', methods=['GET'])
@auth.login_required
def get_digital_3d_detail():
    """
                @@@
                #### Args:
                        current_page = request.args.get('page', type=int, default=1)
                        limit = request.args.get('limit', type=int, default=20)
                        order_id = request.args.get('order_id')

                        key_word = request.args.get('key_word')
                        start_time = request.args.get('start_time')
                        end_time = request.args.get('end_time')

                        order_type = request.args.get('order_type')    订单类型:1胜负(让球)2大小球3波胆 无参表示全部
                        order_types = request.args.get('order_types')  订单类型多选
                        bet_type = request.args.get('bet_type')        下注类型:1主胜,2客胜   无参表示全部
                        status = request.args.get('status')            订单状态:0无效,1有效   无参表示全部
                        is_win = request.args.get('is_win')            订单结果:0、输，1、赢,  2未出结果    无参表示全部
                #### Returns::
                        {
                            'code': 20000,
                            'items': [u.to_dict() for u in order_list],
                            'total': total,
                            'total_bet': total_bet,       下注总金额
                            'total_bonus': total_bonus    总奖金
                        }
            """

    match_id = request.args.get('match_id')
    order_list = Order.query.filter(Order.STATUS == "1")

    digit_stage = Digital3D.query.filter_by(ID=match_id).first()

    if match_id:
        order_list = order_list.filter(Order.MATCH_ID == match_id)

    order_list = order_list.filter(Order.ORDER_TYPE == '8')

    order_list = order_list.group_by(Order.BET_TYPE)
    _sum = Order.query.filter(Order.ORDER_TYPE == '8',
                              Order.MATCH_ID == match_id).with_entities(Order.BET_TYPE,
                                                                        func.sum(Order.BET_MONEY)).group_by(
        Order.BET_TYPE).all()

    order_list = order_list.all()

    result = []
    sum_dict = {}

    for bet_type, bet_money in _sum:
        # print("---", type(bonus), type(bet_money), type(id_win))
        sum_dict[bet_type] = {
            "BET_MONEY": str(bet_money),
            "LIMIT_NUM": digit_stage.LIMIT_NUM
        }
    for u in order_list:
        temp = u.to_dict()
        if u.BET_TYPE in sum_dict:
            temp.update(sum_dict[u.BET_TYPE])
        result.append(temp)
    total = len(result)
    # print("the ret:", [u.to_dict() for u in order_list])

    return jsonify({
        'code': 20000,
        'items': result,
        'total': total
    })
