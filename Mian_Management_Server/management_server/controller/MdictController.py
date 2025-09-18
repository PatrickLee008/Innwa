from management_server import app, db, auth, user_opt
from flask import jsonify, Blueprint, request, g
from management_server.model.MDictModel import MDict
from management_server.utils import OrmUttil

r_conf = Blueprint('config', __name__)


@r_conf.route('/get_commissions', methods=['GET'])
@auth.login_required
def get_commissions():
    """
        佣金配置
    @@@
    #### Args:
    #### Returns::
                {
                    "code": 20000,
                    "items": [
                      {
                        "MDICT_ID": "",
                        "CONTENT": "40",
                        "NAME": "波胆下注平台佣金比例",
                        "TITLE": "平台佣金比例",
                        "TYPE": "ratio"
                      },
                      ...
                    ]
                }
                {'code': 50001, 'message': "未知错误"}
    """
    com_configs = MDict.query.filter(MDict.MDICT_ID.in_({'444', '554', '555', '666'}))

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in com_configs]
    })


@r_conf.route('/get_limits', methods=['GET'])
@auth.login_required
def get_limits():
    """
       限额配置
    @@@
    #### Args:
    #### Returns::
            {
                "code": 20000,
                "items": [
                  {
                    "MDICT_ID": "",
                    "CODE": "1",
                    "CONTENT": "1000000",
                    "NAME": "大小下注最大最小金额",
                    "TITLE": "bigsmallposition",
                    "TYPE": "minAndMaxMoney"
                  },
                  ...
                ]
            }
            {'code': 50001, 'message': "未知错误"}
    """
    com_configs = MDict.query.filter(MDict.MDICT_ID.in_({'888', '999', '13', '30', '31', '32', '33', '889'})).order_by(MDict.CREATOR_TIME).all()
    print("the limits:", [u.to_dict() for u in com_configs])
    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in com_configs]
    })


@r_conf.route('/get_update', methods=['GET'])
@auth.login_required
def get_update():
    com_configs = MDict.query.filter(MDict.MDICT_ID.in_({'8888'})).order_by(MDict.CREATOR_TIME).all()
    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in com_configs]
    })


@r_conf.route('/get_scraps', methods=['GET'])
@auth.login_required
def get_scraps():
    """
        采集配置
    @@@
    #### Args:
    #### Returns::
            {
                "code": 20000,
                "items": [
                  {
                    "MDICT_ID": "",
                    "CODE": null,
                    "CONTENT": "kkuummtfaj",
                    "NAME": "采集网账号",
                    "TITLE": null,
                    "TYPE": "account"
                  },
                  ...
                ]
            }
            {'code': 50001, 'message': "未知错误"}
    """
    com_configs = MDict.query.filter(MDict.MDICT_ID.in_({'14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '40', '41'}))

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in com_configs]
    })


@r_conf.route('/get_other_setting', methods=['GET'])
@auth.login_required
def get_other_setting():
    com_configs = MDict.query.filter(MDict.MDICT_ID.in_({'24', '25', '29', '26', '1333'}))

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in com_configs]
    })


@r_conf.route('/edit', methods=['POST'])
@auth.login_required
def edit_conf():
    """
    @@@
    #### Args:
            {
               "MDICT_ID": "",
               "NAME": "",
               "TYPE": "",
               "CODE": "",
               "TITLE": "",
               "CONTENT": "",
               "URL": "",
               "REMARK": ""
            }
    #### Returns::
            {'code': 20000, 'message': "修改成功"}
            {'code': 50001, 'message': "未知错误"}
    """
    args = request.get_json()
    edit_id = args.get('MDICT_ID')
    print("editing:", args)
    try:
        config = MDict.query.filter_by(MDICT_ID=edit_id).one_or_none()
        OrmUttil.set_field(config, args)
        config.UPDATOR = g.user.NAME
        db.session.commit()
        user_opt.send({
            "operate": "修改配置",
            "route": "配置管理",
            "key_word": edit_id,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "修改成功"})
    except Exception as e:
        print(e)
        return jsonify({
            'code': 50001,
            'message': "未知错误"
        })
