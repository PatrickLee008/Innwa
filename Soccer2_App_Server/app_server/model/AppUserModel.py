from app_server import db, app
from sqlalchemy import Column, String, Integer, Boolean, text
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from sqlalchemy.dialects.mysql import TIMESTAMP, BIGINT
import ipaddress
from app_server.model import Redis
import datetime
import hashlib


class AppUser(db.Model):
    __tablename__ = 'm_app_user'
    MAJUSER_ID = Column(String(100), nullable=False, primary_key=True)
    OPENID = Column(String(32), comment="微信用户opeid(同样存放userID)")
    NICK_NAME = Column(String(255), comment="昵称")
    USER_ID = Column(String(64), comment="用户ID")
    STATUS = Column(String(6), default="0", comment="状态（ 0：正常 1：禁用）")
    SEX = Column(String(2), comment="性别（0:男 1：女）")
    PROVINCE = Column(String(64), comment="省份(暂不用)")
    CITY = Column(String(64), comment="城市(暂不用)")
    PHONE = Column(String(40), comment="手机号码")
    ROOM_CARD = Column(Integer, default=0)
    CREAT_TIME = Column(TIMESTAMP, default=datetime.datetime.now)
    OPT_TIME = Column(TIMESTAMP, comment="操作时间")

    LOGO_URL = Column(String(255), comment="头像路径")
    USER_ACCOUNT = Column(String(100), comment="pc版登录用户名(已废弃)")
    USER_PWD = Column(String(100), comment="用户密码")
    USER_TYPE = Column(String(2), comment="用户类型，1：app用户，2：pc用户(暂不用)")
    YQ_CODE = Column(String(16), comment="所属代理商的邀请码(已废弃)")
    BANK_CARD = Column(String(64), comment="银行卡")
    BANK_USER_NAME = Column(String(255), comment="用户真实姓名")
    AGENT_ID = Column(String(16), comment="代理商id,绑定代理商")
    TOTAL_MONEY = Column(String(32), default="0", comment="总金额(充值金额和返利金额都入这)")
    CASH_MONEY = Column(String(32), default="0", comment="提现金额")
    IS_VIP = Column(Boolean, nullable=False, server_default=text('False'), comment="是否VIP")
    HIGHER_LIMIT = Column(Boolean, nullable=False, server_default=text('False'), comment="是否高额玩家")
    LAST_LOGIN_IP = Column(BIGINT(20), nullable=False, server_default='0', comment="最后登录ip")
    CASH_CODE = Column(String(32), default="0", comment="提现码， 自动充值用")


    def set_psw(self, password):
        self.USER_PWD = hashlib.sha1((password + self.OPENID).encode(encoding='utf-8')).hexdigest()

    def check_psw(self, password):
        return hashlib.sha1((password + self.OPENID).encode(encoding='utf-8')).hexdigest() == self.USER_PWD

    # 获取token，有效时间10min
    def generate_auth_token(self, expiration=60*60*12):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        token = s.dumps({'MAJUSER_ID': self.MAJUSER_ID})
        Redis.write("user_token|%s" % self.MAJUSER_ID, token, expiration)
        return token

    def generate_new_cash_code(self):
        last_user = AppUser.query.order_by(AppUser.CASH_CODE.desc()).first()
        if last_user and last_user.CASH_CODE:
            # 直接将CASH_CODE转换为整数
            last_index = int(last_user.CASH_CODE)
            new_index = last_index + 1
        else:
            new_index = 1
        # 格式化新的CASH_CODE，保持至少为6位数
        new_cash_code = f'{new_index:06d}'
        return new_cash_code

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            print("token verifying:", token, data)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
            # token has been logout
        r_token = Redis.read("user_token|%s" % data['MAJUSER_ID'])
        if not r_token or token != r_token:
            print("token has been logout")
            return None
        admin = AppUser.query.get(data['MAJUSER_ID'])
        return admin

    def to_dict(self, include=None, exclude=None):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:

            if include and key not in include:
                continue
            if exclude and key in exclude:
                continue


            value = getattr(self, key)
            if key in {'CREATE_TIME', 'UPDATE_TIME'}:
                value = str(value)
            if key == 'LAST_LOGIN_IP':
                value = str(ipaddress.ip_address(value))
            result[key] = value
        result['TOTAL_MONEY'] = format(int(float(self.TOTAL_MONEY)), ",")
        result['CASH_MONEY'] = format(int(float(self.CASH_MONEY)), ",")
        return result
