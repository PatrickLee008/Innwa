from app_server import db, app
from sqlalchemy import Column, String, DECIMAL, DateTime, Boolean, func, text
from sqlalchemy.dialects.mysql import INTEGER, BIGINT, TINYINT, SMALLINT, MEDIUMINT
import ipaddress
from datetime import datetime


class OrderHistory(db.Model):
    __tablename__ = 'order_history'
    ID = Column(INTEGER(unsigned=True), primary_key=True)
    ORDER_ID = Column(String(32), nullable=False, comment="订单号")
    USER_ID = Column(String(32), nullable=False, comment="用户ID")
    USER_NAME = Column(String(32), nullable=False, server_default="", comment="用户昵称")
    MATCH_ID = Column(String(16), nullable=False, comment="比赛号")
    ORDER_TYPE = Column(TINYINT(unsigned=True), nullable=False, comment="订单类型:1单笔胜负(让球)2单笔大小球3波胆4混合胜负5混合大小6单笔单双7混合单双")
    ORDER_DESC = Column(String(64), nullable=False, server_default="", comment="订单描述")
    BET_MONEY = Column(MEDIUMINT(unsigned=True), server_default=text("0"), nullable=False, comment="下注金额")
    BET_TYPE = Column(SMALLINT(unsigned=True), server_default=text("0"), nullable=False, comment="下注类型:1主胜,2客胜 0:非胜负订单")
    CREATE_TIME = Column(DateTime, nullable=False, server_default=func.now())
    UPDATE_TIME = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    MATCH_TIME = Column(DateTime, nullable=False)
    REMARK = Column(String(64), nullable=False, server_default="", comment="备注")
    BET_HOST_TEAM_RESULT = Column(SMALLINT, nullable=False, server_default=text('-1'), comment="比赛主队结果 -1:未写入结果")
    BET_GUEST_TEAM_RESULT = Column(TINYINT, nullable=False, server_default=text('-1'), comment="比赛客队结果")
    BALL_TYPE = Column(TINYINT(1, unsigned=True), nullable=False, server_default=text("0"), comment="大小球类型:1.大球;2,小球 0.非大小球订单")
    STATUS = Column(Boolean, nullable=False, server_default=text('False'), comment="订单状态:0无效,1有效")
    IS_MIX = Column(Boolean, nullable=False, server_default=text('False'), comment="是否混合过关:0否，1是")
    IS_WIN = Column(TINYINT(1, unsigned=True), nullable=False, server_default=text('2'), comment="订单结果:0、输，1、赢,  2未出结果")
    BONUS = Column(DECIMAL(14, 3), nullable=False, server_default=text("0"), comment="奖金(赢得奖金+下注金额)")
    BET_ODDS = Column(DECIMAL(4, 2), nullable=False, comment="下注时所选赔率")
    DRAW_BUNKO = Column(TINYINT(1, unsigned=True), nullable=False, server_default=text("0"), comment="平局胜负(0:+;1:-)")
    DRAW_ODDS = Column(TINYINT(unsigned=True), nullable=False, server_default=text("0"), comment="平局赔率（%）")
    LOSE_TEAM = Column(TINYINT(1, unsigned=True), nullable=False, server_default=text("1"), comment="让球方1主队,2客队")
    LOSE_BALL_NUM = Column(TINYINT(2, unsigned=True), nullable=False, server_default=text("1"), comment="胜负时：让球数/大小球时：球数")
    AGENT_CODE = Column(String(16), nullable=False, server_default="", comment="代理code")
    IP = Column(BIGINT(20), nullable=False, server_default='0', comment="下单ip")

    __mapper_args__ = {
        "order_by": CREATE_TIME.desc(),
    }

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            value = getattr(self, key)
            if key in {'CREATE_TIME', 'UPDATE_TIME', 'MATCH_TIME', 'BONUS'}:
                value = str(value)
            if key == "BET_ODDS":
                value = float(value) if self.ORDER_TYPE == 10 else int(value)
            if key in {'BET_HOST_TEAM_RESULT', 'BET_GUEST_TEAM_RESULT'} and value == -1:
                value = ''
            if key == 'IP':
                value = str(ipaddress.ip_address(value))
            result[key] = value
        return result


db.create_all()
