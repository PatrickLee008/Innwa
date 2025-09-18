import json

import requests

from app_server import app, db, auth
from app_server.model import Redis
from flask import g, request, jsonify, Blueprint

from app_server.utils.DataKits import find_matching_games
from app_server.utils.Kits import Kits

# 定义直播模块
live = Blueprint('live', __name__)


# 获取直播数据
@live.route('/football', methods=['GET'])
@auth.login_required
def football():
    """
        描述: 获取直播数据
        作者: Arthur
        版本: 1.0
    """
    # params = request.get_json()

    # 从缓存都获取数据
    cache_key = "live_football_matchs"
    live_data = Redis.read(cache_key)
    if live_data:
        live_data = json.loads(live_data)
        return Kits.rt_data(live_data)

    # 从接口中读取数据
    url = app.config['LIVE_API_URL'] + '/live/football'
    data = {
        "page": -1,#查询所有
        "is_live": 1,#是否直播
    }
    response = requests.post(url=url, data=data)
    if response.status_code != 200:
        return Kits.rt_data(" get live data error")

    # 解析数据
    res = response.json()
    if not res['ok']:
        return Kits.rt_error(" get live data failed")

    # 获取当前的比赛
    #print(res)
    live_data = res['data']['list']
    if not live_data:
        # 返回空数据
        return Kits.rt_data([])
    # 获取缓存中的比赛信息
    odds_type = "single"
    match_cache_key = "live_matchs|%s" % odds_type
    match_caches = Redis.read(match_cache_key)
    if not match_caches:
        match_caches = []
    else:
        match_caches = json.loads(match_caches)
    # 跟系统中的比赛进行匹配
    #print(match_caches)
    #print(live_data)
    map_result = find_matching_games(match_caches, live_data, 30, 0.8)

    # 缓存当前的比赛信息(秒）
    Redis.write(cache_key, json.dumps(live_data), 30)
    return Kits.rt_data(live_data)


# 获取直播链接
@live.route('/h5playurl', methods=['GET'])
@auth.login_required
def h5playurl():
    """
        描述: 获取直播数据
        作者: Arthur
        版本: 1.0
    """
    # 获取GET参数
    params = request.args.to_dict()
    id = params.get('id')
    h5play = params.get('h5play')
    if not id:
        return Kits.rt_error(" no id")

    uid = g.user.MAJUSER_ID
    ip = request.remote_addr
    # 从接口中读取数据
    url = app.config['LIVE_API_URL'] + '/live/h5playurl'
    data = {
        "id": id,
        "lang": "zh",
        "uid": uid,
        "ip": ip,
        "h5play": h5play
    }
    response = requests.post(url=url, data=data)
    if response.status_code != 200:
        return Kits.rt_data(" get h5playurl data error")

    # 解析数据
    res = response.json()
    if not res['ok']:
        return Kits.rt_error(" get h5playurl data failed")

    # 返回直播链接
    play_url = res['data']
    return Kits.rt_data(play_url)