from management_server import db
from sqlalchemy import Column, String, Boolean,Integer


class Route(db.Model):
    __tablename__ = 'm_route'
    ID = Column(Integer, nullable=False, primary_key=True)
    path = Column(String(100), comment="路由路径")
    component = Column(String(100), comment="组件")
    name = Column(String(100), comment="路由名称")
    redirect = Column(String(100), comment="重定向路径")
    parent_id = Column(String(100), comment="上级路由")
    alwaysShow = Column(Boolean, comment="总是显示")
    title = Column(String(100), comment='显示名称')
    icon = Column(String(100), comment='图标')
    roles = Column(String(100), comment="角色")

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            value = getattr(self, key)
            result[key] = value

        children = Route.query.filter_by(parent_id=self.ID).all()

        if len(children):
            result['children'] = [child.to_dict() for child in children]

        return result

    def to_dict_with_permission(self, permissions):
        if self.ID not in permissions:
            return None
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            value = getattr(self, key)
            result[key] = value
        result['permission'] = permissions[self.ID]

        children = Route.query.filter_by(parent_id=self.ID).all()

        if len(children):
            result['children'] = [child.to_dict_with_permission(permissions) for child in children if child.to_dict_with_permission(permissions)]

        return result
