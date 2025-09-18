import random
import uuid
from datetime import datetime
from typing import List

from flask import jsonify

# 工具包
class Kits:
    @staticmethod
    def rt_data(data):
        # 先判断是否是简单数据类型，然后再判断是否是字典类型，最后判断是否是对象类型
        # 简单数据类型：str、int、float、bool、list、tuple、set、dict
        # 字典类型：字典类型
        # 对象类型：对象类型
        # 最后返回json数据
        if isinstance(data, (str, int, float, bool, list, tuple, set, dict)):
            return jsonify({'code': 20000, 'data': data})
        elif not isinstance(data, dict):
            data = data.to_dict() if hasattr(data, 'to_dict') else data
        return jsonify({'code': 20000, 'data': data})

    @staticmethod
    def rt_ok(message):
        return jsonify({'code': 20000, 'message': message})

    @staticmethod
    def rt_code(code, message, data):
        return jsonify({'code': 20000, 'message': message, 'data': data})

    @staticmethod
    def rt_error(message):
        response = jsonify({'code': 50002, 'message': message})
        response.status_code = 500
        return response

    def is_empty(arg):
        # 判断是否存在空值，存在则返回True
        return True if arg is None or arg == '' or arg == [] or arg == {} or arg == 'null' or arg == 'undefined' or arg == 'None' else False

    @staticmethod
    def is_all_empty(*args):
        # 判断是否存在空值，存在则返回True
        for arg in args:
            empty = Kits.is_empty(arg)
            if not empty:
                return False
        return True

    @staticmethod
    def is_not_empty(*args):
        # 判断所有参赛是否都是非空，有空则返回False
        for arg in args:
            if arg is None or arg == '' or arg == [] or arg == {} or arg == 'null' or arg == 'undefined' or arg == 'None':
                return False
        return True

    #生成UUID
    @staticmethod
    def generate_uuid():
        # 换成雪花ID
        #return _snowflake_gen.generate_id()
        return str(uuid.uuid4()).replace('-', '').upper()

    # 获取客户端信息
    @staticmethod
    def client_info(request):
        # 获取客户端信息
        # {"os": "Windows", "device": "Unknown", "is_bot": false, "browser": "Edge", "ip_address": "2405:9800:b910:1784:18b:34dd:1bce:9cfb", "last_login": "2025-02-26T04:01:52.722Z", "user_agent": "Edge 133.0.0.0 Windows 10 undefined Blink 133.0.0.0 amd64"}
        # 解析 User-Agent 字符串
        user_agent = request.headers.get('User-Agent')
        if user_agent:
            #解析 User-Agent 字符串
            user_agent_info = user_agent
        else:
            user_agent_info = None
        if not user_agent_info:
            return {}

        # 获取客户端信息
        info = {
            #"os": user_agent_info.os.family if user_agent_info.os else "Unknown",
            #"device": user_agent_info.device.family if user_agent_info.device else "Unknown",
            #"is_bot": user_agent_info.is_bot if user_agent_info else False,
            #"browser": user_agent_info.browser.family if user_agent_info.browser else "Unknown",
            "ip_address": request.remote_addr,
            "last_login": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            #"user_agent": user_agent
        }
        return info  # 返回客户端信息