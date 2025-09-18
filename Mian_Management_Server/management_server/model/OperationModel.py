from management_server import db, app
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.mysql import TIMESTAMP
from datetime import datetime


class Operation(db.Model):
    __tablename__ = 'm_operation'
    ID = Column(Integer, autoincrement=True, primary_key=True)
    USER_ACCOUNT = Column(String(255), comment="用户账户")
    CREATE_TIME = Column(TIMESTAMP, default=datetime.now)
    OPERATION = Column(String(255), comment="操作")
    TARGET = Column(String(255), comment="操作对象")
    ROUTE = Column(String(255), comment="操作模块")

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:

            value = getattr(self, key)
            if key == "CREATE_TIME":
                value = str(value)
            result[key] = value
        return result


