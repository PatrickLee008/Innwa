from app_server import app, db, auth, app_opt
from app_server.model.MatchModel import Match, MatchAttr, VipMatchAttr
from app_server.model.MatchResultModel import Result
from flask import g, request, jsonify, Blueprint
from app_server.utils import OrmUttil
from sqlalchemy import or_, func, and_
import json
from datetime import datetime
from app_server.model import Redis

match = Blueprint('match', __name__)


# 获取比赛列表
@match.route('/get', methods=['GET'])
@auth.login_required
def get_match_list():
    """
        @@@
        #### Args:
                page = request.args.get('page', type=int, default=1)
                limit = request.args.get('limit', type=int, default=20)
                odds_type = 'single'/'mix'/'old_mix'
                odds_type_ex = 2
                sub_leagues = request.args.get('sub_leagues')
        #### Returns::
                {
                    'code': 20000,
                    'items': [u.to_dict() for u in match_list],
                    'total': total
                }
    """
    ot_dict = {
        'single': {'1', '2', '6', '8', '10'},
        'mix': {'4', '5', '7', '9'},
        'old_mix': {'4', '5'}
    }
    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)

    match_id = request.args.get('matchId')

    # key_word = request.args.get('key_word')
    odds_type = request.args.get('odds_type')
    odds_type_ex = request.args.get('odds_type_ex')
    sub_leagues = request.args.get('sub_leagues')
    if odds_type:
        print('dict:%s' % ot_dict[odds_type])
    print(">>>>>", request.args)

    cache_key = "live_matchs|%s" % odds_type
    if odds_type_ex:
        cache_key = "live_matchs|%s" % odds_type_ex

    # if g.user.IS_VIP:
    #     print("match vip requesting...")
    #     cache_key = "live_matchs|%s_vip" % odds_type
    #     if odds_type_ex:
    #         cache_key = "live_matchs|%s_vip" % odds_type_ex

    match_caches = Redis.read(cache_key)
    # match_caches = None
    top_leagues = {'Spain Primera Division',
                   'Italy Serie A',
                   'Germany Bundesliga 1',
                   'France Ligue 1',
                   'English Premier League',
                   'English League Championship'}

    items = []
    if match_caches:
        items = json.loads(match_caches)

        print("we have got matches cache:", cache_key, len(items), items[0] if len(items) else None)
    # else:
    #     print("there is no caches fits", cache_key)
    #     odds_type_dict = ot_dict[odds_type]
    #     if odds_type_ex:
    #         odds_type_dict = {odds_type_ex}
    #
    #     match_list = Match.query.filter(and_(Match.CLOSING_TIME > datetime.now(), Match.MATCH_TIME > datetime.now())).filter(or_(Match.hide.is_(None), Match.hide != "1"))
    #
    #     if match_id:
    #         match_list = match_list.filter(Match.MATCH_ID == match_id)
    #
    #     match_list = match_list.filter(and_(Match.IS_GAME_OVER == "0", Match.CLOSING_STATE == "0")).order_by(Match.REMARK.in_(top_leagues).desc()).all()
    #     matches_dict = {m.MATCH_ID: m.to_dict() for m in match_list}
    #
    #     all_attrs = MatchAttr.query.filter(MatchAttr.MATCH_ID.in_(matches_dict)).all()
    #
    #     for attr in all_attrs:
    #         if 'ATTR' not in matches_dict[attr.MATCH_ID]:
    #             matches_dict[attr.MATCH_ID]['ATTR'] = []
    #         matches_dict[attr.MATCH_ID]['ATTR'].append(attr.to_dict())
    #
    #     for mc in match_list:
    #         info = matches_dict[mc.MATCH_ID]
    #         odds_type_fit = False
    #         if not info.get('ATTR'):
    #             continue
    #
    #         for i in range(len(info['ATTR']) - 1, -1, -1):
    #             attr = info['ATTR'][i]
    #             if attr['MATCH_ATTR_TYPE'] in odds_type_dict:
    #                 print("----info", info)
    #                 odds_type_fit = True
    #                 # 单双赔率拼接方式不同
    #                 if attr['MATCH_ATTR_TYPE'] in {'6', '7'}:
    #                     attr['REAL_ODDS'] = "%s/%s" % (attr['ODDS'], attr['ODDS_GUEST'])
    #                 else:
    #                     sign = "-" if attr['DRAW_BUNKO'] == "1" else "+"
    #                     attr['REAL_ODDS'] = "%s%s%s" % (attr['LOSE_BALL_NUM'], sign, attr['DRAW_ODDS'])
    #             else:
    #                 del (info['ATTR'][i])
    #         if odds_type_fit:
    #             items.append(info)
    #     print("the ---", items)

        # Redis.write(cache_key, json.dumps(items), 10)

    # 联赛排序
    leagues = list({u['REMARK'] for u in items})
    leagues.sort()
    leagues.sort(key=lambda x: x in top_leagues, reverse=True)

    # 联赛过滤
    if sub_leagues:
        sub_leagues = set(sub_leagues.split(","))
        print(sub_leagues)
        items = [i for i in items if i['REMARK'] in sub_leagues]

    # print("got the sub leagues", items)
    # 分页操作
    total = len(items)
    page_num = int(total / limit) + 1
    right_bound = current_page * limit
    paged_items = items[(current_page - 1) * limit: right_bound if right_bound < len(items) else len(items)]

    return jsonify({
        'code': 20000,
        'items': paged_items,
        'total': len(items),
        'allPage': page_num,
        'leagues': leagues
    })


# 获取订单列表
@match.route('/get_result', methods=['GET'])
# @auth.login_required
def get_match_result():
    """
        @@@
        #### Args:
                page = request.args.get('page', type=int, default=1)
                limit = request.args.get('limit', type=int, default=20)
                odds_type = 'single'/'mix'
        #### Returns::
                {
                    'code': 20000,
                    'items': [u.to_dict() for u in match_list],
                    'total': total
                }
    """
    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)

    match_id = request.args.get('matchId')

    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    odds_type = request.args.get('odds_type')

    result_list = Result.query
    # print(result_list.all())
    if match_id:
        result_list = result_list.filter(Result.MATCH_ID == match_id)

    if key_word:
        result_list = result_list.filter(
            or_(Result.LEAGUE_NAME.like('%{}%'.format(key_word)), Result.HOST_TEAM.like('%{}%'.format(key_word)),
                Result.GUEST_TEAM.like('%{}%'.format(key_word))))
    if start_time:
        result_list = result_list.filter(Result.MATCH_TIME >= start_time)

    if end_time:
        end_time += ' 23:59:59'
        result_list = result_list.filter(Result.MATCH_TIME <= end_time)

    total = result_list.count()
    print(result_list.all())

    result_list = result_list.offset((current_page - 1) * limit).limit(limit).all()

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in result_list],
        'total': total
    })


# 获取Odds
@match.route('/get_odds', methods=['GET'])
# @auth.login_required
def get_odds():
    """
        @@@
        #### Args:
             details = {match_id: 195532, ORDER_TYPE:1}
        #### Returns::
                {
                    'code': 20000,
                    'items': [u.to_dict() for u in attrs],
                    'total': total
                }
    """
    match_list = Match.query.filter(Match.MATCH_TIME > datetime.now(), Match.hide == "0")
    matches = {u.MATCH_ID for u in match_list}
    attrs = MatchAttr.query.filter(and_(MatchAttr.MATCH_ID.in_(matches), MatchAttr.MATCH_ATTR_TYPE.in_({'1', '2', '4', '5', '8', '9', '10'}))).all()

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in attrs],
        'total': len(attrs)
    })


# 获取Odds
@match.route('/get_odd_detail', methods=['POST'])
@auth.login_required
def get_odd_detail():
    """
        @@@
        #### Args:
             details = {match_id: 195532, ORDER_TYPE:1}
        #### Returns::
                {
                    'code': 20000,
                    'items': [u.to_dict() for u in attrs],
                    'total': total
                }
    """
    details = request.get_json().get("details")
    print(">>>>>>>>>>>dt", request.args, request.get_json())
    if details:
        result = []
        for det in details:
            attr = None
            if g.user.IS_VIP:
                attr = VipMatchAttr.query.filter(and_(VipMatchAttr.MATCH_ID == det['matchId'], VipMatchAttr.MATCH_ATTR_TYPE == det['attrType'])).one_or_none()
            if not attr:
                attr = MatchAttr.query.filter(and_(MatchAttr.MATCH_ID == det['matchId'], MatchAttr.MATCH_ATTR_TYPE == det['attrType'])).one_or_none()
            temp = attr.to_dict()
            temp.update(det)
            temp.pop('CREATE_TIME')
            result.append(temp)

        return jsonify({
            'code': 20000,
            'items': result,
            'total': len(result)
        })
    return jsonify({'code': 50001, 'message': "unknown error"})
