from management_server import db
from sqlalchemy import Column, String, func, DateTime
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from datetime import datetime


class SettleStatus:
    NONE = 0
    WAIT = 1
    PAUSE = 2
    SETTLING = 3
    FINISHED = 4


class SettleType:
    SETTLE = 0
    CANCEL = 1
    REVERSE = 2


class GameType:
    Match = 0
    Digit = 1
    Digit3D = 2


class MatchSettle(db.Model):
    __tablename__ = 'm_match_settle'
    ID = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    MATCH_ID = Column(String(16), nullable=False, server_default='', comment='比赛号')
    PRIORITY = Column(INTEGER(unsigned=True), nullable=False, server_default='0', comment='优先级')
    GAME_TYPE = Column(TINYINT(unsigned=True), nullable=False, server_default='0', comment="游戏类型: 0比赛 1数字")
    CREATE_TIME = Column(DateTime, nullable=False, server_default=func.now())
    UPDATE_TIME = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    SETTLE_TYPE = Column(TINYINT(unsigned=True), nullable=False, server_default='0', comment="结算类型: 0结算 1取消 2撤回")
    STATUS = Column(TINYINT(unsigned=True), nullable=False, server_default='1', comment='订单状态:0未加入队列 1等待结算, 2暂停结算, 3正在结算, 4结算完成')
    RUN_TYPE = Column(TINYINT(unsigned=True), nullable=False, server_default='0',comment="结算方式: 0 旧结算 ， 1 新结算")

    __mapper_args__ = {
        'order_by': (STATUS == 4, PRIORITY.desc(), ID.desc()),
    }

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}

        for key in columns:
            value = getattr(self, key)
            if key in ('CREATE_TIME', 'UPDATE_TIME'):
                value = str(value)
            result[key] = value
        from ..model.MatchModel import Match
        from ..model.DigitalModel import Digital
        from ..model.Digital3DModel import Digital3D
        if self.GAME_TYPE == GameType.Match:
            match = Match.query.filter(Match.MATCH_ID == self.MATCH_ID).first()
            if match:
                result.update({'MATCH_DESC': match.MATCH_DESC, 'REMARK': match.REMARK})
        elif self.GAME_TYPE == GameType.Digit:
            digit = Digital.query.filter(Digital.ID == self.MATCH_ID).first()
            if digit:
                result.update({'MATCH_DESC': digit.STAGE, 'REMARK': "2D"})
        else:
            digit3d = Digital3D.query.filter(Digital3D.ID == self.MATCH_ID).first()
            if digit3d:
                result.update({'MATCH_DESC': digit3d.STAGE, 'REMARK': "3D"})
        return result

    def topping(self):
        max_priority = MatchSettle.query.with_entities(func.max(MatchSettle.PRIORITY)).scalar() or 0
        print("got max_priority", max_priority)
        self.PRIORITY = max_priority + 1


db.create_all()
