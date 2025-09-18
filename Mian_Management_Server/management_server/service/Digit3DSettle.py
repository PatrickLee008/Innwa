from management_server import app_opt, app
from management_server.model.Digital3DModel import Digital3D, Digit3DStatus
from management_server.model.OrderModel import Order
from management_server.model.AppUserModel import AppUser
from management_server.model.MDictModel import MDict
from management_server.model.SettleMentModel import Settlement
from management_server.model.MatchSettleModel import SettleType
from management_server.model.OrderHistoryModel import OrderHistory
from management_server.utils.OrmUttil import set_field
from management_server.model.AppOperationModel import AppOperation
from management_server.utils.OrmUttil import AppOpType2Name, AppOpType
from management_server.utils import get_session
from multiprocessing.dummy import Pool
from decimal import Decimal
from subprocess import Popen
import time
import uuid


class Digit3DSettle:
    def __init__(self, current_settle):
        self.current_settle = current_settle
        self.digit_id = current_settle.MATCH_ID
        self.com_ratio = None
        self.result = None
        self.odds = 0

    def execute(self):
        if self.current_settle.SETTLE_TYPE == SettleType.SETTLE:
            self.settle()
        elif self.current_settle.SETTLE_TYPE == SettleType.CANCEL:
            self.cancel()
        elif self.current_settle.SETTLE_TYPE == SettleType.REVERSE:
            self.reverse()

    def settle(self):
        print(self.current_settle)
        session = get_session()
        digit_id = self.digit_id

        # 佣金比例
        self.com_ratio = int(session.query(MDict).filter_by(MDICT_ID="102").one().CONTENT) * 0.01
        the_digit = session.query(Digital3D).filter_by(ID=self.digit_id).one_or_none()
        self.result = the_digit.RESULT
        self.odds = the_digit.ODDS
        order_q = session.query(Order).filter(Order.MATCH_ID == digit_id)
        # 更新订单比分结果
        order_q.update({Order.BET_HOST_TEAM_RESULT: the_digit.RESULT})
        session.commit()

        # # 查询所有单笔订单
        single_orders = order_q.filter(Order.STATUS != "0").all()
        print("got single orders:", single_orders)
        order_list = [u.to_cal() for u in single_orders]

        start = time.time()
        pool = Pool(10)
        # # 多进程结算
        comp_profits = pool.map(self.deal_order, order_list)

        end = time.time()
        print("---结算ID为:[", digit_id, "]的  3d数字盘 用时----:", end - start, "秒")
        com_benefit = 0
        for profit in comp_profits:
            com_benefit += profit
        the_digit.BENEFIT = the_digit.BENEFIT + com_benefit
        the_digit.STATUS = Digit3DStatus.Settled
        print("u r not dealing it ?!")
        session.commit()
        session.close()
        pool.close()
        pool.join()

        compile_popen = Popen(app.config['SPHINX_COMMAND'], shell=True)
        compile_popen.wait()
        print(compile_popen.stdout)

    def deal_order(self, order):
        session = get_session()
        order_win = int(order['BET_TYPE']) == self.result

        print("got order", order['ID'], "result:", order_win)
        bet_money = Decimal(order['BET_MONEY'])

        bonus = 0
        com_money = 0
        if order_win:
            bonus = bet_money * self.odds
            com_money = float(bonus - bet_money) * self.com_ratio

        order['BONUS'] = bonus
        order['IS_WIN'] = order_win
        order['IS_MIX'] = order['IS_MIX'] == "1"
        order['STATUS'] = False

        oh = order.copy()
        oh.pop('ID')
        # 转换到历史记录
        order_history = OrderHistory()
        set_field(order_history, oh)
        session.add(order_history)
        session.query(Order).filter_by(ID=order['ID']).delete()

        # 3.插入结算记录
        settlement = Settlement(ID=str(uuid.uuid4()).replace("-", ""), TRAN_ID=order['ORDER_ID'], USER_NICK_NAME=order['USER_NAME'],
                                USER_ID=order['USER_ID'], MATCH_ID=order['MATCH_ID'], ORDER_TYPE=order['ORDER_TYPE'], PROFIT_TYPE="2",
                                TRAN_MONEY=bet_money, TRAN_CONTENT=order['REMARK'], AGENT_PROFIT_BL=self.com_ratio, AGENT_PROFIT_MONEY=com_money, STATUS="1")
        session.add(settlement)

        # 用户信息加锁写入
        user = session.query(AppUser).filter_by(OPENID=order['USER_ID']).first()
        main_id = user.MAJUSER_ID
        user = None
        user = session.query(AppUser).filter_by(MAJUSER_ID=main_id).with_for_update().first()
        nick_name = user.NICK_NAME
        before_amount = Decimal(user.TOTAL_MONEY)
        after_amount = before_amount + bonus
        user.TOTAL_MONEY = after_amount
        session.commit()
        self.new_do_app_record(session, order['USER_ID'], nick_name, order['ID'], before_amount, after_amount)
        session.commit()

        session.close()

        com_profit = bet_money - bonus
        return com_profit

    def reverse(self):
        pass

    def cancel(self):
        pass

    @staticmethod
    def new_do_app_record(user_id, nick_name, order_id, before_amount, after_amount, opt_type=AppOpType.SETTLEMENT):
        app_opt.send({
            "user_account": user_id,
            "user_name": nick_name,
            "type": opt_type,
            "amount": before_amount,
            "balance": after_amount,
            "source_id": order_id,
            "is_digit": True
        })
