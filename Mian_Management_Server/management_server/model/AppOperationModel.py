from management_server import db, app
from sqlalchemy import Column, String, Integer, Float, BOOLEAN
from sqlalchemy.dialects.mysql import TIMESTAMP
from datetime import datetime


class AppOperation(db.Model):
    __tablename__ = 'm_app_operation'
    ID = Column(Integer, autoincrement=True, primary_key=True)
    USER_ACCOUNT = Column(String(255), comment="用户账户")
    CREATE_TIME = Column(TIMESTAMP, default=datetime.now)
    TYPE = Column(Integer, comment="操作类型: 0.充值,1.提现,2.下注,3.结算,4.取消")
    AMOUNT = Column(Float, comment="变动金额")
    BALANCE = Column(Float, comment="余额")
    SOURCE_ID = Column(String(255), comment="来源ID,比如 提现记录ID")
    DESC = Column(String(255), comment="操作描述")
    IS_DIGIT = Column(BOOLEAN, server_default="0", nullable=False, comment="是否数字盘操作")
    MATCH_ID = Column(String(16), nullable=False, server_default="", comment="比赛号")

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:

            value = getattr(self, key)
            if key == "CREATE_TIME":
                value = str(value)
            result[key] = value
        return result

