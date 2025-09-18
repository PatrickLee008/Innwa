from Orm import DBSession, Match, MatchAttr, Config, Redis
from sqlalchemy import and_, or_
from datetime import datetime, timedelta, date
import requests
import json
import time
import os
import re
from ibet_match import same_match_hide

username = "y7yyjajj"
password = "zaq12WSX"
# 测试账号
# username = 'y7yjk1'
# password = 'Abcd1234'

proxy = {'https': "127.0.0.1:10809"}
# proxy = {'https': "127.0.0.1:10120"}
# proxy = {'socks5': '127.0.0.1:10808'}
# proxy = None
headers = {'x-forwarded-for': '37.111.7.124',
           "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.55"}
# headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.55"}

draw_bunko_dict = {
    '0': '+', '1': '-', 0: '+', 1: '-',
}

lose_team_dict = {
    '1': '主队', '2': '客队', 1: '主队', 2: '客队',
}


class HomeAway:
    home = '1'
    away = '2'


def get_page_validate(page):
    # 获取页面验证参数
    view_state = re.findall(r'VIEWSTATE\".*value=\"(.*)\"', page)[0]
    view_state_generator = re.findall(r'__VIEWSTATEGENERATOR\".*value=\"(.*)\"', page)[0]
    event_validation = re.findall(r'EVENTVALIDATION\".*value=\"(.*)\"', page)[0]
    return view_state, view_state_generator, event_validation


def check_cookie(cookies):
    try:
        resp = requests.get("https://www.ibet789.com/_View/AccInfo.aspx", cookies=cookies, proxies=proxy, headers=headers, timeout=7)
    except Exception as e:
        return False
    # print("the check page:", resp.text)
    # with open("check_result.html", "w", encoding="utf-8") as f:
    #     f.write(resp.text)
    print("check result:", resp.url, resp.text != "")
    return "_View/AccInfo.aspx" in resp.url and resp.text != ""


def login():
    session = requests.session()
    resp = session.get("https://ibet789.com/", proxies=proxy, headers=headers)
    print("login resp:", resp.status_code, resp.text)
    if not resp.text:
        print("get page fail")
        return None
    # 获取页面验证参数
    view_state, view_state_generator, event_validation = get_page_validate(resp.text)
    # 构造登录表单
    login_form = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": view_state,
        "__VIEWSTATEGENERATOR": view_state_generator,
        "__VIEWSTATEENCRYPTED": "",
        "__EVENTVALIDATION": event_validation,
        "txtUserName": username,
        "password": password,
        "btnSignIn": "Login"
    }

    # 提交登录表单
    session.post("https://www.ibet789.com/Default1_0.aspx", login_form, proxies=proxy, headers=headers)
    cookies = requests.utils.dict_from_cookiejar(session.cookies)
    return cookies


def get_cookies():
    cookie_path = "cookies"

    cookies = {}
    try:
        if os.path.isfile(cookie_path):
            with open(cookie_path, 'r', encoding='utf-8') as f:
                cookies = json.loads(f.read())
    except Exception as e:
        print("cookie check error", e)

    cookie_valid = check_cookie(cookies)
    if not cookie_valid:
        cookies = login()
        cookie_valid = check_cookie(cookies)

    if cookie_valid:
        with open(cookie_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(cookies))
        return cookies

    return None


def get_matches(with_mix=False):
    # 预处理
    start_time = time.time()
    db_session = DBSession()
    exe_on = db_session.query(Config).filter_by(MDICT_ID="20").one().CONTENT == '1'
    if not exe_on:
        db_session.close()
        return

    single_odds_on = db_session.query(Config).filter_by(MDICT_ID="21").one().CONTENT == '1'
    multi_odds_on = db_session.query(Config).filter_by(MDICT_ID="22").one().CONTENT == '1'
    print("mix en?", multi_odds_on, with_mix)

    odds_cond_1 = int(db_session.query(Config).filter_by(MDICT_ID="16").one().CONTENT)
    odds_cond_2 = int(db_session.query(Config).filter_by(MDICT_ID="17").one().CONTENT)
    odds_cond_4 = int(db_session.query(Config).filter_by(MDICT_ID="18").one().CONTENT)
    odds_cond_5 = int(db_session.query(Config).filter_by(MDICT_ID="19").one().CONTENT)

    # 爬取的联赛
    include_leagues = db_session.query(Config).filter_by(MDICT_ID="41").one().CONTENT.upper()
    include_leagues = set(include_leagues.split(","))

    # 查询已有比赛
    old_match_queries = db_session.query(Match).filter(Match.MATCH_TIME > (datetime.now() - timedelta(days=1))).all()
    old_matches = {}
    live_matches = set()
    hided_matches = set()
    abort_matches = set()
    live_match_ids = set()
    for match in old_match_queries:
        web_id = int(match.MATCH_WEB_ID or 0)
        if match.MANUAL_ON == "1" or match.IS_GAME_OVER == "1":
            abort_matches.add(web_id)
            continue
        old_matches[web_id] = match

        if match.hide and match.hide == "1":
            hided_matches.add(web_id)

        if match.CLOSING_TIME > datetime.now() and match.hide == "0":
            live_matches.add(web_id)
            live_match_ids.add(match.MATCH_ID)

    # 查询已有赔率
    old_odds_dict = {}
    old_let_teams = {}
    old_odds_queries = db_session.query(MatchAttr).filter(MatchAttr.MATCH_ID.in_(live_match_ids)).all()
    for row in old_odds_queries:
        old_odds_dict[row.MATCH_ID] = row
        if row.LOSE_TEAM:
            old_let_teams[row.MATCH_ID] = row.LOSE_TEAM

    _cookies = get_cookies()
    if not _cookies:
        db_session.close()
        return
    ts = round(time.time())
    request_session = requests.Session()
    request_session.get("https://www.ibet789.com/Main.aspx?lang=EN-US", cookies=_cookies, proxies=proxy, headers=headers)
    # 先行处理1x2
    params = {
        "ot": "t",
        "gType": "S",
        "gType2": "S",
        "sk": "",
        "r": "",
        "LID": "",
        "_": str(ts)
    }
    resp = request_session.get("https://www.ibet789.com/_View/OddsOE1X2_G.ashx", params=params, cookies=_cookies, proxies=proxy, headers=headers)
    wld_list = eval(resp.text)[2]
    #读取本地爬虫数据
    #with open("D:/tmp/爬虫/wld_odds_dict.txt", "r", encoding="utf-8") as file:
    #    content = file.read()
    #wld_list = eval(content)[2]
    wld_odds_dict = {}
    for league in wld_list:
        title = league[0]
        matches = league[1]
        league_name = title[1]

        # 过滤未录入联赛
        if league_name.upper() not in include_leagues:
            continue
        for match in matches:
            match_web_id = match[0]
            if match[28] <= 0:
                continue
            w, l, d = "%.2f" % match[28], "%.2f" % match[29], "%.2f" % match[30]
            wld_odds_dict[match_web_id] = [w, l, d]

    # tf为 "r" 时表示已经开始
    params = {
        "ot": "t",
        "tf": "2",
        "mt": "0",
        "tv": "2",
        "ov": "0",
        "sk": "",
        "r": "",
        "LID": "",
        "_": str(ts)
    }

    resp = request_session.get("https://www.ibet789.com/_View/MOdds_G.ashx", params=params, cookies=_cookies, proxies=proxy, headers=headers)

    info_list = eval(resp.text)
    # 读取本地爬虫数据
    # with open("D:/tmp/爬虫/info_list.txt", "r", encoding="utf-8") as file:
    #     content = file.read()
    # info_list = eval(content)
    all_leagues = info_list[2]

    # print("the now matches:", all_leagues)

    match_count = 0
    attrs = []

    def odds_format(d_odds):
        d_odds = str(d_odds)
        tens = 0
        if len(d_odds) > 1:
            tens = int(d_odds[:-1])
        ones = int(d_odds[-1])
        if ones < 3:
            return str(tens * 10)
        if ones < 8:
            return str(tens * 10 + 5)
        return str(tens * 10 + 10)

    for league in all_leagues:
        title = league[0]
        matches = league[1]
        league_name = title[1]
        if league_name == "FIFA WORLD CUP 2022 (IN QATAR)":
            print("?????", league_name.upper() not in include_leagues, include_leagues)

        # 过滤未录入联赛
        if league_name.upper() not in include_leagues:
            print("not included league_name:", league_name)
            continue
        for match in matches:
            time.sleep(0.001)
            match_web_id = match[0]
            match_time = datetime.strptime(match[63], "%Y-%m-%d %H:%M:%S")  # 筛选myan盘

            _is_mian = (not match[76] or not match[77]) and (match[72] != -1 or match[75] != -1)

            is_first = match[9]
            is_first = True
            if not _is_mian or not is_first:
                continue

            # 让球方判断更改
            lose_team = HomeAway.home if match[68] else HomeAway.away
            if match[19] == "France" and match[20] == "Denmark":
                # and league_name == "FIFA WORLD CUP 2022 (IN QATAR)"
                print("?????", match[68], match[24], lose_team)

            wl_mak = match[72]
            bs_mak = match[75]

            match_web_id_wl = "%s_%s" % (match_web_id, "1")
            match_web_id_bs = "%s_%s" % (match_web_id, "2")
            match_web_id_4 = "%s_%s" % (match_web_id, "4")
            match_web_id_5 = "%s_%s" % (match_web_id, "5")
            match_web_id_10 = "%s_%s" % (match_web_id, "10")

            # 去除已禁用或者已结束的比赛
            if match_web_id in abort_matches:
                print("*--match which is abort--*:", match_web_id)
                continue

            match_count += 1

            match_md_time = match_time - timedelta(hours=1.5)
            match_desc = ""

            if match_web_id in live_matches:
                live_matches.remove(match_web_id)

            if match_web_id in old_matches:
                old_match = old_matches[match_web_id]
                match_id = old_matches[match_web_id].MATCH_ID
                old_match.MATCH_TIME = match_time
                old_match.CLOSING_TIME = match_time
                old_match.MATCH_MD_TIME = match_md_time
                match_desc = old_match.MATCH_DESC
                # 更新比赛时间
                # db_session.query(Match).filter(Match.MATCH_ID == match_id).update({"MATCH_TIME": match_time, "MATCH_MD_TIME": match_md_time})
            else:
                # 比赛未录入时 创建比赛
                host_name = match[19]
                guest_name = match[20]
                # Arthur 获取主客队ID
                host_team_id = match[60]
                guest_team_id = match[61]
                match_desc = "%s vs %s" % (host_name, guest_name)

                match_repeated = False
                for old_match in old_matches.values():
                    # for match_ in old_matches:
                    #     _match_ = old_matches[match_]
                    if old_match.REMARK == league_name and old_match.MATCH_DESC.replace(" ", "").lower() == match_desc.replace(" ", "").lower():
                        print("--------", old_match.MATCH_WEB_ID, old_match.MATCH_WEB_ID in live_matches)

                        old_match_id = int(old_match.MATCH_WEB_ID)
                        print("++++++++", old_match.MATCH_WEB_ID, old_match_id in live_matches)
                        if old_match_id in live_matches:
                            live_matches.remove(int(old_match.MATCH_WEB_ID))
                            old_match.MATCH_TIME = match_time
                            old_match.CLOSING_TIME = match_time
                            old_match.MATCH_MD_TIME = match_md_time
                            old_web_id = old_match.MATCH_WEB_ID
                            old_match.MATCH_WEB_ID = match_web_id
                            match_id = old_match.MATCH_ID
                            match_repeated = True

                            # 重复比赛的时候赔率给他删了
                            db_session.query(MatchAttr).filter(MatchAttr.MATCH_WEB_ID == old_web_id).delete()
                            print("something enter")
                            break

                if not match_repeated:
                    match_id = str(round(time.time() * 1000))
                    new_match = Match(MATCH_ID=match_id, MATCH_DESC=match_desc, MATCH_TIME=match_time, CLOSING_TIME=match_time, MATCH_MD_TIME=match_md_time, HOST_TEAM=host_name, REMARK=league_name,
                                      GUEST_TEAM=guest_name, MATCH_WEB_ID=match_web_id, IS_GAME_OVER="0", HOST_TEAM_WEBID=host_team_id, GUEST_TEAM_WEBID=guest_team_id)
                    db_session.add(new_match)
                    #Arthur 检查是否存在重复比赛
                    same_match_hide(db_session, new_match, old_match_queries)
                # db_session.add(new_match)

            # 更新赔率
            # 处理让球盘
            wl_odds = match[71]
            if wl_mak and wl_mak != -1 and wl_odds:
                wl_ball = str(match[70])
                wl_draw = int(wl_mak / 100)
                # lose_team = "1" if match[68] else "2"
                wl_draw_bunko = "0" if wl_draw >= 0 else "1"
                wl_draw_odds = str(odds_format(abs(wl_draw)))
                # 当赢球数等于0时候,主队赢球且赔率为+的时候，设置客队为赢球方，反转平局胜负
                if wl_ball == '0' and lose_team == '1' and wl_draw_bunko == '0':
                    lose_team = "2"
                    wl_draw_bunko = "1"
                old_attr = db_session.query(MatchAttr).filter_by(MATCH_ATTR_ID=match_web_id_wl).one_or_none()
                old_match = old_matches.get(match_web_id)
                if old_attr and old_match:
                    # 让球数不变，赔率不变，(赔率大于15且让球方（LOSE_TEAM）变化或-+号（DRAW_BUNKO）平局胜负变化)
                    if old_attr.LOSE_BALL_NUM == wl_ball and old_attr.DRAW_ODDS == wl_draw_odds:
                        if int(wl_draw_odds) > 15 and ((old_attr.DRAW_BUNKO != wl_draw_bunko) and (old_attr.LOSE_TEAM == lose_team)):
                            old_match.exception = 1
                            old_match.hide = '1'
                            print('确认比赛异常，进行隐藏')
                            # print('让球方或平局胜负变化,让球方是否变化：', old_attr.LOSE_TEAM != lose_team, old_match.to_dict())
                            change_log = "赛事变盘信息(平局胜负): %s|%s 旧盘口: %s|%s%s%s, 新盘口: %s|%s%s%s  时间: %s\n" % (
                                old_match.MATCH_ID, match_desc, lose_team_dict.get(old_attr.LOSE_TEAM), wl_ball, draw_bunko_dict.get(old_attr.DRAW_BUNKO), old_attr.DRAW_ODDS,
                                lose_team_dict.get(lose_team), wl_ball, draw_bunko_dict.get(wl_draw_bunko), wl_draw_odds, datetime.now())
                            print(change_log)
                            with open("变盘日志.txt", mode='a', encoding='utf-8') as f:
                                f.write(change_log)
                        if old_attr.DRAW_BUNKO == wl_draw_bunko and old_attr.LOSE_TEAM != lose_team:
                            old_match.exception = 1
                            old_match.hide = '1'
                            print('确认比赛异常，进行隐藏')
                            # print('让球方或平局胜负变化,让球方是否变化：', old_attr.LOSE_TEAM != lose_team, old_match.to_dict())
                            change_log = "赛事变盘信息(让球方): %s|%s 旧盘口: %s|%s%s%s, 新盘口: %s|%s%s%s  时间: %s\n" % (
                                old_match.MATCH_ID, match_desc, lose_team_dict.get(old_attr.LOSE_TEAM), wl_ball, draw_bunko_dict.get(old_attr.DRAW_BUNKO), old_attr.DRAW_ODDS,
                                lose_team_dict.get(lose_team), wl_ball, draw_bunko_dict.get(wl_draw_bunko), wl_draw_odds, datetime.now())
                            print(change_log)
                            with open("变盘日志.txt", mode='a', encoding='utf-8') as f:
                                f.write(change_log)

                match_attr_desc = "胜负让球盘赔率"
                # 用于判断是否显示的赔率
                cond_odds = wl_odds * 10
                if single_odds_on and cond_odds >= odds_cond_1:
                    new_attr = MatchAttr(MATCH_ATTR_ID=match_web_id_wl, MATCH_ID=match_id, MATCH_ATTR_DESC=match_attr_desc, MATCH_ATTR_TYPE="1", ODDS="1", ODDS_GUEST="1",
                                         DRAW_BUNKO=wl_draw_bunko, DRAW_ODDS=wl_draw_odds, LOSE_TEAM=lose_team, LOSE_BALL_NUM=wl_ball, MATCH_WEB_ID=match_web_id)
                    # db_session.add(new_attr)
                    attrs.append(new_attr)
                # 混合盘 如果已存在旧赔率则不进行更新 -> 1小时更新一次
                if multi_odds_on and with_mix and cond_odds >= odds_cond_4:
                    new_attr = MatchAttr(MATCH_ATTR_ID=match_web_id_4, MATCH_ID=match_id, MATCH_ATTR_DESC=match_attr_desc, MATCH_ATTR_TYPE="4", ODDS="2", ODDS_GUEST="2",
                                         DRAW_BUNKO=wl_draw_bunko, DRAW_ODDS=wl_draw_odds, LOSE_TEAM=lose_team, LOSE_BALL_NUM=wl_ball, MATCH_WEB_ID=match_web_id)
                    # db_session.add(new_attr)
                    attrs.append(new_attr)

            # 处理大小盘
            bs_odds = match[74]
            if bs_mak and bs_mak != -1 and bs_odds:
                bs_draw = int(bs_mak / 100)
                bs_draw_bunko = "0" if bs_draw >= 0 else "1"
                bs_draw_odds = odds_format(abs(bs_draw))
                bs_ball = match[73]
                match_attr_desc = "大小球赔率"
                # 用于判断是否显示的赔率
                cond_odds = bs_odds * 10
                if single_odds_on and cond_odds >= odds_cond_2:
                    new_attr = MatchAttr(MATCH_ATTR_ID=match_web_id_bs, MATCH_ID=match_id, MATCH_ATTR_DESC=match_attr_desc, MATCH_ATTR_TYPE="2", ODDS="1", ODDS_GUEST="1",
                                         DRAW_BUNKO=bs_draw_bunko, DRAW_ODDS=bs_draw_odds, LOSE_TEAM=lose_team, LOSE_BALL_NUM=bs_ball, MATCH_WEB_ID=match_web_id)
                    # db_session.add(new_attr)
                    attrs.append(new_attr)
                # 混合盘 如果已存在旧赔率则不进行更新 -> 1小时更新一次
                if multi_odds_on and match_web_id_5 and with_mix and cond_odds >= odds_cond_5:
                    new_attr = MatchAttr(MATCH_ATTR_ID=match_web_id_5, MATCH_ID=match_id, MATCH_ATTR_DESC=match_attr_desc, MATCH_ATTR_TYPE="5", ODDS="2", ODDS_GUEST="2",
                                         DRAW_BUNKO=bs_draw_bunko, DRAW_ODDS=bs_draw_odds, LOSE_TEAM=lose_team, LOSE_BALL_NUM=bs_ball, MATCH_WEB_ID=match_web_id)
                    # db_session.add(new_attr)
                    attrs.append(new_attr)

            # 处理胜平负盘
            wld_odds = wld_odds_dict.get(match_web_id)
            if wld_odds:
                match_attr_desc = "胜平负盘赔率"
                wdl_odds, wdl_guest_odds, wdl_draw_odds = wld_odds
                if single_odds_on:
                    new_attr = MatchAttr(MATCH_ATTR_ID=match_web_id_10, MATCH_ID=match_id, MATCH_ATTR_DESC=match_attr_desc, MATCH_ATTR_TYPE="10", ODDS=wdl_odds, ODDS_GUEST=wdl_guest_odds,
                                         DRAW_BUNKO="", DRAW_ODDS=wdl_draw_odds, LOSE_TEAM="", LOSE_BALL_NUM="", MATCH_WEB_ID=match_web_id)
                    attrs.append(new_attr)

            # 确保比赛不被隐藏
            if match_web_id in hided_matches:
                old_match = old_matches[match_web_id]
                if old_match.exception != 1:
                    old_match.hide = "0"
                # db_session.query(Match).filter(Match.MATCH_ID == match_id).update({"hide": "0"})

    t1 = time.time()
    for attr in attrs:
        db_session.merge(attr)

    print("merge cost:", time.time() - t1)
    print("what's left:", len(live_matches), live_matches)

    if len(live_matches):
        # print(db_session.query(Match).filter(Match.MATCH_WEB_ID.in_(live_matches), datetime.now() + timedelta(minutes=1) >= Match.MATCH_TIME).all())
        db_session.query(Match).filter(Match.MATCH_WEB_ID.in_(live_matches), datetime.now() + timedelta(minutes=1) >= Match.MATCH_TIME).update({"hide": "1"}, synchronize_session=False)

    print("提交前耗时:", time.time() - start_time)
    db_session.commit()
    db_session.close()
    print(datetime.now(), "成功处理", match_count, "场比赛", "耗时:", time.time() - start_time)


def cache_to_redis():
    print("开始缓存到redis")
    start_time = time.time()
    db_session = DBSession()

    # cond_dict = {
    #     '1': odds_cond_1,
    #     '2': odds_cond_2,
    #     '4': odds_cond_4,
    #     '5': odds_cond_5
    # }
    cache_keys = ['single', 'mix', 'old_mix', '1', '2', 'wdl']
    cache_dicts = {
        'single': {'1', '2', '6', '10'},
        'mix': {'4', '5', '7', '11'},
        'old_mix': {'4', '5'},
        '1': {"1"},
        '2': {"2"}
    }
    # 存放各类型的 比赛: 赔率
    cache_list = {k: {} for k in cache_keys}

    match_list = db_session.query(Match).filter(and_(Match.CLOSING_TIME > datetime.now(), Match.MATCH_TIME > datetime.now())).filter(or_(Match.hide.is_(None), Match.hide != "1"))

    match_list = match_list.filter(and_(Match.IS_GAME_OVER == "0", Match.CLOSING_STATE == "0")).order_by(Match.REMARK.in_({'Spain Primera Division',
                                                                                                                           'Italy Serie A',
                                                                                                                           'Germany Bundesliga 1',
                                                                                                                           'France Ligue 1',
                                                                                                                           'English Premier League',
                                                                                                                           'English League Championship'}).desc()).all()
    matches_dict = {m.MATCH_ID: m.to_dict() for m in match_list}
    # print(">>>>matches_dict", matches_dict)

    all_attrs = db_session.query(MatchAttr).filter(MatchAttr.MATCH_ID.in_(matches_dict)).all()

    cache_attrs = []
    for attr in all_attrs:
        attr = attr.to_dict()
        match_id = attr["MATCH_ID"]
        attr_type = attr['MATCH_ATTR_TYPE']
        if attr_type in {'6', '7'}:
            attr['REAL_ODDS'] = "%s/%s" % (attr['ODDS'], attr['ODDS_GUEST'])
        else:
            # if attr['COND_ODDS'] < cond_dict[attr_type]:
            #     continue
            sign = "-" if attr['DRAW_BUNKO'] == "1" else "+"
            attr['REAL_ODDS'] = "%s%s%s" % (attr['LOSE_BALL_NUM'], sign, attr['DRAW_ODDS'])
        cache_attrs.append(attr)

        for k, v in cache_dicts.items():
            if attr_type not in v:
                continue
            if match_id not in cache_list[k]:
                cache_list[k][match_id] = matches_dict[match_id].copy()
                cache_list[k][match_id]['ATTR'] = []
            cache_list[k][match_id]['ATTR'].append(attr)

    # print("try>>>>>>>>>", cache_list['1'])

    # 最终结果
    items = {k: [] for k in cache_keys}

    for match in match_list:
        match_id = match.MATCH_ID
        for k, v in cache_list.items():
            if match_id in v:
                # print("about to append:", v[match_id])
                items[k].append(v[match_id])
    # print("we got the this items:", items['mix'])
    for k, v in items.items():
        Redis.set("live_matchs|%s" % k, json.dumps(v), 240)
    Redis.set("live_odds", json.dumps(cache_attrs), 240)
    db_session.close()
    print("缓存完毕,耗时:", time.time() - start_time)
    # print("????", Redis.get("live_matchs|mix"))


if __name__ == '__main__':
    # get_matches(with_mix=True)
    # cache_to_redis()

    cnt = 0
    #while True:
    # Arthur 取消轮询，定时任务调用
    try:
        # if cnt % 60 == 0:
        #     # get_matches(with_mix=True)
        #     cnt = 0
        # else:
        #     pass
        # get_matches()
        get_matches(with_mix=True)
        # cache_to_redis()
        # cnt += 1
    except Exception as e:
        print("get_matches run error:", e)
        # traceback.print_stack()
    try:
        cache_to_redis()
    except Exception as e:
        print("cache_to_redis run error:", e)
        # traceback.print_stack()

        #time.sleep(120)
