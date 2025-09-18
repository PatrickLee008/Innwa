from management_server import db
from sqlalchemy import Column, String, Integer
from management_server.model.UserRole import UserRole


class Role(db.Model):
    __tablename__ = 'm_role'
    ID = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    NAME = Column(String(255), comment="角色名称")
    DESCRIPTION = Column(String(255), comment="描述")
    USERS = db.relationship('SysUser', secondary=UserRole, backref=db.backref('role'), passive_deletes=True)
    ROLE_ROUTES = db.relationship('RoleRoute', backref='role', lazy='dynamic', cascade="all, delete-orphan")

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            value = getattr(self, key)
            result[key] = value

        return result
