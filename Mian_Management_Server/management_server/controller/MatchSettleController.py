from management_server import app, db, auth
from management_server.model.MatchModel import Match
from management_server.model.MDictModel import MDict
from management_server.model.MatchSettleModel import MatchSettle, SettleStatus
from flask import g, request, jsonify, Blueprint
from sqlalchemy import or_

r_match_settle = Blueprint('match_settle', __name__)


@r_match_settle.route('/set_switch', methods=['POST'])
def set_switch():
    """
        @@@
        #### Args:
                switch: True/False
        #### Returns::
                {'code': 20000, 'message': "switch on" if switch else "switch off"}
        """
    switch = request.get_json().get('switch')
    MDict.query.filter_by(MDICT_ID="27").update({MDict.CONTENT: "1" if switch else "0"})
    db.session.commit()
    return jsonify({'code': 20000, 'message': "switch on" if switch else "switch off"})


@r_match_settle.route('/get_switch', methods=['GET'])
def get_switch():
    """
        @@@
        #### Args:
        #### Returns::
                {'code': 20000, 'settle_switch': switch}
        """
    switch = MDict.query.filter_by(MDICT_ID="27").one().CONTENT
    return jsonify({'code': 20000, 'settle_switch': switch == "1"})


# 结算比赛
@r_match_settle.route('/start_all', methods=['POST'])
# @auth.login_required
def start_all_settle():
    MatchSettle.query.filter(MatchSettle.STATUS == SettleStatus.PAUSE).update({MatchSettle.STATUS: SettleStatus.WAIT})
    db.session.commit()
    return jsonify({'code': 20000, 'message': "ok"})


# 结算比赛
@r_match_settle.route('/stop_all', methods=['POST'])
# @auth.login_required
def stop_all_settle():
    MatchSettle.query.filter(MatchSettle.STATUS == SettleStatus.WAIT).update({MatchSettle.STATUS: SettleStatus.PAUSE})
    db.session.commit()

    return jsonify({'code': 20000, 'message': "ok"})


# 获取比赛列表
@r_match_settle.route('/get_match_settle_list', methods=['GET'])
@auth.login_required
def get_match_settle_list():
    """
        @@@
        #### Args:
                current_page = request.args.get('page', type=int, default=1)
                limit = request.args.get('limit', type=int, default=20)
                is_finished = request.args.get('is_finished')
                match_id = request.args.get('match_id')
                key_word = request.args.get('key_word')
                start_time = request.args.get('start_time')
                end_time = request.args.get('end_time')
                reverse = request.args.get('reverse', type=int, default=0)
        #### Returns::
                {
                    'code': 20000,
                    'items': [u.to_dict() for u in match_settle_list],
                    'total': total
                }
                item:
                ID = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
                MATCH_ID = Column(String(16), nullable=False, server_default='', comment='比赛号')
                MATCH_DESC = Column(String(64), nullable=False, server_default='', comment='比赛描述')
                HOST_TEAM_RESULT = Column(TINYINT, nullable=False, server_default=text('-1'), comment='比赛主队结果 -1:未写入结果')
                GUEST_TEAM_RESULT = Column(TINYINT, nullable=False, server_default=text('-1'), comment='比赛客队结果')
                CREATE_TIME = Column(DateTime, nullable=False, server_default=func.now())
                UPDATE_TIME = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
                MATCH_TIME = Column(DateTime, nullable=False)
                MATCH_MD_TIME = Column(DateTime, nullable=False, comment='比赛时间(缅甸)')
                REMARK = Column(String(64), nullable=False, server_default='', comment='备注')
                SETTLE_TYPE = Column(TINYINT(unsigned=True), nullable=False, server_default='0', comment="结算类型: 0结算 1取消 2撤回")
                STATUS = Column(TINYINT(unsigned=True), nullable=False, server_default=text('0'), comment='订单状态:0未加入队列 1等待结算, 2暂停结算, 3正在结算, 4结算完成')

    """
    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)
    is_finished = request.args.get('is_finished', type=int, default=0)

    match_id = request.args.get('match_id')

    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    match_settle_list = MatchSettle.query

    if match_id:
        match_settle_list = match_settle_list.filter(MatchSettle.MATCH_ID == match_id)

    if key_word:
        match_settle_list = match_settle_list.filter(or_(MatchSettle.MATCH_ID.like('%{}%'.format(key_word)), Match.MATCH_DESC.like('%{}%'.format(key_word)),
                                                         Match.REMARK.like('%{}%'.format(key_word))))
    if start_time:
        match_settle_list = match_settle_list.filter(Match.MATCH_TIME >= start_time)

    if end_time:
        end_time += ' 23:59:59'
        match_settle_list = match_settle_list.filter(Match.MATCH_TIME <= end_time)
    print("----0", is_finished)

    if is_finished:
        match_settle_list = match_settle_list.filter(MatchSettle.STATUS == SettleStatus.FINISHED)
    else:
        match_settle_list = match_settle_list.filter(MatchSettle.STATUS != SettleStatus.FINISHED)

    total = match_settle_list.count()

    match_settle_list = match_settle_list.offset((current_page - 1) * limit).limit(limit).all()

    result = [u.to_dict() for u in match_settle_list]
    # for u in match_settle_list:
    #     temp = u[1].to_dict_simple()
    #     temp.update(u[0].to_dict())
    #     result.append(temp)

    return jsonify({
        'code': 20000,
        'items': result,
        'total': total
    })


@r_match_settle.route('/remove', methods=['GET'])
@auth.login_required
def remove_match_settle():
    """
            @@@
            #### Args:
                    remove_id = request.args.get('remove_id')
            #### Returns::
                    {'code': 20000, 'message': "删除成功"}
                    {'code': 50001, 'message': "未知错误"}
        """
    remove_id = request.args.get('remove_id')

    if remove_id:
        try:
            match_settle = MatchSettle.query.filter_by(ID=remove_id).one_or_none()
            if not match_settle:
                return jsonify({'code': 50002, 'message': "settlement not exist"})
            db.session.delete(match_settle)
            db.session.commit()
            return jsonify({'code': 20000, 'message': "删除成功"})
        except Exception as e:
            print("remove_bet_account del error: ", e)
    return jsonify({'code': 50001, 'message': "未知错误"})


@r_match_settle.route('/stop', methods=['POST'])
@auth.login_required
def stop_settle():
    """
            @@@
            #### Args:
                    stop_id = request.args.get('stop_id')
            #### Returns::
                    {'code': 20000, 'message': "修改成功"}
                    {'code': 50001, 'message': "未知错误"}
        """
    args = request.get_json()
    stop_id = args.get('stop_id')

    if stop_id:
        match_settle = MatchSettle.query.filter_by(ID=stop_id).one_or_none()
        if not match_settle:
            return jsonify({'code': 50002, 'message': "settlement not exist."})
        if match_settle.STATUS >= SettleStatus.SETTLING:
            return jsonify({'code': 50002, 'message': "settlement has been started."})
        match_settle.STATUS = SettleStatus.PAUSE

        db.session.commit()
        return jsonify({'code': 20000, 'message': "修改成功"})
    else:
        return jsonify({'code': 50001, 'message': "未知错误"})


@r_match_settle.route('/start', methods=['POST'])
@auth.login_required
def start_settle():
    """
            @@@
            #### Args:
                    start_id = request.args.get('start_id')
            #### Returns::
                    {'code': 20000, 'message': "修改成功"}
                    {'code': 50001, 'message': "未知错误"}
        """
    args = request.get_json()
    start_id = args.get('start_id')

    if start_id:
        match_settle = MatchSettle.query.filter_by(ID=start_id).one_or_none()
        if not match_settle:
            return jsonify({'code': 50002, 'message': "settlement not exist."})
        if match_settle.STATUS == SettleStatus.FINISHED:
            return jsonify({'code': 50002, 'message': "settlement has been finished."})
        match_settle.STATUS = SettleStatus.WAIT

        db.session.commit()
        return jsonify({'code': 20000, 'message': "修改成功"})
    else:
        return jsonify({'code': 50001, 'message': "未知错误"})
