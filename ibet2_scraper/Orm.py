from sqlalchemy import create_engine, Column, String, DateTime, SmallInteger
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import TIMESTAMP, TINYINT
from datetime import datetime
import redis
# alter table m_app_match modify column MATCH_DESC varchar(127);
# alter table m_app_match modify column REMARK varchar(127);
# 创建对象的基类:
Base = declarative_base()


# 定义Match对象:
class Match(Base):
    # 表的名字:
    __tablename__ = 'm_app_match'

    # 表的结构:
    MATCH_ID = Column(String(20), primary_key=True, comment="比赛号:系统主机，用时间戳生成，MH201804240001")
    MATCH_DESC = Column(String(127), comment="比赛描述")
    MATCH_TIME = Column(TIMESTAMP, comment="比赛时间")
    CLOSING_TIME = Column(TIMESTAMP, comment="封盘时间")
    CLOSING_STATE = Column(String(4), default="0", comment="封盘状态")
    REMARK = Column(String(127), comment="备注")
    CREATE_TIME = Column(TIMESTAMP, default=datetime.now, comment="创建时间")
    UPDATE_TIME = Column(TIMESTAMP, onupdate=datetime.now, comment="更新时间")
    HOST_TEAM = Column(String(64), comment="主队")
    GUEST_TEAM = Column(String(64), comment="客队")
    HOST_TEAM_RESULT = Column(String(4), comment="主队得分")
    GUEST_TEAM_RESULT = Column(String(4), comment="客队得分")
    IS_GAME_OVER = Column(String(2), default="0", comment="比赛是否结束:0否,1是")
    MATCH_WEB_ID = Column(String(20), comment="爬虫对应的网页ID")
    HOST_TEAM_ENG = Column(String(64), comment="主队英文名称")
    GUEST_TEAM_ENG = Column(String(64), comment="客队英文名称")
    MATCH_MD_TIME = Column(TIMESTAMP, comment="比赛时间(缅甸)")
    MANUAL_ON = Column(String(64), default="0", comment="是否切换到人工配置,0:否,1:是")
    hide = Column(String(2), default="0", comment="是否隐藏")
    exception = Column(TINYINT(3), nullable=False, default="0", comment="比赛异常状态：0正常，1可能异常，2确认异常")
    HIDE_REASON = Column(String(256), comment="隐藏原因")
    HIDE_CONFIRM = Column(String(2), comment="隐藏确认：0未确认，1已确认")
    HOST_TEAM_WEBID = Column(String(32), comment="主队ID")
    GUEST_TEAM_WEBID = Column(String(32), comment="客队ID")
    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            value = getattr(self, key)
            if key in ('MATCH_TIME', 'CLOSING_TIME', 'CREATE_TIME', 'UPDATE_TIME', 'MATCH_MD_TIME'):
                value = str(value)
            result[key] = value
        return result


# 定义MatchAttr对象:
class MatchAttr(Base):
    # 表的名字:
    __tablename__ = 'm_app_match_attr'

    # 表的结构:
    MATCH_ATTR_ID = Column(String(40), primary_key=True, comment="比赛属性id  系统主机，用时间戳生成，MH201804240001")
    MATCH_ATTR_DESC = Column(String(32), comment="比赛赔率属性描述")
    MATCH_ATTR_TYPE = Column(String(2), comment="赔率类型:1胜负(让球)2大小球3波胆")
    ODDS = Column(String(6), comment="输赢赔率(输赢和大小球时做主队和大球赔率)|波胆赔率")
    ODDS_GUEST = Column(String(6), comment="输赢和大小球时做客队和小球赔率  波胆不用")
    DRAW_BUNKO = Column(String(4), comment="平局胜负(0:+;1:-)")
    DRAW_ODDS = Column(String(6), comment="平局赔率（%）")
    MATCH_ID = Column(String(20), comment="比赛号")
    ODDS_HOST_TEAM_RESULT = Column(String(16), comment="比赛主队结果")
    ODDS_GUEST_TEAM_RESULT = Column(String(16), comment="比赛客队结果")
    REMARK = Column(String(64), comment="备注")
    CREATE_TIME = Column(TIMESTAMP, default=datetime.now, comment="创建时间")
    UPDATE_TIME = Column(TIMESTAMP, onupdate=datetime.now, comment="更新时间")
    LOSE_TEAM = Column(String(16), comment="让球方1主队,2客队")
    LOSE_BALL_NUM = Column(String(32), comment="胜负时：让球数/大小球时：球数")
    MATCH_WEB_ID = Column(String(20), comment="网页上爬取到的比赛id")

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            value = getattr(self, key)
            if key in ('UPDATE_TIME', 'CREATE_TIME'):
                value = str(value)
            result[key] = value
        return result


class Result(Base):
    # 表的名字:
    __tablename__ = 'result'
    # 表的结构:
    MATCH_ID = Column(String(20), primary_key=True)
    LEAGUE_NAME = Column(String(128))
    HOST_TEAM = Column(String(64))
    GUEST_TEAM = Column(String(64))
    MATCH_TIME = Column(DateTime)
    HALF_HOST_SCORE = Column(SmallInteger)
    HALF_GUEST_SCORE = Column(SmallInteger)
    FULL_HOST_SCORE = Column(SmallInteger)
    FULL_GUEST_SCORE = Column(SmallInteger)
    CREATE_TIME = Column(DateTime, default=datetime.now)

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            value = getattr(self, key)
            if key in ('MATCH_TIME', 'CREATE_TIME'):
                value = str(value)
            result[key] = value
        return result


# Config:
class Config(Base):
    # 表的名字:
    __tablename__ = 'm_dict'

    # 表的结构:
    MDICT_ID = Column(String(20), primary_key=True)
    CONTENT = Column(String(20))


# redis
Redis = redis.StrictRedis("localhost", 6379, 0, decode_responses=True)

# 初始化数据库连接:
# 本地
# engine = create_engine("mysql+pymysql://root:aa369963@localhost/elszuqiu")
# 服务器测试
# engine = create_engine("mysql+pymysql://root:zaq12WSX@localhost/elszuqiu")
# 服务器prod
# engine = create_engine("mysql+pymysql://root:zaq12WSX@localhost/elszuqiu")
# 新服务器prod
# engine = create_engine("mysql+pymysql://innwa:zaq12WSX@pc-gs5o3o40mcus3g0cf.rwlb.singapore.rds.aliyuncs.com/innwa", pool_size=30, pool_recycle=600,)
# 服务器test
engine = create_engine("mysql+pymysql://innwa:123456@192.168.99.114/innwa")
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
