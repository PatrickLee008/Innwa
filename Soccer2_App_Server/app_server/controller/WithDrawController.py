import time
from sqlalchemy import or_, func
from app_server import db, auth, app_opt, Redis
from app_server.model.WithDrawModel import WithDraw
from app_server.model.WithDrawGroupModel import WithDrawGroup
from app_server.model.BankCardModel import BankCard
from app_server.utils.OrmUttil import AppOpType
from flask import g, request, jsonify, Blueprint
from app_server.model.MDictModel import MDict
import uuid
import datetime


withdraw = Blueprint('withdraw', __name__)


# 获取订单列表
@withdraw.route('/get', methods=['GET'])
@auth.login_required
def get_withdraw_list():
    """
                @@@
                #### Args:
                        current_page = request.args.get('page', type=int, default=1)
                        limit = request.args.get('limit', type=int, default=20)

                        key_word = request.args.get('key_word')
                        start_time = request.args.get('start_time')
                        end_time = request.args.get('end_time')
                        is_pay = request.args.get('is_pay') 是否付款 0未付款 1已付款 不传此参数则表示全部
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

    withdraw_list = WithDraw.query.filter_by(USER_ID=g.user.USER_ID).order_by(WithDraw.CREATE_TIME.desc())

    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    is_pay = request.args.get('is_pay')

    if key_word:
        withdraw_list = withdraw_list.filter(
            or_(WithDraw.USER_ID.like('%{}%'.format(key_word)), WithDraw.NICK_NAME.like('%{}%'.format(key_word))))

    if is_pay:
        withdraw_list = withdraw_list.filter(WithDraw.IS_PAY == is_pay)

    if start_time:
        start_time += " 00:00:00"
        withdraw_list = withdraw_list.filter(WithDraw.CREATE_TIME >= start_time)

    if end_time:
        end_time += " 23:59:59"
        withdraw_list = withdraw_list.filter(WithDraw.CREATE_TIME <= end_time)

    total_amount = withdraw_list.with_entities(func.sum(WithDraw.MONEY)).scalar() or 0

    total = withdraw_list.count()

    withdraw_list = withdraw_list.offset((current_page - 1) * limit).limit(limit).all()

    # 修改提现组名称
    all_group_names = WithDrawGroup.query.all()
    name_dict = {u.ID: u.GROUP_NAME for u in all_group_names}
    print(name_dict)
    items = []
    for wd in withdraw_list:
        wd = wd.to_dict()
        if wd['Work_Group'] in name_dict:
            wd['Work_Group'] = name_dict[wd['Work_Group']]
        items.append(wd)

    return jsonify({
        'code': 20000,
        'items': items,
        'total': total,
        'total_amount': total_amount
    })


@withdraw.route('/apply', methods=['POST'])
@auth.login_required
def apply_withdraw():
    """
            发起提现
            @@@
            #### Args:
                    MONEY : 金额
                    ALL: 0|1 是否全部提现
                    CARD_ID : 提现银行卡ID
            #### Returns::
                    {'code': 20000, 'message': "edit successful."}
                    {'code': 50001, 'message': "unknown error."}
        """
    args = request.get_json()
    money = args.get('MONEY')
    withdraw_all = args.get('ALL')
    card_id = args.get('CARD_ID')
    try:
        user = g.user
        main_id = user.MAJUSER_ID
        del user
        from app_server.model.AppUserModel import AppUser
        db.session.commit()

        user = AppUser.query.filter_by(MAJUSER_ID=main_id).with_for_update(of=AppUser).first()

        repeat_user_key = "withdraw_limit_%s" % user.USER_ID
        if repeat_user_key and Redis.exists(repeat_user_key):
            return jsonify({'code': 40001, 'message': "withdraw repeat"})
        Redis.setex(repeat_user_key, 10, 'processed')

        print("what have we got:", user.TOTAL_MONEY)

        before_amount = float(user.TOTAL_MONEY)
        if withdraw_all:
            money = user.TOTAL_MONEY
        if before_amount < float(money):
            return jsonify({'code': 50002, 'message': "user money not enough."})
        withdraw_min_limit = MDict.query.filter_by(MDICT_ID="23").one().CONTENT
        if float(money) < float(withdraw_min_limit):
            return jsonify({'code': 50002, 'message': "withdraw_min_limit"})

        spare_groups = WithDrawGroup.query.filter(WithDrawGroup.HANDLE_ON).all()
        if not len(spare_groups):
            return jsonify({'code': 50002, 'message': "Too many players withdrawing cash, please try again later."})
        spare_groups = [u.ID for u in spare_groups]
        print("we got spare groups:", spare_groups)

        now = datetime.datetime.now()
        key_date = now.date()
        # if now.hour < 12:
        #     key_date -= datetime.timedelta(days=1)

        after_amount = before_amount - float(money)
        user.TOTAL_MONEY = after_amount
        print("app got to write:", before_amount, after_amount)

        date_key = "withdraw_code_%s" % key_date
        if not Redis.exists(date_key):
            Redis.set(date_key, 0, ex=24*60*60)

        Redis.incr(date_key)
        withdraw_code = "%05d" % int(Redis.get(date_key))

        group_key = "user_withdraw%s" % user.USER_ID
        group_value = Redis.get(group_key)
        if group_value and int(group_value) in spare_groups:
            print("user", user.USER_ID, "got group:", group_value, "expiring:", Redis.ttl(group_key))
            next_group_id = int(group_value)
        else:
            cur_work_group = MDict.query.filter_by(MDICT_ID='28').with_for_update().first()
            cur_group_id = int(cur_work_group.CONTENT)
            next_group_id = spare_groups[0]
            for gr in spare_groups:
                if gr > cur_group_id:
                    next_group_id = gr
                    break
            cur_work_group.CONTENT = next_group_id
        # 处理达到上限
        next_group = WithDrawGroup.query.filter(WithDrawGroup.ID == next_group_id).with_for_update().first()
        next_group.NOW_HANDLE += 1
        if next_group.NOW_HANDLE >= next_group.MAX_HANDLE:
            next_group.HANDLE_ON = False

        # 组过期时间
        expiration = int(MDict.query.filter_by(MDICT_ID='29').with_for_update().first().CONTENT) * 60
        print("user", user.USER_ID, "got no group, write:", next_group_id, expiration, "at:", datetime.datetime.now())
        Redis.set("user_withdraw%s" % user.USER_ID, next_group_id, expiration)

        the_withdraw = WithDraw(WITHDRAWAL_ID=str(uuid.uuid4()).replace("-", ""), WITHDRAWAL_CODE=withdraw_code, USER_ID=user.USER_ID,
                                NICK_NAME=user.NICK_NAME, MONEY=money, IS_PAY="0", CREATOR=user.USER_ID,
                                PAY_TYPE="2", BEFORE_MONEY=before_amount, AFTER_MONEY=after_amount, Work_Group=next_group_id)
        print("user withdrawing:", money, user.USER_ID, before_amount, after_amount)
        if card_id:
            bank_card = BankCard.query.get({'ID': card_id})
            the_withdraw.CARD_NUM = bank_card.CARD_NUM
            the_withdraw.BANK_TYPE = bank_card.BANK_TYPE

        db.session.add(the_withdraw)
        db.session.commit()

        app_opt.send({
            "user_account": user.OPENID,
            "user_name": user.NICK_NAME,
            "type": AppOpType.WITHDRAW,
            "amount": before_amount,
            "balance": float(user.TOTAL_MONEY),
            "source_id": the_withdraw.WITHDRAWAL_ID
        })
        return jsonify({'code': 20000, 'message': "add successful."})
    except Exception as e:
        print("add_user_withdraw error", e)
        return jsonify({'code': 50001, 'message': "unknown error."})
