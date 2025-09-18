from management_server import db
from sqlalchemy import Column, Integer, String
from management_server.utils.OrmUttil import PERMISSION


class RoleRoute(db.Model):
    __tablename__ = 'm_role_route'
    ID = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    ROLE_ID = Column(Integer, db.ForeignKey('m_role.ID'), comment="角色id")
    ROUTE_ID = Column(Integer, db.ForeignKey('m_route.ID'), comment="路由id")
    PERMISSION = Column(Integer, comment="权限 增:0 删:1 改:2 查:3")

    def set_per(self, per):
        self.PERMISSION = per

    def disable_per(self, per):
        self.PERMISSION &= per

    def enable_per(self, per):
        self.PERMISSION |= per

    def is_allow(self, per):
        return self.PERMISSION & per == per

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            value = getattr(self, key)
            if key == "PERMISSION":
                value = PERMISSION.crud(self.PERMISSION)
            result[key] = value
        return result
