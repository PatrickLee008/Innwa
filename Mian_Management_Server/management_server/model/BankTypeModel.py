from management_server import db, app
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.mysql import TIMESTAMP
from datetime import datetime


class BankType(db.Model):
    __tablename__ = 'm_app_bank_type'
    ID = Column(Integer, nullable=False, autoincrement=True, primary_key=True, comment="ID")
    NAME = Column(String(64), comment="银行名称")

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            value = getattr(self, key)
            result[key] = value
        return result

db.create_all()