from management_server import db, app
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.mysql import TIMESTAMP
import datetime


class Settlement(db.Model):
    __tablename__ = 'm_tran_settlement'
    ID = Column(String(100), nullable=False, primary_key=True)
    TRAN_ID = Column(String(32), comment="交易流水号(订单号)")
    MATCH_ID = Column(String(32), comment="比赛号")
    USER_ID = Column(String(64), comment="玩家游戏编号")
    USER_NICK_NAME = Column(String(255), comment="游戏玩家昵称")
    TRAN_MONEY = Column(String(40), comment="交易金额(下注金额)")
    AGENT_ID = Column(String(32), default="", comment="代理商ID")
    AGENT_NAME = Column(String(255), default="", comment="代理商名字")
    AGENT_PROFIT_BL = Column(String(32), comment="代理商分润比例")
    AGENT_PROFIT_MONEY = Column(String(32), comment="代理商分润金额")
    TRAN_CONTENT = Column(String(255), comment="交易内容，如10元20张房卡")
    PROFIT_TYPE = Column(String(10), comment="分润类型 1玩家下注给代理分润2 比赛结算玩家分润")
    STATUS = Column(String(32), comment="0:未付款给代理，1:已付款给代理商 2:订单被撤回")
    CREATE_TIME = Column(TIMESTAMP, default=datetime.datetime.now)
    UPDATE_TIME = Column(TIMESTAMP, onupdate=datetime.datetime.now, comment="操作时间")
    UPDATOR = Column(String(64), default="", comment="结算人")
    ORDER_TYPE = Column(String(2), comment="订单类型:1胜负(让球)2大小球3波胆")
    IS_WIN = Column(String(2), comment="结算结果:0、输，1、赢,")
    BONUS = Column(String(40), comment="奖金(赢得奖金+下注金额)")

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:

            value = getattr(self, key)
            if key in {'CREATE_TIME', 'UPDATE_TIME'}:
                value = str(value)
            result[key] = value
        return result
