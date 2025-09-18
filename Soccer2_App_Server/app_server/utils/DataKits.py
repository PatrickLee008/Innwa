# 数据处理包
import json
from datetime import datetime, timedelta
import difflib
import re
from typing import Tuple


def normalize_team_name(name: str) -> str:
    """
    标准化队名：
    - 转换为小写
    - 移除常见缩写和符号（如FC、.等）
    - 移除多余空格
    """
    # 定义需要移除的常见词（可根据需求扩展）
    stop_words ={'fk','baku','fc', 'club', 'cf', 'team', 'ac', 'sc', '&', '.', 'n', 'ksa', 'sd', 'cd', 'rc', 'as', 'us', 'rs', 'ts', 'fcw', 'fco', 'rsc', 'cfr', 'ksc', 'msc'}
    # 移除特殊符号并转换为小写
    name = re.sub(r'[^\w\s]', '', name.lower())
    # 按空格分割并过滤停用词
    words = [word for word in name.split() if word not in stop_words]
    return ' '.join(words).strip()


def calculate_similarity(str1: str, str2: str) -> float:
    """计算两个字符串的相似度（基于Jaro-Winkler改进的SequenceMatcher）"""
    return difflib.SequenceMatcher(None, str1, str2).ratio()


def is_same_match(home1: str, away1: str,home2: str, away2: str, threshold: float = 0.90) -> Tuple[bool, float, str]:
    """
    判断两场比赛是否队名相同：
    1. 分割主队和客队
    2. 标准化名称
    3. 计算主队和客队的相似度
    4. 综合判断是否超过阈值
    """
    # 分割主队和客队
    # home1, away1 = map(normalize_team_name, match1.split(' vs '))
    # home2, away2 = map(normalize_team_name, match2.split(' vs '))
    #print(f"对比{home1} vs {away1}，{home2} vs {away2}")
    # 计算主队和客队的相似度
    #home_sim = calculate_similarity(home1, home2)
    #away_sim = calculate_similarity(away1, away2)
    # 综合相似度（取最小值确保双方都匹配）
    #similarity = min(home_sim, away_sim)

    # 计算最优匹配相似度（考虑顺序可能互换）
    similarityHom1AndHome2 = calculate_similarity(home1, home2)
    similarityAway1AndAway2 = calculate_similarity(away1, away2)
    similarityHom1AndAway2 = calculate_similarity(home1, away2)
    similarityAway1AndHome2 = calculate_similarity(away1, home2)
    # 如果有1个相似度=1的则认为是同一场比赛
    same_team = ''
    if similarityHom1AndHome2 == 1:
        same_team = home1
    elif similarityAway1AndAway2 == 1:
        same_team = away1
    elif similarityHom1AndAway2 == 1:
        same_team = home1
    elif similarityAway1AndHome2 == 1:
        same_team = away1
    # 综合判断是否超过阈值
    if same_team != '':
        similarity = 1
    else:
        similarity = max(
            calculate_similarity(home1, home2) + calculate_similarity(away1, away2),
            calculate_similarity(home1, away2) + calculate_similarity(away1, home2)
        ) / 2
    # if similarity >= threshold:
    #     print(f"对比{home1}和{home2}，相似度为{calculate_similarity(home1, home2)}")
    #     print(f"对比{away1}和{away2}，相似度为{calculate_similarity(away1, away2)}")
    return similarity >= threshold, similarity, same_team

def find_matching_games(live_matches, lives_videos, time_threshold_minutes=30, name_similarity_threshold=0.8):
    """
    找出两个数据集中匹配的比赛，基于队伍名称和比赛时间的相似度

    参数:
        matches: 第一个数据集 (包含HOST_TEAM和MATCH_TIME的字典列表)
        dataset2: 第二个数据集 (包含home和time_start的字典列表)
        time_threshold_minutes: 允许的最大时间差(分钟)
        name_similarity_threshold: 队伍名称相似度的最低阈值(0-1)

    返回:
        包含匹配比赛对和相似度得分的列表
    """
    matches = []

    for game2 in lives_videos:
        for game1 in live_matches:
            # 处理队伍名称：转小写、移除(n)标记、去除空格
            home1 = game1.get('HOST_TEAM', '').lower().strip()
            away1 = game1.get('GUEST_TEAM', '').lower().strip()
            home2 = game2.get('home', '').lower().strip()
            away2 = game2.get('guest', '').lower().strip()

            # 计算名称相似度 (使用difflib序列匹配器)
            same, name_similarity, same_team = is_same_match(home1, away1, home2, away2, threshold=name_similarity_threshold)

            # 处理比赛时间
            try:
                # 将字符串时间转换为datetime对象
                time1 = datetime.strptime(game1['MATCH_TIME'], '%Y-%m-%d %H:%M:%S')
                time2 = datetime.strptime(game2['time_start'], '%Y-%m-%d %H:%M:%S')

                # 计算时间差(绝对值)
                time_diff = abs((time1 - time2).total_seconds() / 60)  # 转换为分钟

                # 输出调试比对信息
                #print(f"比赛名称1: {host_team1}, 比赛名称2: {home_team2}")
                #print(f"比赛时间1: {time1}, 比赛时间2: {time2}")
                #print(f"比赛名称相似度: {name_similarity:.2f}, 比赛时间差: {time_diff:.2f}")
                # 如果名称和时间都满足阈值条件
                if (name_similarity >= name_similarity_threshold and
                        time_diff <= time_threshold_minutes):
                    # 匹配成功
                    print(f"匹配成功: {game1['MATCH_DESC']} vs {game2['name']}")
                    game2['matchInfo'] = game1
                    break

                    # 记录匹配结果
                    matches.append({
                        'dataset1_match': game1['MATCH_DESC'],
                        'dataset2_match': game2['name'],
                        'host_team_similarity': name_similarity,
                        'time_difference_minutes': time_diff,
                        'dataset1_info': {
                            'MATCH_ID': game1['MATCH_ID'],
                            'MATCH_TIME': game1['MATCH_TIME'],
                            'HOST_TEAM': game1['HOST_TEAM'],
                            'GUEST_TEAM': game1['GUEST_TEAM']
                        },
                        'dataset2_info': {
                            'id': game2['id'],
                            'time_start': game2['time_start'],
                            'home': game2['home'],
                            'away': game2['away'],
                            'league': game2['league']
                        }
                    })

            except KeyError as e:
                print(f"缺少必要字段: {e}")
                continue
            except ValueError as e:
                print(f"时间格式错误: {e}")
                continue

    # 按名称相似度排序(从高到低)
    matches.sort(key=lambda x: x['host_team_similarity'], reverse=True)

    return matches
