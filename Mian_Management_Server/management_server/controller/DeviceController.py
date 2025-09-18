from management_server import app, db, auth, user_opt
from flask import g, request, jsonify, Blueprint
from management_server.utils import OrmUttil
from management_server.model.DeviceModel import Device
from sqlalchemy import or_, func, and_
import traceback

r_device = Blueprint('device', __name__)


# 获取所有用户列表
@r_device.route('/get', methods=['GET'])
@auth.login_required
def get_device_list():
    """
                @@@
                #### Args:
                        current_page = request.args.get('page', type=int, default=1)
                        limit = request.args.get('limit', type=int, default=20)

                        key_word = request.args.get('key_word')
                        start_time = request.args.get('start_time')
                        end_time = request.args.get('end_time')
                #### Returns::
                        {
                            'code': 20000,
                            'items': [u.to_dict() for u in mem_list],
                            'total': total
                        }
            """

    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)

    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    card_list = Device.query

    if key_word:
        card_list = card_list.filter(
            or_(Device.ID.like('%{}%'.format(key_word)), Device.Name.like('%{}%'.format(key_word)),
                Device.MacAddress.like('%{}%'.format(key_word)), Device.Creator.like('%{}%'.format(key_word))))

    if start_time:
        card_list = card_list.filter(Device.CreateTime >= start_time)

    if end_time:
        end_time += ' 23:59:59'
        card_list = card_list.filter(Device.CreateTime <= end_time)

    total = card_list.count()

    card_list = card_list.offset((current_page - 1) * limit).limit(limit).all()

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in card_list],
        'total': total
    })


@r_device.route('/add', methods=['POST'])
@auth.login_required
def add_device():
    """
    @@@
    #### Args:
            Name = Column(String(255), comment="名称")
            MacAddress = Column(String(128), comment="物理地址")
            Enable = Column(Boolean, comment="是否启用")
            Creator = Column(String(64), comment="创建者")

            CreateTime = Column(DateTime, default=datetime.now, comment="创建时间")
            LastLoginTime = Column(DateTime, comment="最后登录时间")
            Remark = Column(String(255), comment="备注")
    #### Returns::
            {'code': 20000, 'message': "Add Successful."}
            {'code': 50001, 'message': "Unknown Error."}
    """

    args = request.get_json()
    card_name = args.get("Name")
    card_num = args.get("MacAddress")

    try:
        old_devices = Device.query.filter(Device.Name == card_name).all()
        if len(old_devices):
            return jsonify({'code': 50002, 'message': "Name already exists."})
        old_devices = Device.query.filter(Device.MacAddress == card_num).all()
        if len(old_devices):
            return jsonify({'code': 50003, 'message': "Address already exists."})

        device = Device()
        OrmUttil.set_field(device, args)
        device.Creator = g.user.ACCOUNT
        db.session.add(device)
        db.session.commit()
        user_opt.send({
            "route": "设备管理",
            "operate": "添加设备",
            "key_word": device.ID,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "Add Successful."})
    except Exception as e:
        print("add match error:", e)
    return jsonify({'code': 50001, 'message': "Unknown Error."})


@r_device.route('/remove', methods=['GET'])
@auth.login_required
def remove_device():
    """
            @@@
            #### Args:
                    ID: 51
            #### Returns::
                    {'code': 20000, 'message': "Delete Successful."}
                    {'code': 50001, 'message': "Unknown Error."}
        """
    remove_id = request.args.get('ID')

    try:
        if not remove_id:
            return jsonify({'code': 50002, 'message': "Param Required: ID"})
        Device.query.filter_by(ID=remove_id).delete()
        db.session.commit()
        user_opt.send({
            "route": "设备管理",
            "operate": "删除设备",
            "key_word": remove_id,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "Delete Successful."})
    except Exception as e:
        print("remove_bet_account del error: ", e)
    return jsonify({'code': 50001, 'message': "Unknown Error."})


@r_device.route('/edit', methods=['POST'])
@auth.login_required
def edit_device():
    """
            @@@
            #### Args:
                    ID: 51
                    Name = Column(String(255), comment="名称")
                    MacAddress = Column(String(128), comment="物理地址")
                    Enable = Column(Boolean, comment="是否启用")
                    Creator = Column(String(64), comment="创建者")

                    CreateTime = Column(DateTime, default=datetime.now, comment="创建时间")
                    LastLoginTime = Column(DateTime, comment="最后登录时间")
                    Remark = Column(String(255), comment="备注")
            #### Returns::
                    {'code': 20000, 'message': "Edit Successful."}
                    {'code': 50001, 'message': "Unknown Error."}
        """
    args = request.get_json()
    edit_id = args.get('ID')

    if edit_id:
        card = Device.query.filter_by(ID=edit_id).one_or_none()
        if not card:
            return jsonify({'code': 50002, 'message': "Bankcard Not Exists."})
        args.pop('ID')
        OrmUttil.set_field(card, args)
        db.session.commit()
        user_opt.send({
            "route": "设备管理",
            "operate": "修改设备",
            "key_word": edit_id,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "Edit Successful."})
    else:
        return jsonify({'code': 50001, 'message': "Unknown Error."})
