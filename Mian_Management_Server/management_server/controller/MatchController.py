from management_server import db, auth, user_opt
from sqlalchemy import func
from management_server.model.OrderModel import Order
from management_server.model.MatchModel import Match, MatchAttr, VipMatchAttr
from management_server.model.MatchSettleModel import MatchSettle, SettleStatus, SettleType
from flask import g, request, jsonify, Blueprint
from management_server.utils import OrmUttil
from sqlalchemy import or_
import time

r_match = Blueprint('match', __name__)


# 根据列表添加比赛
@r_match.route('/add_by_list', methods=['POST'])
def add_by_list():
    args = request.get_json()

    print(args)
    for match_info in args:
        try:
            match_id = int(round(time.time() * 1000))
            match = Match(MATCH_ID=match_id)

            db.session.add(match)
            match.IS_GAME_OVER = "0"
            match.CLOSING_STATE = "0"
            OrmUttil.set_field(match, match_info)

            print(match_info['ATTR'])
            for attr in match_info['ATTR']:
                attr['MATCH_ID'] = match_id
                match_attr = MatchAttr(MATCH_ATTR_ID="%s_%s" % (match_id, attr["MATCH_ATTR_TYPE"]))
                db.session.add(match_attr)
                OrmUttil.set_field(match_attr, attr)

            db.session.commit()
        except Exception as e:
            print("add match error:", e)

    return jsonify({'code': 20000, 'message': "结算完成"})


# 结算比赛
@r_match.route('/settle', methods=['POST'])
# @auth.login_required
def settle_match():
    """
        @@@
        #### Args:
                match_id
        #### Returns::
                {'code': 20000, 'message': "添加成功"}
                {'code': 50001, 'message': "未知错误"}
        """

    args = request.get_json()
    match_id = args.get("match_id")
    run_type = args.get("run_type", 0)
    try:
        match = Match.query.filter_by(MATCH_ID=match_id).with_for_update().first()
        if not match:
            return jsonify({'code': 50002, 'message': "match does not exist"})
        if match.IS_GAME_OVER == "1":
            return jsonify({'code': 50002, 'message': "match is game over."})
        settle = MatchSettle.query.filter(MatchSettle.MATCH_ID == match_id, MatchSettle.SETTLE_TYPE == SettleType.SETTLE, MatchSettle.STATUS != SettleStatus.FINISHED).first()
        if settle:
            return jsonify({'code': 50002, 'message': "match is already under settle."})

        settle = MatchSettle(MATCH_ID=match_id, STATUS=SettleStatus.WAIT, SETTLE_TYPE=SettleType.SETTLE, RUN_TYPE=run_type)

        db.session.add(settle)
        db.session.commit()
        return jsonify({'code': 20000, 'message': "添加成功"})
    except Exception as e:
        print("add match_settle error:", e)

    return jsonify({'code': 50001, 'message': "未知错误"})


@r_match.route('/cancel', methods=['POST'])
def cancel_match():
    """
                @@@
                #### Args:
                        match_id = request.args.get('match_id')
                #### Returns::
                        {'code': 20000, 'message': "比赛撤销完成"}
            """

    args = request.get_json()
    match_id = args.get("match_id")
    run_type = args.get("run_type", 0)
    try:
        match = Match.query.filter_by(MATCH_ID=match_id).with_for_update().first()
        if not match:
            return jsonify({'code': 50002, 'message': "match does not exist"})
        settle = MatchSettle.query.filter_by(MATCH_ID=match_id).one_or_none()
        if settle:
            return jsonify({'code': 50002, 'message': "match is already under settle."})

        settle = MatchSettle(MATCH_ID=match_id, STATUS=SettleStatus.WAIT, SETTLE_TYPE=SettleType.CANCEL, RUN_TYPE=run_type)

        db.session.add(settle)
        db.session.commit()
        return jsonify({'code': 20000, 'message': "添加成功"})
    except Exception as e:
        print("add match_settle error:", e)

    return jsonify({'code': 50001, 'message': "未知错误"})


@r_match.route('/reverse', methods=['POST'])
def reverse_match():
    """
                @@@
                #### Args:
                        match_id = request.args.get('match_id')
                #### Returns::
                        {'code': 20000, 'message': "比赛撤销完成"}
            """

    args = request.get_json()
    match_id = args.get("match_id")
    run_type = args.get("run_type", 0)
    try:
        match = Match.query.filter_by(MATCH_ID=match_id).with_for_update().first()
        if not match:
            return jsonify({'code': 50002, 'message': "match does not exist"})
        if match.IS_GAME_OVER != "1":
            return jsonify({'code': 50002, 'message': "match has not been settled"})
        settle = MatchSettle.query.filter(MatchSettle.MATCH_ID == match_id, MatchSettle.STATUS < SettleStatus.FINISHED).one_or_none()
        if settle:
            return jsonify({'code': 50002, 'message': "match is already under settle."})

        settle = MatchSettle(MATCH_ID=match_id, STATUS=SettleStatus.WAIT, SETTLE_TYPE=SettleType.REVERSE, RUN_TYPE=run_type)
        settle.topping()

        db.session.add(settle)
        db.session.commit()
        return jsonify({'code': 20000, 'message': "添加成功"})
    except Exception as e:
        print("reverse match_settle error:", e)

    return jsonify({'code': 50001, 'message': "未知错误"})


@r_match.route('/add', methods=['POST'])
@auth.login_required
def add_match():
    """
    @@@
    #### Args:
            match_desc = request.args.get('MATCH_DESC', type=int)
            match_time = request.args.get('MATCH_TIME')
            closing_time = request.args.get('CLOSING_TIME')
            closing_state = request.args.get('CLOSING_STATE')
            remark = request.args.get('REMARK')
            host_team = request.args.get('HOST_TEAM')
            guest_team = request.args.get('GUEST_TEAM')
            host_team_result = request.args.get('HOST_TEAM_RESULT')
            guest_team_result = request.args.get('GUEST_TEAM_RESULT')
    #### Returns::
            {'code': 20000, 'message': "添加成功"}
            {'code': 50001, 'message': "未知错误"}
    """

    args = request.get_json()
    attrs = args.get("ATTR")

    try:
        match_id = int(round(time.time() * 1000))
        match = Match(MATCH_ID=match_id)

        db.session.add(match)
        match.IS_GAME_OVER = "0"
        match.CLOSING_STATE = "0"
        match.hide = "0"
        OrmUttil.set_field(match, args)

        for attr in attrs:
            attr['MATCH_ID'] = match_id
            match_attr = MatchAttr(MATCH_ATTR_ID="%s_%s" % (match_id, attr["MATCH_ATTR_TYPE"]))
            db.session.add(match_attr)
            OrmUttil.set_field(match_attr, attr)

        db.session.commit()
        return jsonify({'code': 20000, 'message': "添加成功"})
    except Exception as e:
        print("add match error:", e)

    return jsonify({'code': 50001, 'message': "未知错误"})


# 获取比赛列表
@r_match.route('/get_match_list', methods=['GET'])
@auth.login_required
def get_match_list():
    """
        @@@
        #### Args:
                current_page = request.args.get('page', type=int, default=1)
                limit = request.args.get('limit', type=int, default=20)
        #### Returns::
                {
                    'code': 20000,
                    'items': [u.to_dict() for u in match_list],
                    'total': total
                }
                STATUS:
                    NONE = 0
                    WAIT = 1
                    PAUSE = 2
                    SETTLING = 3
                    FINISHED = 4
    """
    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)
    is_game_over = request.args.get('is_game_over')

    match_id = request.args.get('matchId')

    exception = request.args.get('exception')
    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    reverse = request.args.get('reverse', type=int, default=0)

    match_list = Match.query.order_by(Match.MATCH_TIME.desc() if reverse else Match.MATCH_TIME)
    if exception:
        match_list = match_list.filter(Match.exception == exception)

    if match_id:
        match_list = match_list.filter(Match.MATCH_ID == match_id)

    if exception:
        match_list = match_list.filter(Match.exception == exception)

    if key_word:
        match_list = match_list.filter(or_(Match.MATCH_ID.like('%{}%'.format(key_word)), Match.MATCH_DESC.like('%{}%'.format(key_word)),
                                           Match.REMARK.like('%{}%'.format(key_word)), Match.HOST_TEAM.like('%{}%'.format(key_word)),
                                           Match.GUEST_TEAM.like('%{}%'.format(key_word))))
    if start_time:
        match_list = match_list.filter(Match.MATCH_TIME >= start_time)

    if end_time:
        end_time += ' 23:59:59'
        match_list = match_list.filter(Match.MATCH_TIME <= end_time)

    if is_game_over:
        match_list = match_list.filter(Match.IS_GAME_OVER == is_game_over)

    total = match_list.count()

    match_list = match_list.offset((current_page - 1) * limit).limit(limit).all()

    result = {}
    for u in match_list:
        result[u.MATCH_ID] = u.to_dict()
        result[u.MATCH_ID].update({'ATTR': [], 'VIP_ATTR': [], 'STATUS': 0})
    match_ids = {u.MATCH_ID for u in match_list}
    attrs = MatchAttr.query.filter(MatchAttr.MATCH_ID.in_(match_ids)).all()
    [result[u.MATCH_ID]['ATTR'].append(u.to_dict()) for u in attrs]

    vip_attrs = VipMatchAttr.query.filter(VipMatchAttr.MATCH_ID.in_(match_ids)).all()
    [result[u.MATCH_ID]['VIP_ATTR'].append(u.to_dict()) for u in vip_attrs]

    status = MatchSettle.query.filter(MatchSettle.MATCH_ID.in_(match_ids)).all()
    for u in status:
        result[u.MATCH_ID]['STATUS'] = u.STATUS
        result[u.MATCH_ID]['SETTLE_TYPE'] = u.SETTLE_TYPE
    # print("aaaaa:", result)

    return jsonify({
        'code': 20000,
        'items': list(result.values()),
        'total': total
    })


# 获取比赛列表
@r_match.route('/<int:pid>', methods=['GET'])
# @auth.login_required
def get_detail(pid):
    """
                    @@@
                    #### Args:
                           park_record/id
                    #### Returns::
                            {
                                'code': 20000,
                                'items': [u.to_dict() for u in park_record_list],
                            }
                """
    match = Match.query.filter_by(MATCH_ID=pid).first()
    if not match:
        return jsonify({
            'code': 50002,
            'message': '查询比赛记录不存在'
        })
    attrs = MatchAttr.query.filter(MatchAttr.MATCH_ID == pid).all()
    vip_attrs = VipMatchAttr.query.filter(VipMatchAttr.MATCH_ID == pid).all()
    status = MatchSettle.query.filter(MatchSettle.MATCH_ID == pid).order_by(MatchSettle.CREATE_TIME.desc()).first()

    result = match.to_dict()
    result.update({'ATTR': [], 'VIP_ATTR': [], 'STATUS': 0})

    for attr in attrs:
        all_order_ids = Order.query.with_entities(Order.ID).filter(Order.MATCH_ID == pid, Order.ORDER_TYPE == attr.MATCH_ATTR_TYPE).group_by(Order.ORDER_ID).all()
        temp = attr.to_dict()
        temp['BET_TOTAL'] = len(all_order_ids)
        result['ATTR'].append(temp)

    [result['VIP_ATTR'].append(u.to_dict()) for u in vip_attrs]
    if status:
        result['STATUS'] = status.STATUS
        result['SETTLE_TYPE'] = status.SETTLE_TYPE

    return jsonify({
        'code': 20000,
        'message': 'success',
        'items': result,
    })


@r_match.route('/remove', methods=['GET'])
@auth.login_required
def remove_match():
    """
            @@@
            #### Args:
                    remove_id = request.args.get('match_id')
            #### Returns::
                    {'code': 20000, 'message': "删除成功"}
                    {'code': 50001, 'message': "未知错误"}
        """
    remove_id = request.args.get('match_id')

    if remove_id:
        try:
            # match = Match.query.filter_by(MATCH_ID=remove_id).first_or_404()
            match = Match.query.filter_by(MATCH_ID=remove_id).with_for_update().first()
            # 删除子属性
            MatchAttr.query.filter(MatchAttr.MATCH_ID == remove_id).delete()
            VipMatchAttr.query.filter(VipMatchAttr.MATCH_ID == remove_id).delete()
            db.session.delete(match)
            db.session.commit()
            return jsonify({'code': 20000, 'message': "删除成功"})
        except Exception as e:
            print("remove_bet_account del error: ", e)
    return jsonify({'code': 50001, 'message': "未知错误"})


@r_match.route('/edit', methods=['POST'])
@auth.login_required
def edit_match():
    """
            @@@
            #### Args:
                    edit_id = request.args.get('match_id')

                    match_desc = request.args.get('MATCH_DESC', type=int)
                    match_time = request.args.get('MATCH_TIME')
                    closing_time = request.args.get('CLOSING_TIME')
                    closing_state = request.args.get('CLOSING_STATE')
                    remark = request.args.get('REMARK')
                    host_team = request.args.get('HOST_TEAM')
                    guest_team = request.args.get('GUEST_TEAM')
                    host_team_result = request.args.get('HOST_TEAM_RESULT')
                    guest_team_result = request.args.get('GUEST_TEAM_RESULT')
            #### Returns::
                    {'code': 20000, 'message': "修改成功"}
                    {'code': 50001, 'message': "未知错误"}
        """
    args = request.get_json()
    edit_id = args.get('MATCH_ID')
    attrs = args.get("ATTR")

    if edit_id:
        # match = Match.query.filter_by(MATCH_ID=edit_id).first_or_404()
        match = Match.query.filter_by(MATCH_ID=edit_id).with_for_update().first()
        # order_type = ['4', '5']
        # orders = Order.query.filter(and_(Order.MATCH_ID == edit_id, Order.ORDER_TYPE.in_(order_type)))
        if match.IS_GAME_OVER == "1":
            print("edit match while its settled:", args)
            if "HOST_TEAM_RESULT" in args or "GUEST_TEAM_RESULT" in args:
                print("edit match score while its settled:", args)
                return jsonify({'code': 50002, 'message': "match is game over, cannot edit score."})

            # HOST_TEAM_RESULT
            # GUEST_TEAM_RESULT
        OrmUttil.set_field(match, args)
        # 删除原有子属性
        MatchAttr.query.filter(MatchAttr.MATCH_ID == edit_id).delete()
        for attr in attrs:
            match_attr = MatchAttr(MATCH_ATTR_ID="%s_%s" % (match.MATCH_ID, attr["MATCH_ATTR_TYPE"]), MATCH_ID=edit_id)

            db.session.add(match_attr)

            OrmUttil.set_field(match_attr, attr)

        db.session.commit()

        user_opt.send({
            "operate": "Edit Match",
            "route": "Match Info",
            "key_word": edit_id,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "修改成功"})
    else:
        return jsonify({'code': 50001, 'message': "未知错误"})

# arthur 获取被隐藏且未确认的比赛列表
@r_match.route('/get_match_hide_warning', methods=['GET'])
@auth.login_required
def get_match_hide_warning():
    # 获取被隐藏且未确认的比赛列表，构建查询组件
    match_query = Match.query.order_by(Match.MATCH_TIME.desc()).filter(Match.hide == "1", Match.HIDE_CONFIRM == "0")
    total = match_query.count()

    match_list = match_query.all()

    result = {}
    for u in match_list:
        result[u.MATCH_ID] = u.to_dict()

    return jsonify({
        'code': 20000,
        'items': list(result.values()),
        'total': total
    })

# arthur 修改隐藏状态
@r_match.route('/set_match_hide_state', methods=['POST'])
@auth.login_required
def set_match_hide_state():
    # 修改隐藏状态
    args = request.get_json()
    match_ids = args.get('match_ids')
    hide_state = args.get('hide_state')
    # 分割字符串，转换成列表
    match_ids = match_ids.split(',')
    # 遍历列表，修改隐藏状态
    for match_id in match_ids:
        match = Match.query.filter_by(MATCH_ID=match_id).first()
        if match:
            Match.query.filter_by(MATCH_ID=match_id).update({'hide': hide_state, 'HIDE_CONFIRM': "1"})
    db.session.commit()
    return jsonify({'code': 20000, 'message': "修改成功"})