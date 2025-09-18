import time
from sqlalchemy import or_, func
from management_server import app, db, auth, user_opt
from management_server.model.AppUserModel import AppUser
from management_server.model.SettleMentModel import Settlement
from flask import g, request, jsonify, Blueprint
from datetime import datetime

settlement = Blueprint('settlement', __name__)


# 获取订单列表
@settlement.route('/get', methods=['GET'])
@auth.login_required
def get_settlement_list():
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

    settlement_list = Settlement.query.order_by(Settlement.CREATE_TIME.desc())

    if g.user.AGENT_CODE:
        users_under = AppUser.query.filter_by(AGENT_ID=g.user.AGENT_CODE).all()
        users_under = set([u.USER_ID for u in users_under])
        settlement_list = settlement_list.filter(Settlement.USER_ID.in_(users_under))

    if key_word:
        settlement_list = settlement_list.filter(
            or_(Settlement.TRAN_ID.like('%{}%'.format(key_word)),Settlement.USER_ID.like('%{}%'.format(key_word)), Settlement.MATCH_ID.like('%{}%'.format(key_word))))

    if start_time:
        start_time += " 00:00:00"
        settlement_list = settlement_list.filter(Settlement.CREATE_TIME >= start_time)

    if end_time:
        end_time += " 23:59:59"
        settlement_list = settlement_list.filter(Settlement.CREATE_TIME <= end_time)

    total_bet = '%.2f' % (settlement_list.with_entities(func.sum(Settlement.TRAN_MONEY)).scalar() or 0)
    bonus = '%.2f' % (settlement_list.with_entities(func.sum(Settlement.BONUS)).scalar() or 0)
    benefit = '%.2f'  % (settlement_list.with_entities(func.sum(Settlement.AGENT_PROFIT_MONEY)).scalar() or 0)

    total = settlement_list.count()

    settlement_list = settlement_list.offset((current_page - 1) * limit).limit(limit).all()

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in settlement_list],
        'total_bet': total_bet,
        'bonus': bonus,
        'benefit': benefit,
        'total': total
    })
