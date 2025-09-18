from management_server import db
from sqlalchemy import Column, String, Boolean, DECIMAL, INTEGER
from management_server.utils.BaseModel import BaseModel


class SysBankcardStatus:
    Disable = 0
    Enable = 1
    Invalid = 2


class SysBankcard(BaseModel):
    __tablename__ = 'm_sys_bankcard'
    NAME = Column(String(32), nullable=False, server_default="", comment="账号名称")
    ACCOUNT = Column(String(32), index=True, nullable=False, server_default="", comment="入账账号")
    BANK_CODE = Column(String(32), nullable=False, server_default="", comment="银行代号")
    INCOME = Column(DECIMAL(11, 2), nullable=False, server_default="0", comment="收入")
    DAILY_LIMIT = Column(DECIMAL(11, 2), nullable=False, server_default="0", comment="每日金额限制")
    ENABLE = Column(Boolean, nullable=False, server_default="0", comment="充值状态: 0:停用;1:启用;")
    VISIBLE = Column(Boolean, nullable=False, server_default="0", comment="可见状态: 0:不可见;1:课件;")
    RANK = Column(INTEGER, nullable=False, server_default="0", comment="轮换顺序")
    REMARK = Column(String(256), nullable=False, server_default="", comment="充值不通过原因")

    def get_today_charge(self):
        from management_server.model.ChargeCallback import ChargeCallback
        from datetime import datetime
        from sqlalchemy import func
        # mian_today = datetime.strptime("%s 01:30:00" % datetime.today().date(), "%Y-%m-%d %H:%M:%S")
        # today_charge = ChargeCallback.query.with_entities(func.sum(ChargeCallback.AMOUNT)).filter(ChargeCallback.RECEIVER_BANK_ACCOUNT == self.ACCOUNT,
        #                                                                                           ChargeCallback.CUSTOMER_BANK_CODE == self.BANK_CODE,
        #                                                                                           ChargeCallback.TRANSACTION_DATETIME >= mian_today).scalar() or 0
        today_charge = ChargeCallback.query.with_entities(func.sum(ChargeCallback.AMOUNT)).filter(
            ChargeCallback.RECEIVER_BANK_ACCOUNT == self.ACCOUNT,
            ChargeCallback.CUSTOMER_BANK_CODE == self.BANK_CODE,
            db.cast(ChargeCallback.TRANSACTION_DATETIME, db.Date) == datetime.today().date()).scalar() or 0
        return today_charge

    def to_dict(self, include=None, exclude=None):
        result = super().to_dict(include, exclude)
        if include and 'DAILY_INCOME' in include:
            result['DAILY_INCOME'] = str(self.get_today_charge())
        return result


db.create_all()
