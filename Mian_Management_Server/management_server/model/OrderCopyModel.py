from management_server import db
from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import TIMESTAMP, BIGINT
from datetime import datetime
import ipaddress


defaults = {
    'USER_NAME': '',
    'ORDER_DESC': '',
    'BET_TYPE': '0',
    'REMARK': '',
    'BET_HOST_TEAM_RESULT': '-1',
    'BET_GUEST_TEAM_RESULT': '-1',
    'BALL_TYPE': '0',
    'STATUS': False,
    'IS_MIX': False,
    'IS_WIN': '2',
    'BONUS': '0',
    'DRAW_BUNKO': '0',
    'DRAW_ODDS': '0',
    'LOSE_TEAM': '1',
    'LOSE_BALL_NUM': '1',
    'AGENT_CODE': '',
}


class OrderType:
    Digit = "8"


class OrderCopy(db.Model):
    __tablename__ = 'm_app_order_copy'
    ID = Column(String(100), primary_key=True)
    ORDER_ID = Column(String(40), comment="订单号")
    USER_ID = Column(String(100), comment="比赛描述")
    AGENT_CODE = Column(String(16), nullable=False, server_default="", comment="代理code")
    USER_NAME = Column(String(255), comment="用户昵称")
    MATCH_ID = Column(String(20), comment="比赛号")
    ORDER_TYPE = Column(String(2), comment="订单类型:1单笔胜负(让球)2单笔大小球3波胆4混合胜负5混合大小6单笔单双7混合单双8数字盘9数字盘3d 10胜负平单笔 11胜负平混合")
    ORDER_DESC = Column(String(64), comment="订单描述")
    BET_MONEY = Column(String(64), comment="下注金额")
    BET_TYPE = Column(String(3), comment="下注类型:1主胜,2客胜,3平局")
    CREATE_TIME = Column(TIMESTAMP, default=datetime.now)
    UPDATE_TIME = Column(TIMESTAMP, onupdate=datetime.now)
    MATCH_TIME = Column(TIMESTAMP)
    REMARK = Column(String(64), comment="备注")
    BET_HOST_TEAM_RESULT = Column(String(16), comment="比赛主队结果")
    BET_GUEST_TEAM_RESULT = Column(String(16), comment="比赛主队结果")
    BALL_TYPE = Column(String(2), comment="大小球类型:1.大球;2,小球")
    STATUS = Column(String(2), comment="订单状态:0无效,1有效")
    IS_MIX = Column(String(2), comment="是否混合过关:0否，1是")
    IS_WIN = Column(String(2), comment="订单结果:0、输，1、赢,  2未出结果")
    BONUS = Column(String(32), comment="奖金(赢得奖金+下注金额)")
    BET_ODDS = Column(String(32), comment="下注时所选赔率")
    DRAW_BUNKO = Column(String(4), comment="平局胜负(0:+;1:-)")
    DRAW_ODDS = Column(String(4), comment="平局赔率（%）")
    LOSE_TEAM = Column(String(32), comment="让球方1主队,2客队")
    LOSE_BALL_NUM = Column(String(16), comment="胜负时：让球数/大小球时：球数")
    IP = Column(BIGINT(20), nullable=False, server_default='0', comment="下单ip")

    __mapper_args__ = {
        "order_by": CREATE_TIME.desc(),
    }

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            value = getattr(self, key)
            if key in {'CREATE_TIME', 'UPDATE_TIME', 'MATCH_TIME'}:
                value = str(value)
            if key == 'IP':
                value = str(ipaddress.ip_address(value))
            if key in {'BET_HOST_TEAM_RESULT', 'BET_GUEST_TEAM_RESULT'} and value == '-1':
                value = ''
            result[key] = value
        return result

    def to_cal(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            value = getattr(self, key)
            result[key] = value
        return result

    def to_history(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            value = getattr(self, key)
            if key == 'ID':
                continue
            if key == "UPDATE_TIME" and not value:
                value = datetime.now()
            if value is None or value == "":
                value = defaults[key]
            if key in {'IS_MIX', 'STATUS'}:
                value = value == "1"
            result[key] = value
        return result


