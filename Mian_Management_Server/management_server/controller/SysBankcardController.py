import uuid
from datetime import datetime

from _decimal import Decimal

from management_server import db, auth, user_opt, Redis
from flask import jsonify, Blueprint, request, g
from sqlalchemy import or_, func, cast, Date

from management_server.model.ChargeCallback import ChargeCallback
from management_server.model.SysBankcardModel import SysBankcard, SysBankcardStatus
from management_server.utils.OrmUttil import set_field
import math

r_sys_bankcard = Blueprint('sys_bankcard', __name__)


@r_sys_bankcard.route('', methods=['POST'])
@auth.login_required
def add_bankcard():
    """
    @@@
    #### Args:
            {
                gym_id: BIGINT(20    #球馆id
                name: String(64)    #名称
                status: TINYINT(unsigned=True)    #状态: 0:正常 1:未开放
            }
    #### Returns::
            {'code': 20000, 'message': "平台银行卡添加成功"}
            {'code': 50001, 'message': "添加平台银行卡时发生错误"}
    """

    args = request.get_json()

    bankcard = SysBankcard()
    try:
        set_field(bankcard, args)
        db.session.add(bankcard)
        db.session.commit()

        cards_queue = 'cards_queue_kbz' if bankcard.BANK_CODE == 'KBZ' else 'cards_queue_wave'
        # 把新增加的卡加入到轮转规则中

        if bankcard.ENABLE:
            Redis.rpush(cards_queue, bankcard.ID)

        user_opt.send({
            "operate": "添加平台银行卡",
            "route": "平台银行卡管理",
            "key_word": bankcard.ID,
            "user": g.user.ACCOUNT
        })

        return jsonify({'code': 20000, 'message': "add successful."})
    except Exception as e:
        db.session.rollback()
        print("add bankcard error:", e)

    return jsonify({'code': 50001, 'message': "unknown error"})


@r_sys_bankcard.route('/<int:pid>', methods=['DELETE'])
@auth.login_required
def remove_bankcard(pid):
    """
        @@@
        #### Args:
                bankcard/id
        #### Returns::
                {'code': 20000, 'message': "平台银行卡删除成功"}
                {'code': 50001, 'message': "删除平台银行卡时发生错误"}
        """
    try:
        
      
        bankcard = SysBankcard.query.filter_by(ID=pid).first()
        if not bankcard:
            return jsonify({'code': 50001, 'message': "card not exist"})
        
        SysBankcard.query.filter_by(ID=pid).delete()

        # 把删除的踢出轮转规则
        cards_queue = 'cards_queue_kbz' if bankcard.BANK_CODE == 'KBZ' else 'cards_queue_wave'
        visible_cards = 'visible_cards_kbz' if bankcard.BANK_CODE == 'KBZ' else 'visible_cards_wave'

        Redis.lrem(cards_queue, 1, bankcard.ID)
        Redis.srem(visible_cards, bankcard.ID)

        db.session.commit()

        user_opt.send({
            "operate": "删除平台银行卡",
            "route": "平台银行卡管理",
            "key_word": pid,
            "user": g.user.ACCOUNT
        })

        return jsonify({'code': 20000, 'message': "delete successful"})
    except Exception as e:
        print("remove bankcard error:", e)
        return jsonify({
            'code': 50001,
            'message': "unknown error"
        })


@r_sys_bankcard.route('/<int:pid>/visible', methods=['PUT'])
@auth.login_required
def bankcard_visible(pid):
    """
    @@@
    #### Args:
           bankcard/id
    #### Returns::
            {'code': 20000, 'message': "平台银行卡修改成功"}
            {'code': 50001, 'message': "修改平台银行卡时发生错误"}
    """
    visible = request.get_json().get('VISIBLE')
    try:
        bankcard = SysBankcard.query.filter_by(ID=pid).first()

        visible_cards = 'visible_cards_kbz' if bankcard.BANK_CODE == 'KBZ' else 'visible_cards_wave'

        if bankcard.ENABLE and visible:
            bankcard.VISIBLE = True
            Redis.sadd(visible_cards, bankcard.ID)
        else:
            bankcard.VISIBLE = False
            Redis.srem(visible_cards, bankcard.ID)
        db.session.commit()

        user_opt.send({
            "operate": "修改银行卡显示",
            "route": "平台银行卡管理",
            "key_word": bankcard.ID,
            "user": g.user.ACCOUNT
        })

        return jsonify({'code': 20000, 'message': "edit successful"})
    except Exception as e:
        db.session.rollback()
        print("edit bankcard error:", e)

    return jsonify({'code': 50001, 'message': "unknown error"})


@r_sys_bankcard.route('/<int:pid>/active', methods=['PUT'])
@auth.login_required
def active_bankcard(pid):
    """
    @@@
    #### Args:
           bankcard/id
    #### Returns::
            {'code': 20000, 'message': "平台银行卡修改成功"}
            {'code': 50001, 'message': "修改平台银行卡时发生错误"}
    """
    enable = request.get_json().get('enable')
    try:
        bankcard = SysBankcard.query.filter_by(ID=pid).first()

        cards_queue = 'cards_queue_kbz' if bankcard.BANK_CODE == 'KBZ' else 'cards_queue_wave'
        visible_cards = 'visible_cards_kbz' if bankcard.BANK_CODE == 'KBZ' else 'visible_cards_wave'

        if enable:
            bankcard.ENABLE = True
            Redis.rpush(cards_queue, bankcard.ID)
        else:
            bankcard.ENABLE = False
            bankcard.VISIBLE = False

            Redis.srem(visible_cards, bankcard.ID)
            Redis.lrem(cards_queue, 1, bankcard.ID)

        db.session.commit()
        #
        # user_opt.send({
        #     "operate": "激活平台银行卡",
        #     "route": "平台银行卡管理",
        #     "key_word": bankcard.ID,
        #     "user": g.user.ACCOUNT
        # })

        return jsonify({'code': 20000, 'message': "edit successful"})
    except Exception as e:
        db.session.rollback()
        print("edit bankcard error:", e)

    return jsonify({'code': 50001, 'message': "unknown error"})


@r_sys_bankcard.route('/<int:pid>', methods=['PUT'])
@auth.login_required
def edit_bankcard(pid):
    """
    @@@
    #### Args:
           bankcard/id
    #### Returns::
            {'code': 20000, 'message': "平台银行卡修改成功"}
            {'code': 50001, 'message': "修改平台银行卡时发生错误"}
    """
    args = request.get_json()
    try:
        bankcard = SysBankcard.query.filter_by(ID=pid).first()
        set_field(bankcard, args)

        db.session.commit()

        user_opt.send({
            "operate": "修改平台银行卡",
            "route": "平台银行卡管理",
            "key_word": pid,
            "user": g.user.ACCOUNT
        })

        return jsonify({'code': 20000, 'message': "edit successful"})
    except Exception as e:
        db.session.rollback()
        print("edit bankcard error:", e)

    return jsonify({'code': 50001, 'message': "unknown error"})


@r_sys_bankcard.route('/<int:pid>', methods=['GET'])
@auth.login_required
def get_detail(pid):
    """
                    @@@
                    #### Args:
                           bankcard/id
                    #### Returns::
                            {
                                'code': 20000,
                                'items': [u.to_dict() for u in bankcard_list],
                            }
                """
    bankcard = SysBankcard.query.filter_by(ID=pid).first()
    if not bankcard:
        return jsonify({
            'code': 50002,
            'message': '查询平台银行卡不存在'
        })

    return jsonify({
        'code': 20000,
        'message': 'success',
        'items': bankcard.to_dict(),
    })


# >>>>> auto generate end <<<<<


@r_sys_bankcard.route('', methods=['GET'])
@auth.login_required
def get_bankcards():
    """
                    @@@
                    #### Args:
                           {
                                page: 1,
                                limit: 20,
                                filter: {},
                                start_time: "2021-09-10",
                                end_time: "2021-09-12",
                            }
                    #### Returns::
                            {
                                'code': 20000,
                                'items': [u.to_dict() for u in bankcard_list],
                            }
                """
    args = request.args
    current_page = args.get('page', type=int, default=1)
    limit = args.get('limit', type=int, default=20)
    key_word = args.get('key_word')
    start_time = args.get('start_time')
    end_time = args.get('end_time')
    bank_code = args.get('bank_code')
    print("-----", args)

    bank_card_list = SysBankcard.query

    if key_word:
        bank_card_list = bank_card_list.filter(
            or_(SysBankcard.ACCOUNT.like('%{}%'.format(key_word)), SysBankcard.BANK_CODE.like('%{}%'.format(key_word))))

    if start_time:
        start_time += ' 00:00:00'
        bank_card_list = bank_card_list.filter(SysBankcard.CREATOR_TIME >= start_time)

    if end_time:
        end_time += ' 23:59:59'
        bank_card_list = bank_card_list.filter(SysBankcard.CREATOR_TIME <= end_time)

    if bank_code:
        bank_card_list = bank_card_list.filter(SysBankcard.BANK_CODE == bank_code)

    total = bank_card_list.count()
    total_amount = bank_card_list.with_entities(func.sum(SysBankcard.INCOME)).scalar() or 0

    bank_card_list = bank_card_list.offset((current_page - 1) * limit).limit(limit).all()
    print("cha--", bank_card_list)

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in bank_card_list],
        'total': total,
        'total_amount': total_amount
    })


@r_sys_bankcard.route('/<int:pid>/reduce_income', methods=['PUT'])
# @auth.login_required
def reduce_charge(pid):
    """
    @@@
    #### Args:
           charge/id
    #### Returns::
            {'code': 20000, 'message': " 充值修改成功"}
            {'code': 50001, 'message': "修改 充值时发生错误"}
    """
    args = request.get_json()
    amount = args.get('amount')
    _datetime = args.get('datetime')
    try:
        print("???", pid, datetime, amount)
        sys_bankcard = SysBankcard.query.filter_by(ID=pid).first()
        if not sys_bankcard:
            return jsonify({
                'code': 50002,
                'message': '查询平台银行卡不存在'
            })
        sys_bankcard.INCOME = sys_bankcard.INCOME - Decimal(amount)

        transaction_id = str(uuid.uuid4())
        charge_callback = ChargeCallback(CUSTOMER_BANK_CODE=sys_bankcard.BANK_CODE, TRANSACTION_ID=transaction_id,
                                         CUSTOMER_BANK_ACCOUNT="system",
                                         RECEIVER_BANK_ACCOUNT=sys_bankcard.ACCOUNT,
                                         TRANSACTION_DATETIME=_datetime or datetime.now(), AMOUNT=-amount)

        db.session.add(charge_callback)
        db.session.commit()

        # user_opt.send({
        #     "operate": "扣除充值总额",
        #     "route": "平台银行卡管理",
        #     "key_word": pid,
        #     "user": g.user.ACCOUNT
        # })

        return jsonify({'code': 20000, 'message': " 充值修改成功"})
    except Exception as e:
        db.session.rollback()
        print("edit charge error:", e)

    return jsonify({'code': 50001, 'message': "修改 充值时发生错误"})


# 获取日报表
@r_sys_bankcard.route('/<int:pid>/daily_reports', methods=['GET'])
# @auth.login_required
def get_daily_reports(pid):
    """
                @@@
                #### Args:
                        current_page = request.args.get('page', type=int, default=1)
                        limit = request.args.get('limit', type=int, default=20)
                        key_word = request.args.get('key_word')
                        start_time = request.args.get('start_time')
                        end_time = request.args.get('end_time')
                        is_pay =
                        charge_type = 充值对象类型: 0:用户 1:代理
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
    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    print("-----", request.args, pid)

    sys_bankcard = SysBankcard.query.filter_by(ID=pid).first()
    if not sys_bankcard:
        return jsonify({
            'code': 50002,
            'message': '查询平台银行卡不存在'
        })

    charge_callback_list = ChargeCallback.query.filter(ChargeCallback.CUSTOMER_BANK_CODE == sys_bankcard.BANK_CODE,
                                                       ChargeCallback.RECEIVER_BANK_ACCOUNT == sys_bankcard.ACCOUNT).order_by(
        ChargeCallback.ID.desc())

    if start_time:
        charge_callback_list = charge_callback_list.filter(cast(ChargeCallback.CREATE_TIME, Date) >= start_time)

    if end_time:
        charge_callback_list = charge_callback_list.filter(cast(ChargeCallback.CREATE_TIME, Date) <= end_time)

    reports = {}
    for charge_callback in charge_callback_list.all():
        # charge_date = (charge_callback.TRANSACTION_DATETIME + timedelta(hours=1.5)).date()
        charge_date = charge_callback.TRANSACTION_DATETIME.date()
        card_date_key = "%s-%s-%s" % (
            charge_callback.CUSTOMER_BANK_CODE, charge_callback.RECEIVER_BANK_ACCOUNT, charge_date)
        print(card_date_key)
        if card_date_key not in reports:
            reports[card_date_key] = {"CUSTOMER_BANK_CODE": charge_callback.CUSTOMER_BANK_CODE,
                                      "RECEIVER_BANK_ACCOUNT": charge_callback.RECEIVER_BANK_ACCOUNT, "AMOUNT": 0,
                                      "DATE": str(charge_date), "CASH_OUT": 0}
        if charge_callback.AMOUNT > 0:
            reports[card_date_key]['AMOUNT'] += charge_callback.AMOUNT
        else:
            reports[card_date_key]['CASH_OUT'] += abs(charge_callback.AMOUNT)

    reports = list(reports.values())
    right_bound = current_page * limit
    paged_items = reports[(current_page - 1) * limit: right_bound if right_bound < len(reports) else len(reports)]

    sys_bankcards = SysBankcard.query.all()
    sys_bankcards = {"%s-%s" % (u.BANK_CODE, u.ACCOUNT): u.to_dict(include={"NAME"}) for u in sys_bankcards}
    result = []
    for report in paged_items:
        temp = report
        card_key = "%s-%s" % (temp['CUSTOMER_BANK_CODE'], temp['RECEIVER_BANK_ACCOUNT'])
        card = sys_bankcards.get(card_key)
        if card:
            temp.update(card)
        temp['AMOUNT'] = str(report['AMOUNT'])
        result.append(temp)

    total = len(reports)
    page_num = math.ceil(total / limit)

    print(charge_callback_list.all())
    print("cha reports--", reports)

    return jsonify({
        'code': 20000,
        'items': paged_items,
        'total': total,
        'page_num': page_num
    })
