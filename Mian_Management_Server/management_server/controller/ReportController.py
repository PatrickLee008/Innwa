import calendar
import functools
from management_server.utils.sphinxapi import *
from management_server import auth
from management_server.model.OrderModel import Order
from flask import g, request, jsonify, Blueprint
from management_server.model.SysUserModel import SysUser
from management_server.model.AppUserModel import AppUser
from management_server.model.ChargeModel import Charge
from management_server.model.WithDrawModel import WithDraw
from management_server.model.ReportHistoryModel import ReportHistory
from management_server.model import GameType
from sqlalchemy import or_, func, and_
import threading
import datetime
import time

report = Blueprint('report', __name__)
lock = threading.Lock()


@report.route('/user_count', methods=['GET'])
def get_user_count():
    user = AppUser.query

    user_count = user.with_entities(func.count(AppUser.MAJUSER_ID)).scalar()  # 总用户数

    now = datetime.datetime.now()
    today = now.date()

    # 活跃用户数(三天内有订单的用户) ,然后根据用户分组
    three_days_before = datetime.date.today() - datetime.timedelta(days=3)

    start = time.time()

    orders = Order.query
    orders_three_day = orders.filter(and_(Order.CREATE_TIME >= three_days_before, Order.CREATE_TIME <= now)).group_by(
        Order.USER_ID)  # 三天内下单的用户数

    user_active_count = len(orders_three_day.all())
    print("活跃用户查询耗时:", time.time() - start)
    start = time.time()

    month_start = datetime.date(now.year, now.month, 1)
    wday, month_range = calendar.monthrange(now.year, now.month)  # 得到本月的天数 第一返回为月第一日为星期几（0-6）, 第二返回为此月天数
    month_end = datetime.date(now.year, now.month, month_range)

    orders_today = orders.filter(Order.CREATE_TIME >= today).all()
    orders_today_sum = 0
    orders_today_count = len(orders_today)
    print("订单总数:", orders_today_count)
    user_today_bet = set()
    for order in orders_today:
        orders_today_sum += float(order.BET_MONEY)
        user_today_bet.add(order.USER_ID)
    user_today_bet = len(list(user_today_bet))
    print("今日下注用户数:", time.time() - start)

    start = time.time()

    user_month = user.filter(and_(AppUser.CREAT_TIME >= month_start, AppUser.CREAT_TIME <= month_end))
    user_month_count = user_month.with_entities(func.count(AppUser.MAJUSER_ID)).scalar()  # 本月新增用户数
    user_today = user.filter(AppUser.CREAT_TIME >= today)
    user_today_count = user_today.with_entities(func.count(AppUser.MAJUSER_ID)).scalar()  # 今日新增用户数

    print("本月新增用户数查询耗时:", time.time() - start)

    return jsonify({'code': 20000, 'user_today_bet': user_today_bet, 'orders_today_sum': orders_today_sum,
                    'orders_today_count': orders_today_count,
                    'user_active_count': user_active_count,
                    'user_today_count': user_today_count, 'user_count': user_count,
                    'user_month_count': user_month_count})


# 查询用户盈利报表
@report.route('/user_benefit_report', methods=['GET'])
@auth.login_required
def get_user_benefit_report():
    """
        @@@
        #### Args:
                current_page = request.args.get('page', type=int, default=1)
                limit = request.args.get('limit', type=int, default=20)
                start_time = request.args.get('start_time')
                end_time = request.args.get('end_time')
                sort_key = request.args.get('sort_key')  既返回值中的key 如: benefit_percent, win_percent
        #### Returns::
                {
                    'code': 20000,
                    'items': result,
                    'total': len(li),
                }
    """
    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    sort_key = request.args.get('sort_key')
    t1 = time.time()

    charges = Charge.query
    withdraws = WithDraw.query

    def compare_by_key(a, b):
        if a[sort_key] == b[sort_key]:
            return 0
        return -1 if a[sort_key] > b[sort_key] else 1

    cl = SphinxClient()
    cl.SetServer('localhost', 9312)
    cl.SetConnectTimeout(10.0)
    cl.SetSortMode(SPH_SORT_ATTR_ASC, "id")
    query_str = ""

    if start_time:
        start_time += '00:00:00'

        print("got to filter:", start_time)
        withdraws = withdraws.filter(WithDraw.CREATE_TIME >= start_time)
        charges = charges.filter(Charge.CREATOR_TIME >= start_time)
        # sphinx 部分
        now_ts = int(time.time())
        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

        start_time = int(start_time.timestamp())
        print("ranging:", start_time, now_ts)
        cl.SetFilterRange('CREATE_TIME', start_time, now_ts)

    if end_time:
        end_time += '23:59:59'
        # end_time延后一日
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

        withdraws = withdraws.filter(WithDraw.CREATE_TIME <= end_time)
        charges = charges.filter(Charge.CREATOR_TIME <= end_time)
        # sphinx 部分
        end_time = int(end_time.timestamp())
        cl.SetFilterRange('CREATE_TIME', start_time or 0, end_time)

    if g.user.is_agent():
        agent_accounts = SysUser.query.filter_by(AGENT_CODE=g.user.AGENT_CODE).all()
        agent_accounts = {a.ACCOUNT for a in agent_accounts}

        charges = charges.filter(Charge.CREATOR.in_(agent_accounts))
        withdraws = withdraws.filter(WithDraw.OPERATOR.in_(agent_accounts))
        # 过滤代理订单
        query_str = "@AGENT_CODE %s" % g.user.AGENT_CODE

    user_charges = charges.with_entities(Charge.USER_ID, func.sum(Charge.MONEY)).group_by(Charge.USER_ID).all()
    user_withdraws = withdraws.with_entities(WithDraw.USER_ID, func.sum(WithDraw.MONEY)).group_by(WithDraw.USER_ID).all()
    user_charges = {c[0]: c[1] for c in user_charges}
    user_withdraws = {c[0]: c[1] for c in user_withdraws}

    # 切换为sphinx统计
    cl.SetGroupBy('ORDER_GROUP', SPH_GROUPBY_ATTR, 'id asc')
    res = cl.Query('', 'order_history;order_history_add')
    total_found = res['total_found']
    print("what have you found?", total_found)
    if total_found:
        cl.SetLimits(0, total_found, total_found)

    res = cl.Query(query_str, 'order_history;order_history_add')
    user_orders = {}
    for o in res['matches']:
        # print(o)
        u_key = o['attrs']['u_id']
        if u_key not in user_orders:
            user_orders[u_key] = {'uid': u_key, 'total_bet': 0, 'total_bonus': 0, 'order_count': 0, 'max_benefit': 0, 'benefit_percent': 0.0, 'win_percent': 0.0, 'win_count': 0}
            if u_key in user_charges:
                user_orders[u_key]['total_charge'] = user_charges[u_key]
            if u_key in user_withdraws:
                user_orders[u_key]['total_withdraw'] = user_withdraws[u_key]

        user_orders[u_key]['total_bet'] += o['attrs']['bet_money']
        user_orders[u_key]['total_bonus'] += o['attrs']['bonus']
        user_orders[u_key]['order_count'] += 1
        if o['attrs']['is_win']:
            user_orders[u_key]['win_count'] += 1
        user_orders[u_key]['benefit_percent'] = user_orders[u_key]['total_bonus'] / user_orders[u_key]['total_bet']
        user_orders[u_key]['win_percent'] = user_orders[u_key]['win_count'] / user_orders[u_key]['order_count']

        if o['attrs']['bonus'] > user_orders[u_key]['max_benefit']:
            user_orders[u_key]['max_benefit'] = o['attrs']['bonus']

    print("....", len(res['matches']), len(user_orders), time.time() - t1)
    # 转换为列表
    li = list(user_orders.values())
    li = sorted(li, key=functools.cmp_to_key(compare_by_key))
    print(li[:20], len(li))
    right = current_page * limit
    result = li[(current_page - 1) * limit: min(right, len(li))]

    print("统计总耗时:", time.time() - t1)
    return jsonify({
        'code': 20000,
        'items': result,
        'total': len(li),
    })


# 查询总报表
@report.route('/total_report', methods=['GET'])
@auth.login_required
def get_total_report():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    report_list = ReportHistory.query
    # 游戏类型 0:所有 1:比赛 2:数字
    game_type = request.args.get('game_type', type=int, default=1)

    if game_type:
        if game_type == GameType.Match:
            report_list = report_list.filter(ReportHistory.game_type != GameType.Digit)
        if game_type == GameType.Digit:
            report_list = report_list.filter(ReportHistory.game_type == GameType.Digit)

    if start_time:
        report_list = report_list.filter(ReportHistory.report_date >= start_time)

    if end_time:
        report_list = report_list.filter(ReportHistory.report_date <= end_time)
    total_bet, company_profit, charge_sum, withdraw_sum, platform_commission, user_active_count, user_sum = report_list.with_entities(func.sum(ReportHistory.bet_money_total),
                                                                                                                                      func.sum(ReportHistory.benefit_total),
                                                                                                                                      func.sum(ReportHistory.charge_total),
                                                                                                                                      func.sum(ReportHistory.withdraw_total),
                                                                                                                                      func.sum(ReportHistory.commission_total),
                                                                                                                                      func.sum(ReportHistory.user_active_count),
                                                                                                                                      func.sum(ReportHistory.new_user_count)).one_or_none()
    print("---", type(total_bet))
    if total_bet:
        return jsonify({
            'code': 20000,
            'bet_sum': int(total_bet),
            'company_profit': int(company_profit),
            'charge_sum': int(charge_sum),
            'withdraw_sum': int(withdraw_sum),
            'platform_commission': int(platform_commission),
            'user_active_count': int(user_active_count),
            'user_sum': int(user_sum)
        })
    else:
        return jsonify({
            'code': 20000,
            'bet_sum': 0,
            'company_profit': 0,
            'charge_sum': 0,
            'withdraw_sum': 0,
            'platform_commission': 0,
            'user_active_count': 0,
            'user_sum': 0,
        })

