from app_server import db, app
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.mysql import TIMESTAMP
from datetime import datetime


# 玩家充值申请表
class ChargeApply(db.Model):
    __tablename__ = 'm_charge_apply'
    ID = Column(String(64), nullable=False, primary_key=True, comment="充值申请ID")
    RECHARGE_ID = Column(String(64), comment="当充值通过时,对应的充值ID")
    USER_ID = Column(String(64), comment="用户游戏ID")
    NICK_NAME = Column(String(64), comment="用户昵称")
    CHARGE_NAME = Column(String(255), comment="充值操作人")
    MONEY = Column(String(64), comment="金额")
    REMARK = Column(String(256), comment="备注：申请说明")
    PICTURE = Column(String(256), comment="充值图片名称")
    CREATE_TIME = Column(TIMESTAMP, default=datetime.now, comment="申请时间")
    STATUS = Column(Boolean, default=False, comment="充值状态: 0:等待审核;1:充值成功;2:充值不通过")
    REASON = Column(String(256), comment="充值不通过原因")

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
            if key == "PICTURE":
                value = "%s%s" % ("static/img/charge_pics/", value)
            result[key] = value
        print("the result:", result)
        return result

db.create_all()
