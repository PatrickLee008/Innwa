from management_server import db, app, Redis
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.mysql import TIMESTAMP, INTEGER
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash
from management_server.model.RouteModel import Route
from management_server.model.RoleModel import Role
from management_server.model.RoleRoute import RoleRoute
from management_server.model.UserRole import UserRole
from management_server.model.DeviceModel import Device
from management_server.utils.OrmUttil import PERMISSION

import datetime


class SysUser(db.Model):
    __tablename__ = 'm_sys_user'
    ID = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    ACCOUNT = Column(String(255), comment="账号")
    PASSWORD = Column(String(255), comment="密码")
    NAME = Column(String(255), comment="用户名称")
    LAST_LOGIN = Column(TIMESTAMP, comment="最后登录时间")
    IP = Column(String(100), comment="IP")
    STATUS = Column(String(32))
    SKIN = Column(String(100))
    PHONE = Column(String(32))
    AGENT_CODE = Column(String(64), db.ForeignKey('m_agent_new.AGENT_CODE', ondelete='CASCADE'), comment="所属代理ID")
    AGENT_NAME = Column(String(255), comment="所属代理名称")
    CREATOR = Column(String(255), comment="创建人")
    CREATE_TIME = Column(TIMESTAMP, default=datetime.datetime.now)
    UPDATER = Column(String(255), comment="修改人")
    UPDATE_TIME = Column(TIMESTAMP, comment="修改时间")
    ROLES = db.relationship('Role', secondary=UserRole, backref=db.backref('user'), passive_deletes=True)
    GOOGLE_SECRET =  Column(String(255), comment="谷歌密钥")
    Withdraw_Group = Column(INTEGER(unsigned=True), server_default='0', nullable=False, comment='结算组ID')

    def set_psw(self, password):
        self.PASSWORD = generate_password_hash(password)

    def check_psw(self, password):
        return check_password_hash(self.PASSWORD, password)

    def need_mac_check(self):
        print("self.role.", self.ROLES)
        roles = {role.NAME for role in self.ROLES}
        need_mac_check = 'admin' not in roles
        return need_mac_check

    # 获取token，有效时间10min
    def generate_auth_token(self, mac, expiration=60 * 60 * 2):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        token = s.dumps({'ID': self.ID, "MAC": mac})
        Redis.set("token_%s" % self.ID, token, ex=expiration)
        return token

        # 解析token，确认登录的用户身份

    def is_agent(self):
        return 'Agent' in {a.NAME for a in self.ROLES}

    def is_agent_child(self):
        return 'AgentChild' in {a.NAME for a in self.ROLES}

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        admin = SysUser.query.get(data['ID'])
        if not admin:
            return None

        # 只有admin账号需要
        # id_token = Redis.get("token_%s" % data['ID'])
        # if admin.ACCOUNT == 'admin' and id_token != token:
        #     return None

        if admin.need_mac_check():
            mac = data.get('MAC')
            if not mac:
                return None
            device = Device.query.filter_by(MacAddress=mac).one_or_none()
            if not device or not device.Enable:
                return None  # device invalid
        return admin

    @staticmethod
    def init_admin():
        print("got to init")
        admin_role = Role.query.filter_by(NAME='admin').one_or_none()
        if not admin_role:
            admin_role = Role(NAME='admin')
            db.session.add(admin_role)
            db.session.commit()
        admin = SysUser.query.filter_by(ACCOUNT='admin').one_or_none()
        if admin:
            return
        admin = SysUser(ACCOUNT='admin')
        db.session.add(admin)
        admin.set_psw('123456')
        db.session.commit()

        admin.ROLES.append(admin_role)
        db.session.commit()

        RoleRoute.query.filter_by(ROLE_ID=admin_role.ID).delete()
        all_routes = Route.query.all()
        for route in all_routes:
            role_route = RoleRoute(ROLE_ID=admin_role.ID, ROUTE_ID=route.ID, PERMISSION=PERMISSION.CRUD)
            db.session.add(role_route)
        db.session.commit()

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:

            value = getattr(self, key)
            if key == "PASSWORD":
                continue
            if key in {'LAST_LOGIN', 'CREATE_TIME', 'UPDATE_TIME'}:
                value = str(value)
            result[key] = value
        result["ROLES"] = [r.to_dict() for r in self.ROLES]

        return result


db.create_all()

SysUser.init_admin()
