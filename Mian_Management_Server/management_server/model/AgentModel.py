from management_server import db, app
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.mysql import TIMESTAMP
from management_server.model.SysUserModel import SysUser
import datetime


class Agent(db.Model):
    __tablename__ = 'm_agent_new'
    AGENT_CODE = Column(String(64), nullable=False, primary_key=True)
    AGENT_NAME = Column(String(255), comment="代理名称")
    LEVEL = Column(String(32), comment="代理级别 0超管 1：一级代理 2：二级代理 3：三级代理")

    SEX = Column(String(8), comment="性别（1：男；2：女；3：未知）")
    PHONE_NO = Column(String(32), comment="手机号")
    STATUS = Column(String(10), comment="状态:0不正常 1正常")

    TOTAL_MONEY = Column(String(40), comment="返利总金额")
    CASH_MONEY = Column(String(40), comment="提现金额")
    SURPLUS_MONEY = Column(String(40), comment="剩余金额")
    PROFIT = Column(String(40), comment="分润比列")

    CREATOR = Column(String(64), comment="创建人")
    CREATOR_TIME = Column(TIMESTAMP, default=datetime.datetime.now)
    UPDATOR = Column(String(64), comment="修改人")
    UPDATOR_TIME = Column(TIMESTAMP, onupdate=datetime.datetime.now)
    REMARK = Column(String(64), comment="备注")
    ACCOUNT = db.relationship('SysUser', backref='AGENT', uselist=False, cascade="all, delete-orphan", passive_deletes=True)

    PARENT_ID = Column(String(64), db.ForeignKey('m_agent_new.AGENT_CODE'), comment="上级代理ID")
    PARENT = db.relationship('Agent', backref='CHILDREN', remote_side=[AGENT_CODE])

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            value = getattr(self, key)
            if key in {'CREATOR_TIME', 'UPDATOR_TIME'}:
                value = str(value)
            result[key] = value
        
        # 添加关联的 ACCOUNT 信息
        result['ACCOUNT'] = self.ACCOUNT.to_dict() if self.ACCOUNT else None
        return result
