from management_server import db, app
from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import TIMESTAMP, TINYINT
from datetime import datetime


class Charge(db.Model):
    __tablename__ = 'm_play_recharge'
    RECHARGE_ID = Column(String(64), nullable=False, primary_key=True, comment="玩家冲卡ID")
    CHARGE_TYPE = Column(String(10), comment="充值对象类型: 0:用户 1:代理")
    CHARGE_WAY = Column(TINYINT, default="0", comment="充值途径,0:手动充值,1:自动充值")
    USER_ID = Column(String(64), comment="用户游戏ID")
    NICK_NAME = Column(String(64), comment="用户昵称")
    # CHARGE_NUM = Column(String(8), comment="冲卡数量")
    # CHARGE_NAME = Column(String(255))
    MONEY = Column(String(64), comment="金额")
    REMARK = Column(String(256), comment="备注：（代给代冲卡）")
    CREATOR = Column(String(64), comment="所属代理商id")
    CREATOR_TIME = Column(TIMESTAMP, default=datetime.now, comment="冲卡时间")

    # 新增于: 2020/9/2
    BEFORE_MONEY = Column(String(64), comment="充值前金额")
    AFTER_MONEY = Column(String(64), comment="充值后金额")

    __mapper_args__ = {
        "order_by": CREATOR_TIME.desc(),
    }

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:

            value = getattr(self, key)
            if key in {'BEFORE_MONEY', 'AFTER_MONEY'}:
                value = "%0.2f" % float(value)
            if key in {'CREATOR_TIME'}:
                value = str(value)
            result[key] = value
        return result
