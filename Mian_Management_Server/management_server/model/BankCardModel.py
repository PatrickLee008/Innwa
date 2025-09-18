from management_server import db, app
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.mysql import TIMESTAMP
from management_server.model.BankTypeModel import BankType
from datetime import datetime


class BankCard(db.Model):
    __tablename__ = 'm_app_bankcard'
    ID = Column(Integer, nullable=False, autoincrement=True, primary_key=True, comment="ID")
    CARD_NUM = Column(String(64), comment="银行卡号")
    USER_ID = Column(String(64), comment="绑定用户ID")
    BANK_TYPE = Column(Integer, comment="银行类型ID")
    CREATE_TIME = Column(TIMESTAMP, default=datetime.now, comment="添加时间")
    UPDATE_TIME = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    __mapper_args__ = {
        "order_by": CREATE_TIME.desc(),
    }

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:

            value = getattr(self, key)
            if key in {'CREATE_TIME'}:
                value = str(value)
            result[key] = value
            # bank_type = BankType.get({'ID': self.BANK_TYPE})
            # result['BANK_TYPE'] = bank_type
        return result

db.create_all()