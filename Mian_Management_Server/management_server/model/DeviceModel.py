from management_server import db
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean
from datetime import datetime


class Device(db.Model):
    __tablename__ = 'device'
    ID = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    Name = Column(String(255), comment="名称")
    MacAddress = Column(String(128), comment="物理地址")
    Enable = Column(Boolean, default=True, comment="是否启用")

    Creator = Column(String(64), comment="创建者")
    CreateTime = Column(DateTime, default=datetime.now, comment="创建时间")
    LastLoginTime = Column(DateTime, comment="最后登录时间")
    Remark = Column(String(255), comment="备注")

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            value = getattr(self, key)
            if key in ('CreateTime', 'LastLoginTime'):
                value = str(value)
            result[key] = value

        return result


db.create_all()
