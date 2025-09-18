from app_server import db, auth
from flask import jsonify, Blueprint, request, g
from ..model.TechResultModel import TechResult, TechDetail
from app_server.utils.OrmUttil import query_by_field
import math

r_tech_result = Blueprint('tech_result', __name__)


@r_tech_result.route('', methods=['GET'])
# @auth.login_required
def get_tech_results():
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
                                'items': [u.to_dict() for u in tech_result_list],
                            }
                """
    page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)
    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    query_filter = request.args.get('filter')

    try:

        tech_result_list = TechResult.query

        tech_result_list = query_by_field(tech_result_list, query_filter, TechResult)

        if start_time:
            tech_result_list = tech_result_list.filter(db.cast(TechResult.begin_time, db.Date) >= start_time)

        if end_time:
            tech_result_list = tech_result_list.filter(db.cast(TechResult.begin_time, db.Date) <= end_time)
        if key_word:
            tech_result_list = tech_result_list.filter(TechResult.body.like('%{}%'.format(key_word)))
        total = tech_result_list.count()

        tech_result_list = tech_result_list.offset((page - 1) * limit).limit(limit).all()

        return jsonify({
            'code': 20000,
            'message': 'success',
            'items': [u.to_dict() for u in tech_result_list],
            'totalCount': total,
            'TotalPageCount': math.ceil(int(total / limit))
        })
    except Exception as e:
        print("get tech_results error:", e)

    return jsonify({'code': 50001, 'message': "查询赛果时发生错误"})


@r_tech_result.route('/<int:pid>', methods=['GET'])
# @auth.login_required
def get_detail(pid):
    """
                    @@@
                    #### Args:
                           tech_result/id
                    #### Returns::
                            {
                                'code': 20000,
                                'item': {..., details:[...]},
                            }
                """
    tech_result = TechResult.query.filter_by(id=pid).first()
    if not tech_result:
        return jsonify({
            'code': 50002,
            'message': 'not result detail found!'
        })
    details = TechDetail.query.filter(TechDetail.result_id == tech_result.id).order_by(TechDetail.minute + TechDetail.min_ex).all()
    result = tech_result.to_dict()
    result['details'] = [u.to_dict() for u in details]

    return jsonify({
        'code': 20000,
        'message': 'success',
        'item': result,
    })
