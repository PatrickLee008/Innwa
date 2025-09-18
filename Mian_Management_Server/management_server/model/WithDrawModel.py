from management_server import db, app
from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import TIMESTAMP, INTEGER
import datetime


class WithDraw(db.Model):
    __tablename__ = 'm_withdrawal'
    WITHDRAWAL_ID = Column(String(100), nullable=False, primary_key=True)
    USER_ID = Column(String(64), comment="用户ID")
    NICK_NAME = Column(String(255), comment="用户名称")
    MONEY = Column(String(32), comment="金额")
    IS_PAY = Column(String(10), default="0", comment="是否付款 0未付款 1已付款 2提现不通过")
    CREATOR = Column(String(32), comment="创建人")
    CREATE_TIME = Column(TIMESTAMP, default=datetime.datetime.now)
    UPDATE_TIME = Column(TIMESTAMP, onupdate=datetime.datetime.now)
    PAY_TYPE = Column(String(2), comment="提现类型:1代理,2玩家")
    OPERATOR = Column(String(32), comment="操作人")
    CARD_NUM = Column(String(64), comment="提现银行卡号")
    BANK_TYPE = Column(String(32), comment="提现银行类型")
    # 新增于: 2020/9/2
    BEFORE_MONEY = Column(String(64), comment="提现前金额")
    AFTER_MONEY = Column(String(64), comment="提现后金额")
    # 新增于: 2020/9/25
    REMARK = Column(String(1023), comment="备注")
    # 新增于: 2020/9/25
    WITHDRAWAL_CODE = Column(String(8), comment="提现码")
    # 新增于: 2021/01/10
    Work_Group = Column(INTEGER(unsigned=True), server_default='0', nullable=False, comment='结算组ID')

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:

            value = getattr(self, key)
            if key in {'CREATE_TIME', 'UPDATE_TIME'}:
                value = str(value)
            result[key] = value
        return result
