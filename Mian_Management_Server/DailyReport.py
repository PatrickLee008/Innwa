from management_server import db
from sqlalchemy import func, and_
from management_server.model.SettleMentModel import Settlement
from management_server.model.ChargeModel import Charge
from management_server.model.WithDrawModel import WithDraw
from management_server.model.AppUserModel import AppUser
from management_server.model.ReportHistoryModel import ReportHistory
from management_server.model.OrderModel import OrderType
from management_server.model import GameType
from management_server.utils.sphinxapi import *
import datetime


def calculate_report():
    last_cal_date = "2021-03-01"
    # last_report = ReportHistory.query.order_by(ReportHistory.report_date.desc()).first()
    # if last_report:
    #     last_cal_date = str(last_report.report_date)
    all_reported_date = ReportHistory.query.with_entities(ReportHistory.report_date).all()
    all_reported_date = {str(u[0]) for u in all_reported_date}
    start_date = datetime.datetime.strptime(last_cal_date, '%Y-%m-%d')
    end_date = datetime.datetime.today()
    while start_date <= end_date:
        print("comparing:", start_date)
        if str(start_date.date()) not in all_reported_date or ((end_date - start_date).days < 4):
            is_old = False
            if (end_date - start_date).days < 4:
                print("???")
                is_old = True
            daily_cal(start_date, is_old)
        start_date += datetime.timedelta(days=1)


def daily_cal(date, is_old=False):
    start_time = date
    end_time = date + datetime.timedelta(days=1)
    withdraw_list = WithDraw.query
    charge_list = Charge.query
    new_user_query = AppUser.query
    settlements = Settlement.query

    withdraw_list = withdraw_list.filter(db.cast(WithDraw.CREATE_TIME, db.Date) >= start_time, db.cast(WithDraw.CREATE_TIME, db.Date) < end_time)
    charge_list = charge_list.filter(db.cast(Charge.CREATOR_TIME, db.Date) >= start_time, db.cast(Charge.CREATOR_TIME, db.Date) < end_time)
    new_user_query = new_user_query.filter(db.cast(AppUser.CREAT_TIME, db.Date) >= start_time, db.cast(AppUser.CREAT_TIME, db.Date) < end_time)
    settlements = settlements.filter(db.cast(Settlement.CREATE_TIME, db.Date) >= start_time, db.cast(Settlement.CREATE_TIME, db.Date) < end_time)
    start_ts = int(start_time.timestamp())
    end_ts = int(end_time.timestamp())

    cl = SphinxClient()
    cl.SetServer('localhost', 9312)
    cl.SetSortMode(SPH_SORT_ATTR_DESC, "id")
    cl.SetFilterRange('CREATE_TIME', start_ts, end_ts)

    cl.SetGroupBy('ORDER_GROUP', SPH_GROUPBY_ATTR, 'id desc')
    order_res = cl.Query("", 'order_history;order_history_add')

    total_benefit_match = 0
    total_bet_match = 0

    total_benefit_digit = 0
    total_bet_digit = 0
    if order_res and order_res['total_found']:
        cl.SetLimits(0, order_res['total_found'], order_res['total_found'])
        order_res = cl.Query("", 'order_history;order_history_add')
        for o in order_res['matches']:
            if o['attrs']['order_type'] == 8:
                total_bet_digit += o['attrs']['bet_money']
                total_benefit_digit += o['attrs']['bet_money'] - o['attrs']['bonus']
            else:
                total_bet_match += o['attrs']['bet_money']
                total_benefit_match += o['attrs']['bet_money'] - o['attrs']['bonus']
    # sphinx统计活跃用户
    user_active_count = 0
    cl.SetGroupBy('U_ID', SPH_GROUPBY_ATTR, 'id asc')
    res = cl.Query("", 'order_history;order_history_add')
    if res and res['total_found']:
        total_found = res['total_found']
        cl.SetLimits(0, total_found, total_found)
        res = cl.Query("", 'order_history;order_history_add')
        user_active_count = res['total_found']

    user_sum = AppUser.query.with_entities(func.count(AppUser.USER_ID)).scalar() or 0
    withdraw_total = withdraw_list.with_entities(func.sum(WithDraw.MONEY)).filter(WithDraw.IS_PAY == "1").scalar() or 0
    charge_total = charge_list.with_entities(func.sum(Charge.MONEY)).scalar() or 0
    new_user_count = new_user_query.with_entities(func.count(AppUser.USER_ID)).scalar() or 0

    platform_commission_match = settlements.filter(Settlement.ORDER_TYPE != OrderType.Digit).with_entities(func.sum(Settlement.AGENT_PROFIT_MONEY)).scalar() or 0
    platform_commission_digit = settlements.filter(Settlement.ORDER_TYPE == OrderType.Digit).with_entities(func.sum(Settlement.AGENT_PROFIT_MONEY)).scalar() or 0
    print("got:", total_benefit_match, platform_commission_match, total_bet_digit)

    report_history_match = ReportHistory(withdraw_total=withdraw_total, commission_total=platform_commission_match, game_type=GameType.Match,
                                         charge_total=charge_total, bet_money_total=total_bet_match, benefit_total=total_benefit_match, user_total=user_sum,
                                         user_active_count=user_active_count, new_user_count=new_user_count, report_date=start_time.date())

    report_history_digit = ReportHistory(withdraw_total=withdraw_total, commission_total=platform_commission_digit, game_type=GameType.Digit,
                                         charge_total=charge_total, bet_money_total=total_bet_digit, benefit_total=total_benefit_digit, user_total=user_sum,
                                         user_active_count=user_active_count, new_user_count=new_user_count, report_date=start_time.date())
    if is_old:
        old_match_report = ReportHistory.query.filter(ReportHistory.report_date == start_time.date(), ReportHistory.game_type == GameType.Match).first()
        old_digit_report = ReportHistory.query.filter(ReportHistory.report_date == start_time.date(), ReportHistory.game_type == GameType.Digit).first()
        if old_match_report:
            report_history_match.id = old_match_report.id
        if old_digit_report:
            report_history_digit.id = old_digit_report.id
    db.session.merge(report_history_match)
    db.session.merge(report_history_digit)

    db.session.commit()


if __name__ == '__main__':
    calculate_report()
