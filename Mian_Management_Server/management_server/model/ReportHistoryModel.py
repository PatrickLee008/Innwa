from management_server import db
from sqlalchemy import Column, DECIMAL, Date
from sqlalchemy.dialects.mysql import INTEGER, TINYINT


class ReportHistory(db.Model):
    __tablename__ = 'report_history'
    id = Column(INTEGER(unsigned=True), autoincrement=True, primary_key=True)
    charge_total = Column(DECIMAL(20, 2), nullable=False, server_default='0', comment="总充值")
    withdraw_total = Column(DECIMAL(20, 2), nullable=False, server_default='0', comment="总提现")

    bet_money_total = Column(DECIMAL(20, 2), nullable=False, server_default='0', comment="总下注")
    benefit_total = Column(DECIMAL(20, 2), nullable=False, server_default='0', comment="总收益")
    commission_total = Column(DECIMAL(20, 2), nullable=False, server_default='0', comment="总佣金")
    user_total = Column(INTEGER(unsigned=True), nullable=False, server_default='0', comment="总用户")
    user_active_count = Column(INTEGER(unsigned=True), nullable=False, server_default='0', comment="总活跃")
    new_user_count = Column(INTEGER(unsigned=True), nullable=False, server_default='0', comment="总新增用户")
    game_type = Column(TINYINT(unsigned=True), nullable=False, server_default='1', comment="盘口类型1:比赛 2:数字")

    report_date = Column(Date, nullable=False, index=True)

    __mapper_args__ = {
        "order_by": report_date.desc(),
    }

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            value = getattr(self, key)
            if key in {'surplus_money', 'withdraw_total', 'charge_total', 'bet_money_total', 'benefit_total'}:
                value = int(value)
            if key == 'report_date':
                value = str(value)
            result[key] = value
        return result


db.create_all()
