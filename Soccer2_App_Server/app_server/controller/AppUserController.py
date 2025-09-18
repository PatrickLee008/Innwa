from app_server import app, db, auth, app_opt
from app_server.model.AppUserModel import AppUser
from flask import g, request, jsonify, Blueprint
from app_server.utils import OrmUttil
import ipaddress
import uuid
import hashlib
import datetime

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import json


app_user = Blueprint('app_user', __name__)


@auth.verify_token
def verify_token(token):
    if not token:
        return False

    user = AppUser.verify_auth_token(token)

    if not user:
        return False

    # 开启部分账号测试
    if app.config['TESTING']:
        if user.USER_ID not in {"09428215939", "09897003434", "09899223535", "0988888888"}:
            return False

    g.user = user
    return True


@auth.error_handler
def unauthorized():
    return jsonify({
        'code': 401,
        'message': "Unauthorized access"
    })


key = 'innwa'.ljust(16, '\0').encode('utf-8')  # 密钥不足16字节的情况
iv = '1234567890123456'.encode('utf-8')  # 初始向量

# 解密函数
def decrypt(cipher_text):
    cipher_text_bytes = base64.b64decode(cipher_text)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_bytes = unpad(cipher.decrypt(cipher_text_bytes), AES.block_size, style='pkcs7')
    return decrypted_bytes.decode('utf-8')

@app_user.route('/login', methods=['POST'])
def login():
    """
        @@@
        #### Args:
                username
                password
        #### Returns::
                {'code': 20000, 'token': "JWT ****"}
                {'code': 50001, 'message': "account or password is not right"}
                {'code': 50001, 'message': "unknown error."}
        """
    print(request.get_json())
    args = request.get_json()

    encrypted_params = args.get('encryptedParams')

    if not encrypted_params:
        return json
    try:

        decrypted_text = decrypt(encrypted_params)
        params = json.loads(decrypted_text)
        account = params.get('account')
        password = params.get('password')

        user = AppUser.query.filter(AppUser.OPENID == account).first()

        if user is None or not user.check_psw(password):
            return jsonify({
                'code': 50002,
                'message': "account or password is not right."
            })

        ip = request.headers.get('x-forwarded-for') or 0
        if ip and "," in ip:
            ip = ip[0:ip.index(',')]

        user.OPT_TIME = datetime.datetime.now()
        user.LAST_LOGIN_IP = int(ipaddress.IPv4Address(ip))
        db.session.commit()
        g.user = user

        token = user.generate_auth_token()

        print("the token", token.decode())

        return jsonify({
            'code': 20000,
            "token": "JWT %s" % token.decode()
        })

    except Exception as e:
        print("login error", e)
        return jsonify({
            'code': 50001,
            'message': "unknown error."
        })


@app_user.route('/user_info', methods=['GET'])
@auth.login_required
def get_user_info():
    try:
        return jsonify({'code': 20000, 'info': g.user.to_dict(exclude=["USER_PWD"])})
    except Exception as e:
        print("user info error:", e)


@app_user.route('/add', methods=['POST'])
def add_app_user():
    """
    @@@
    #### Args:
            NICK_NAME = Column(String(255), comment="昵称")               必填
            STATUS = Column(String(6), comment="状态（ 0：正常 1：禁用）")
            SEX = Column(String(2), comment="性别（0:男 1：女）")
            PROVINCE = Column(String(64), comment="省份(暂不用)")
            CITY = Column(String(64), comment="城市(暂不用)")
            PHONE = Column(String(40), comment="手机号码")               必填
            ROOM_CARD = Column(Integer)
            CREAT_TIME = Column(TIMESTAMP, default=datetime.datetime.now)
            OPT_TIME = Column(TIMESTAMP, comment="操作时间")

            LOGO_URL = Column(String(255), comment="头像路径")
            USER_PWD = Column(String(100), comment="用户密码")               必填
            BANK_CARD = Column(String(64), comment="银行卡")
            BANK_USER_NAME = Column(String(255), comment="用户真实姓名")
            AGENT_ID = Column(String(16), comment="代理商id,绑定代理商")
    #### Returns::
            {'code': 20000, 'message': "add successful."}
            {'code': 50001, 'message': "unknown error."}
    """

    args = request.get_json()

    phone = args.get("PHONE")
    psw = args.get("USER_PWD")
    nick_name = args.get("NICK_NAME")

    try:
        if not phone.isdigit():
            return jsonify({'code': 50002, 'message': "0မှ9သာဖြည့်ရန်."})
        old_user = AppUser.query.filter_by(USER_ID=phone).one_or_none()
        if old_user:
            return jsonify(
                {'code': 50002, 'message': "အကောင့်ဖွင့်ပြီးသား ဖုန်းနပါတ်ဖြစ်နေပါသည်။ တခြားဖုန်းနပါတ်ပြောင်းလဲပါ။"})

        old_user = AppUser.query.filter_by(NICK_NAME=nick_name).one_or_none()
        if old_user:
            return jsonify({'code': 50002, 'message': "nickname repeat"})

        user = AppUser(MAJUSER_ID=str(uuid.uuid4()).replace("-", ""), OPENID=phone, USER_ID=phone)
        user.CASH_CODE = user.generate_new_cash_code()
        db.session.add(user)

        psw_sha1 = hashlib.sha1((psw + phone).encode(encoding='utf-8')).hexdigest()
        args['USER_PWD'] = psw_sha1
        args['OPENID'] = phone
        args['USER_ID'] = phone

        OrmUttil.set_field(user, args, include=['USER_PWD', 'OPENID', 'USER_ID', 'PHONE', 'NICK_NAME'])

        db.session.commit()
        return jsonify({'code': 20000, 'message': "add successful."})
    except Exception as e:
        print("add match error:", e)

    return jsonify({'code': 50001, 'message': "unknown error."})


@app_user.route('/edit', methods=['POST'])
@auth.login_required
def edit_app_user():
    """
            @@@
            #### Args:
                    OLD_PASSWORD: 用于修改密码
                    NICK_NAME = Column(String(255), comment="昵称")
                    SEX = Column(String(2), comment="性别（0:男 1：女）")
                    PHONE = Column(String(40), comment="手机号码")
                    ROOM_CARD = Column(Integer)

                    USER_PWD = Column(String(100), comment="用户密码")
                    BANK_CARD = Column(String(64), comment="银行卡")
            #### Returns::
                    {'code': 20000, 'message': "edit successful."}
                    {'code': 50001, 'message': "unknown error."}
        """
    args = request.get_json()
    phone = args.get('PHONE')
    old_password = args.get('OLD_PASSWORD')

    try:
        user = AppUser.query.filter_by(USER_ID=g.user.USER_ID).first_or_404()
        if phone and not phone.isdigit():
            return jsonify({'code': 50002, 'message': "0မှ9သာဖြည့်ရန်."})
        if args.get('USER_PWD'):
            if not old_password or not user.check_psw(old_password):
                # print("edit the psw:", args, old_password, user.check_psw(old_password))
                return jsonify({'code': 50001, 'message': "old password not right."})

            psw_sha1 = hashlib.sha1((args['USER_PWD'] + user.OPENID).encode(encoding='utf-8')).hexdigest()
            args['USER_PWD'] = psw_sha1
            user.USER_PWD = psw_sha1
        # OrmUttil.set_field(user, args)

        db.session.commit()
        return jsonify({'code': 20000, 'message': "edit successful."})
    except Exception as e:
        print("add match error:", e)
        db.session.rollback()
        return jsonify({'code': 50001, 'message': "unknown error."})
