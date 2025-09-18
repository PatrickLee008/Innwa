import redis
from sqlalchemy import or_, func, and_
from app_server import app, db, auth, Redis, app_opt, google_credentials
from app_server.utils.OrmUttil import AppOpType
from app_server.model.ChargeModel import Charge
from app_server.model.ChargeCallback import ChargeCallback, ChargeCallbackStatus
from app_server.model.SysBankcardModel import SysBankcard, SysBankcardStatus
from app_server.model.AppUserModel import AppUser
from app_server.service import translate_re, translate_re_en
from flask import g, request, jsonify, Blueprint
from decimal import Decimal
import platform
import signal
import os
import time
import re

r_charge = Blueprint('charge', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'JPG', 'PNG', 'gif', 'GIF', 'jpeg'}


def regen_words(text_annotations):
    items = []
    lines = {}

    for text in text_annotations[1:]:
        top_x_axis = text.bounding_poly.vertices[0].x
        top_y_axis = text.bounding_poly.vertices[0].y
        bottom_y_axis = text.bounding_poly.vertices[3].y

        if top_y_axis not in lines:
            lines[top_y_axis] = [(top_y_axis, bottom_y_axis), []]

        for s_top_y_axis, s_item in lines.items():
            if top_y_axis < s_item[0][1]:
                lines[s_top_y_axis][1].append((top_x_axis, text.description))
                break

    for _, item in lines.items():
        if item[1]:
            words = sorted(item[1], key=lambda t: t[0])
            items.append((' '.join([word for _, word in words])))

    print(items)
    return items


@r_charge.route('/order_image', methods=['POST'])
# @auth.login_required
def order_image():
    """

                @@@
                #### Args:
                        MONEY : String(64) "金额"
                        REMARK : String(256) "备注：申请说明"
                        file : File "充值图片"
                #### Returns::
                        {'code': 20000, 'message': "add successful."}
                        {'code': 50001, 'message': "unknown error."}
            """
    from google.cloud import translate_v2 as translate
    from google.cloud import vision
    print(request, request.form)
    try:
        # 设置超时信号处理函数
        def handler(signum, frame):
            raise TimeoutError('Query timed out after {} seconds'.format(timeout))

        if 'Linux' == platform.system() and not app.config.get('TESTING'):
            timeout = 20

            # 注册超时信号处理函数
            signal.signal(signal.SIGALRM, handler)
            # 设置超时时间
            signal.alarm(timeout)

        # 2021/05/22 防止重复提现
        # repeat_key = "user_order_image_%s" % g.user.USER_ID
        # if Redis.get(repeat_key):
        #     return jsonify({'code': 50002, 'message': "Too many operations. Please wait."})
        # Redis.set(repeat_key, 1, ex=10)

        # picture = request.files['image'].read()
        picture = request.files.get('image')
        print("---", request.files, request.form)

        if not picture:
            return jsonify({'code': 50002, 'message': "image cannot be null"})

        suffix = picture.filename.rsplit('.', 1)[1]
        if suffix not in ALLOWED_EXTENSIONS:
            return jsonify({
                'code': 50002, 'message': "incorrect file format"})
        # np_image = numpy.fromstring(picture.read(), numpy.uint8)
        # print('-----', type(picture), type(np_image))
        img_path = os.path.join('app_server/static/img/charge_temp', picture.filename)
        picture.save(img_path)

        # 识别出图片订单号
        client = vision.ImageAnnotatorClient(credentials=google_credentials)
        # client = vision.ImageAnnotatorClient()

        with open(img_path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        texts = regen_words(response.text_annotations)
        print("vision result: ", texts)

        # vision_text = "\n".join([text.description for text in texts])
        vision_text = "\n".join([line for line in texts])
        print("vision_text:", vision_text)
        translate_client = translate.Client(credentials=google_credentials)
        translate_result = translate_client.translate(vision_text, target_language="en", source_language="my")

        result_str = translate_result["translatedText"]
        print("translatedText--:", result_str)

        # return "ok"
        all_valid_trades = translate_re(result_str)

        os.remove(img_path)
        if not len(all_valid_trades):
            return jsonify({'code': 50002,
                            'message': "cannot detect the transaction id, please recheck the image or contact customer service"})

        if 'Linux' == platform.system() and signal:
            # 取消超时信号
            signal.alarm(0)

        return jsonify({
            'code': 20000,
            'message': "check successful.",
            'trades': all_valid_trades
        })
    except TimeoutError as e:
        # 查询超时，返回超时信息
        return jsonify({'code': 50003, 'message': "image reading timeout"})
    except Exception as e:
        print("add r_charge error:", e)
        if img_path and os.path.isfile(img_path):
            os.remove(img_path)

    return jsonify({'code': 50001, 'message': "unknown error."})


@r_charge.route('/order_image_en', methods=['POST'])
# @auth.login_required
def order_image_en():
    """

                @@@
                #### Args:
                        MONEY : String(64) "金额"
                        REMARK : String(256) "备注：申请说明"
                        file : File "充值图片"
                #### Returns::
                        {'code': 20000, 'message': "add successful."}
                        {'code': 50001, 'message': "unknown error."}
            """
    print(request, request.form)
    lan = request.form.get('lan')

    # paddle安装:  pip install "paddleocr>=2.0.1" --upgrade PyMuPDF==1.17.0
    # try:
    # 设置超时信号处理函数
    def handler(signum, frame):
        raise TimeoutError('Query timed out after {} seconds'.format(timeout))

    if 'Linux' == platform.system() and not app.config.get('TESTING'):
        timeout = 20

        # 设置超时信号处理函数

        # 注册超时信号处理函数
        signal.signal(signal.SIGALRM, handler)
        # 设置超时时间
        signal.alarm(timeout)

    # 2021/05/22 防止重复提现
    # repeat_key = "user_order_image_%s" % g.user.USER_ID
    # if Redis.get(repeat_key):
    #     return jsonify({'code': 50002, 'message': "Too many operations. Please wait."})
    # Redis.set(repeat_key, 1, ex=10)

    # picture = request.files['image'].read()
    picture = request.files.get('image')
    print("---", request.files, request.form)

    if not picture:
        return jsonify({'code': 50002, 'message': "image cannot be null"})

    suffix = picture.filename.rsplit('.', 1)[1]
    if suffix not in ALLOWED_EXTENSIONS:
        return jsonify({
            'code': 50002, 'message': "incorrect file format"})
    # np_image = numpy.fromstring(picture.read(), numpy.uint8)
    # print('-----', type(picture), type(np_image))
    img_path = os.path.join('app_server/static/img/charge_temp', picture.filename)
    picture.save(img_path)
    time.sleep(0.5)
    from paddleocr import PaddleOCR

    # 识别出图片订单号
    ocr = PaddleOCR(det=False, use_gpu=False,
                    lang=lan if lan else "ch")  # need to run only once to download and load model into memory
    result = ocr.ocr(img_path, cls=False)
    transaction_id = None
    amount = None
    create_time = None

    if 'Linux' == platform.system():
        result = result[0]
    result_str = " ".join([u[1][0] for u in result])
    print(result_str)
    # return "ok"
    all_valid_trades = translate_re_en(result_str)

    os.remove(img_path)
    if not len(all_valid_trades):
        return jsonify({'code': 50002,
                        'message': "cannot detect the transaction id, please recheck the image or contact customer service"})

    if 'Linux' == platform.system() and signal:
        # 取消超时信号
        signal.alarm(0)

    return jsonify({
        'code': 20000,
        'message': "check successful.",
        'trades': all_valid_trades,
        'create_time': create_time
    })
    # except TimeoutError as e:
    #     # 查询超时，返回超时信息
    #     return jsonify({'code': 50003, 'message': "image reading timeout"})
    # except Exception as e:
    #     print("add r_charge error:", e)
    #     if img_path and os.path.isfile(img_path):
    #         os.remove(img_path)
    #
    # return jsonify({'code': 50001, 'message': "unknown error."})


@r_charge.route('/apply_charge', methods=['POST'])
@auth.login_required
def apply_charge():
    """

                @@@
                #### Args:
                        MONEY : String(64) "金额"
                        REMARK : String(256) "备注：申请说明"
                        file : File "充值图片"
                #### Returns::
                        {'code': 20000, 'message': "add successful."}
                        {'code': 50001, 'message': "unknown error."}
            """
    picture = request.files.get('image')

    if picture:
        args = request.form
    else:
        args = request.get_json()

    transaction_id = args.get('transaction_id')
    amount = args.get('amount')
    try:

        # 防止并发
        getter_key = "charge_%s" % g.user.USER_ID
        success = Redis.setnx(getter_key, 1)  # SETNX命令
        if not success:
            return jsonify({'code': 50003, "message": "charge in very short time"})

        # 设置键的过期时间
        Redis.expire(getter_key, 10)

        if not amount:
            return jsonify({'code': 50002, 'message': "amount cannot be null"})

        if int(amount) < 5000:
            return jsonify({'code': 50002, 'message': "amount cannot be less than 5000"})

        # if not picture:
        #     return jsonify({'code': 50002, 'message': "image cannot be null"})

        charge_callback = ChargeCallback.query.filter(ChargeCallback.TRANSACTION_ID ==transaction_id,
                                                      ChargeCallback.AMOUNT == Decimal(amount),
                                                      ChargeCallback.STATUS == ChargeCallbackStatus.Not).first()

        if not charge_callback:
            return jsonify({'code': 50002,
                            'message': "cannot find order by this order number, please recheck or contact customer service"})

        if picture:
            suffix = picture.filename.rsplit('.', 1)[1]
            if suffix not in ALLOWED_EXTENSIONS:
                return jsonify({
                    'code': 50002, 'message': "incorrect file format"})

            path = app.config['CHARGE_APPLY_PIC_DIR']
            pic_name = "%s.%s" % (transaction_id, suffix)
            picture.save(os.path.join(path, pic_name))
            charge_callback.PICTURE = pic_name

        # 开始充值
        app_user = AppUser.query.filter_by(MAJUSER_ID=g.user.MAJUSER_ID).with_for_update().first()
        charge_id = int(round(time.time() * 1000))
        charge_callback.CHARGE_ID = charge_id

        recharge = Charge(RECHARGE_ID=charge_id)
        before_amount = Decimal(app_user.TOTAL_MONEY)
        after_amount = before_amount + charge_callback.AMOUNT
        app_user.TOTAL_MONEY = after_amount

        recharge.BEFORE_MONEY = before_amount
        recharge.AFTER_MONEY = after_amount
        charge_callback.USER_ID = recharge.USER_ID = app_user.USER_ID
        charge_callback.NICK_NAME = recharge.NICK_NAME = app_user.NICK_NAME
        recharge.MONEY = charge_callback.AMOUNT
        recharge.CHARGE_WAY = 1

        print("send amount:", amount, "data amount:", charge_callback.AMOUNT)

        if int(amount) != int(charge_callback.AMOUNT):
            return jsonify({
                'code': 50002, 'message': "amount not right"})

        db.session.add(recharge)
        charge_callback.STATUS = ChargeCallbackStatus.Confirm

        db.session.commit()

        app_opt.send({
            "user_account": app_user.OPENID,
            "user_name": app_user.NICK_NAME,
            "type": AppOpType.CHARGE,
            "amount": before_amount,
            "balance": Decimal(app_user.TOTAL_MONEY),
            "source_id": charge_id
        })
        return jsonify({'code': 20000, 'message': "add successfull"})
    except Exception as e:
        print("add r_charge error:", e)

    return jsonify({'code': 50001, 'message': "unknown error."})


# 获取订单列表
@r_charge.route('/active_bankcard', methods=['GET'])
@auth.login_required
def get_active_bankcard():
    """
                @@@
                #### Args:
                        current_page = request.args.get('page', type=int, default=1)
                        limit = request.args.get('limit', type=int, default=20)
                        key_word = request.args.get('key_word')
                        start_time = request.args.get('start_time')
                        end_time = request.args.get('end_time')
                        is_pay =
                #### Returns::
                        {
                            'code': 20000,
                            'items': [u.to_dict() for u in order_list],
                            'total': total,
                            'total_amount': total_amount
                        }
            """
    bank_code = request.args.get('bank_code')
    try:
        # if g.user.USER_ID != '09899223535':
        #     return jsonify({'code': 20000, 'items': [], })

        # if g.user.USER_ID not in ['09254338254', '0988888888'] and bank_code != 'KBZ':
        #     return jsonify({'code': 20000, 'items': [], })

        visible_cards = 'visible_cards_kbz' if bank_code == 'KBZ' else 'visible_cards_wave'
        cards_queue = 'cards_queue_kbz' if bank_code == 'KBZ' else 'cards_queue_wave'

        members = Redis.smembers(visible_cards)

        banks_id = [m.decode() for m in members]
        bankcards = SysBankcard.query.filter(SysBankcard.ID.in_(banks_id)).all()

        active_bankcards = []
        for card in bankcards:
            if card.ENABLE:
                active_bankcards.append(card)

            else:
                Redis.srem(visible_cards, card.ID)
                Redis.lrem(cards_queue, 1, card.ID)

        if not len(active_bankcards):
            return jsonify({'code': 50002, 'message': "no active bankcards."})

        return jsonify({
            'code': 20000,
            'items': [u.to_dict(include={'ID', 'ACCOUNT', 'BANK_CODE', 'NAME'}) for u in active_bankcards],
        })
    except Exception as e:
        print("add r_charge error:", e)

    return jsonify({'code': 50001, 'message': "unknown error."})


# 获取订单列表
@r_charge.route('/get', methods=['GET'])
@auth.login_required
def get_charge_list():
    """
                @@@
                #### Args:
                        current_page = request.args.get('page', type=int, default=1)
                        limit = request.args.get('limit', type=int, default=20)
                        key_word = request.args.get('key_word')
                        start_time = request.args.get('start_time')
                        end_time = request.args.get('end_time')
                        is_pay =
                #### Returns::
                        {
                            'code': 20000,
                            'items': [u.to_dict() for u in order_list],
                            'total': total,
                            'total_amount': total_amount
                        }
            """

    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)

    charge_list = ChargeCallback.query.filter(ChargeCallback.USER_ID == g.user.USER_ID, ChargeCallback.STATUS == 1)

    total_amount = charge_list.with_entities(func.sum(Charge.MONEY)).scalar() or 0

    charge_list = charge_list.order_by(ChargeCallback.CREATE_TIME.desc())

    charge_list = charge_list.offset((current_page - 1) * limit).limit(limit).all()
    total = len(charge_list)

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in charge_list],
        'total': total,
        'total_amount': total_amount
    })


# 获取订单列表
@r_charge.route('/change_card_visible', methods=['POST'])
@auth.login_required
def change_card_visible():
    args = request.get_json()
    card_id = args.get("ID")

    try:
        card = SysBankcard.query.filter_by(ID=card_id).first()
        cards_queue = 'cards_queue_kbz' if card.BANK_CODE == 'KBZ' else 'cards_queue_wave'
        visible_cards = 'visible_cards_kbz' if card.BANK_CODE == 'KBZ' else 'visible_cards_wave'

        # 如果可视集合中没这张卡，就不做任何处理
        if not Redis.sismember(visible_cards, card_id):
            return jsonify({'code': 20000})

        # 从可视队列删除
        Redis.srem(visible_cards, card_id)

        current = SysBankcard.query.filter_by(ID=card_id).with_for_update().one()
        # 转入等待队列
        if current.ENABLE:
            Redis.rpush(cards_queue, card_id)
        current.VISIBLE = 0

        # 从等待队列取出下一张
        next_card = Redis.lpop(cards_queue)
        # 如果下一张卡不在VISIBLE集合中，将其添加

        next_bank_card = SysBankcard.query.filter_by(ID=next_card).with_for_update().one()
        if next_bank_card.ENABLE:
            next_bank_card.VISIBLE = 1
            Redis.sadd(visible_cards, next_card.decode())

        db.session.commit()

        return jsonify({'code': 20000})
    except Exception as e:
        print("add r_charge error:", e)

    return jsonify({'code': 50001, 'message': "unknown error."})
