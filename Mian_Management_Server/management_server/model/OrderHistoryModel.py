from management_server import db
from sqlalchemy import Column, String, DECIMAL, DateTime, Boolean, func, text
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, MEDIUMINT, BIGINT, SMALLINT
from datetime import datetime
import ipaddress
import uuid


class OrderHistory(db.Model):
    __tablename__ = 'order_history'
    ID = Column(INTEGER(unsigned=True), primary_key=True)
    ORDER_ID = Column(String(32), nullable=False, comment="订单号")
    AGENT_CODE = Column(String(16), nullable=False, server_default="", comment="代理code")
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
    BET_ODDS = Column(DECIMAL(5, 2), nullable=False, comment="下注时所选赔率")
    DRAW_BUNKO = Column(TINYINT(1, unsigned=True), nullable=False, server_default=text("0"), comment="平局胜负(0:+;1:-)")
    DRAW_ODDS = Column(TINYINT(unsigned=True), nullable=False, server_default=text("0"), comment="平局赔率（%）")
    LOSE_TEAM = Column(TINYINT(1, unsigned=True), nullable=False, server_default=text("1"), comment="让球方1主队,2客队")
    LOSE_BALL_NUM = Column(TINYINT(2, unsigned=True), nullable=False, server_default=text("1"), comment="胜负时：让球数/大小球时：球数")
    IP = Column(BIGINT(20), nullable=False, server_default='0', comment="下单ip")

    __mapper_args__ = {
        "order_by": CREATE_TIME.desc(),
    }

    def to_order(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            value = getattr(self, key)
            if key == 'ID':
                value = str(uuid.uuid4()).replace("-", "")
            if key == "UPDATE_TIME":
                value = datetime.now()
            if key in {'IS_MIX', 'STATUS'}:
                value = "1" if value else "0"
            # if key == 'IP':
            #     value = str(ipaddress.ip_address(value))
            # if key in {'BET_HOST_TEAM_RESULT', 'BET_HOST_TEAM_RESULT'}:
            #     if value == -1:
            #         value = ""
            result[key] = value
        result["IS_WIN"] = "2"
        result["BONUS"] = "0"
        result["STATUS"] = "1"
        # result["BET_HOST_TEAM_RESULT"] = "0"
        # result["BET_GUEST_TEAM_RESULT"] = "0"
        return result

    def set_by_order(self, order):
        for key in order.__table__.columns.keys():
            value = getattr(order, key)
            if key in self.__table__.columns.keys() and value is not None:
                if key == 'ID':
                    continue
                if key in {'IS_MIX', 'STATUS'}:
                    value = int(value) == 1
                if key == "DRAW_BUNKO" and not value:
                    value = "0"
                if key == "LOSE_BALL_NUM" and not value:
                    value = "0"
                if key == "BONUS" and not value:
                    value = "0"

                setattr(self, key, value)

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
            result[key] = value
        return result


db.create_all()
