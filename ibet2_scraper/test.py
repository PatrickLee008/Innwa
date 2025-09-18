from operator import and_

import requests
import time
from Orm import DBSession, Match
from ibet_match import same_match_hide,is_same_match


#headers = {"Host": "47.254.197.27"}
#proxy = {'https': "127.0.0.1:10809"}
#resp = requests.get("https://ibet789.com/", proxies=proxy)
#print("resp", resp.text)

# with open("D:/tmp/爬虫/match_list0323.txt", "r", encoding="utf-8") as file:
#     content = file.read()
#
# print(content)

def match_test():
    # 示例测试
    match1 = "SV Ried vs SK Sturm Graz Am"
    match2 = "SV Ried vs Sturm Graz II"

    is_same, similarity = is_same_match(match1, match2)
    print(f"{match1} 和 {match2} 是否同一比赛: {is_same} (相似度: {similarity:.2f})")
    # 计算用时
    start_time = time.time()
    db_session = DBSession()
    newMatch = db_session.query(Match).filter(Match.MATCH_ID=="1745715617625").first()
    #matchs = db_session.query(Match).filter(Match.MATCH_TIME>"2025-04-28").with_entities(Match.MATCH_DESC).distinct().all()
    matchs = db_session.query(Match).filter(Match.MATCH_TIME >= "2025-04-01").all()

    length = len(matchs)
    print(f"共有{length}场比赛")
    for match in matchs:
        same_match_hide(db_session, match, matchs,False,True)

    end_time = time.time()
    print(f"计算用时: {end_time - start_time:.2f}秒")
match_test()