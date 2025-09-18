from management_server import db, app
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.mysql import TIMESTAMP
from datetime import datetime


class LoginRecord(db.Model):
    __tablename__ = 'm_login_record'
    ID = Column(Integer, autoincrement=True, primary_key=True)
    USER_ACCOUNT = Column(String(255), comment="用户账户")
    LOGIN_TIME = Column(TIMESTAMP, default=datetime.now)
    IP = Column(String(255), comment="用户ip")

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:

            value = getattr(self, key)
            if key == "LOGIN_TIME":
                value = str(value)
            result[key] = value
        return result


db.create_all()
