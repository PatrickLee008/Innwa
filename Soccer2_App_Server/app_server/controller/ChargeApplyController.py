import time
from sqlalchemy import or_, func
from app_server import app, db, auth
from app_server.model.ChargeApplyModel import ChargeApply
from flask import g, request, jsonify, Blueprint
from app_server.utils import OrmUttil
import os

charge_apply = Blueprint('charge_apply', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'JPG', 'PNG', 'gif', 'GIF'}


@charge_apply.route('/add', methods=['POST'])
@auth.login_required
def add_apply():
    """

                @@@
                #### Args:
                        MONEY : String(64) "金额"
                        REMARK : String(256) "备注：申请说明"
                        file : File "充值图片"
                #### Returns::
                        {'code': 20000, 'message': "add successful."}
                        {'code': 50001, 'message': "unknown error."}
            """
    # json.loads(request.form.get('student'))
    print("apply args:", request.form)
    args = request.form

    try:
        apply_id = int(round(time.time() * 1000))
        apply = ChargeApply(ID=apply_id, USER_ID=g.user.USER_ID, NICK_NAME=g.user.NICK_NAME, MONEY=args.get('MONEY'), REMARK=args.get('REMARK') or "")

        picture = request.files.get('file')

        if not picture:
            return jsonify({
                'code': 50002,
                'message': "图片不能为空"
            })

        path = app.config['CHARGE_APPLY_PIC_DIR']
        # 图片后缀
        suffix = picture.filename.rsplit('.', 1)[1]
        if suffix not in ALLOWED_EXTENSIONS:
            return jsonify({
                'code': 50002,
                'message': "文件格式不正确"
            })
        pic_name = "%s_%s.%s" % (g.user.USER_ID, apply_id, suffix)
        picture.save(os.path.join(path, pic_name))

        apply.PICTURE = pic_name

        db.session.add(apply)
        db.session.commit()
        return jsonify({'code': 20000, 'message': "add successful."})
    except Exception as e:
        print("add charge_apply error:", e)

    return jsonify({'code': 50001, 'message': "unknown error."})


@charge_apply.route('/edit', methods=['POST'])
@auth.login_required
def edit_apply():
    """

                @@@
                #### Args:
                        APPLY_ID : 申请ID
                        MONEY : String(64) "金额"
                        REMARK : String(256) "备注：申请说明"
                        PICTURE : File "充值图片"
                #### Returns::
                        {'code': 20000, 'message': "add successful."}
                        {'code': 50001, 'message': "unknown error."}
            """
    args = request.get_json()

    try:
        apply_id = args['APPLY_ID']
        apply = ChargeApply.query.filter_by(ID=apply_id).one_or_none()
        if args['PICTURE']:
            picture = request.files.get('PICTURE')
            path = app.config['CHARGE_APPLY_PIC_DIR']
            # 图片后缀
            suffix = picture.filename.rsplit('.', 1)[1]
            if suffix not in ALLOWED_EXTENSIONS:
                return jsonify({
                    'code': 50002,
                    'message': "文件格式不正确"
                })

            # 删除原有图片
            if os.path.isfile(os.path.join(path, apply.PICTURE)):
                os.remove(os.path.join(path, apply.PICTURE))

            pic_name = "%s_%s.%s" % (g.user.USER_ID, int(round(time.time() * 1000)), suffix)
            picture.save(os.path.join(path, pic_name))

            args['PICTURE'] = pic_name

        OrmUttil.set_field(apply, request.args)

        db.session.add(apply)
        db.session.commit()
        return jsonify({'code': 20000, 'message': "add successful."})
    except Exception as e:
        print("add match error:", e)

    return jsonify({'code': 50001, 'message': "unknown error."})


@charge_apply.route('/delete', methods=['POST'])
@auth.login_required
def delete_apply():
    """

                @@@
                #### Args:
                        APPLY_ID : 申请ID
                #### Returns::
                        {'code': 20000, 'message': "删除成功"}
                        {'code': 50001, 'message': "unknown error."}
            """
    args = request.get_json()

    try:
        apply_id = args['APPLY_ID']
        apply = ChargeApply.query.filter_by(ID=apply_id).delete()

        # 删除原有图片
        if args['PICTURE']:
            path = app.config['CHARGE_APPLY_PIC_DIR']

            if os.path.isfile(os.path.join(path, apply.PICTURE)):
                os.remove(os.path.join(path, apply.PICTURE))
        db.session.commit()
        return jsonify({'code': 20000, 'message': "删除成功"})
    except Exception as e:
        print("add match error:", e)

    return jsonify({'code': 50001, 'message': "unknown error."})


# 获取订单列表
@charge_apply.route('/get', methods=['GET'])
@auth.login_required
def get_apply_list():
    """
                @@@
                #### Args:
                        current_page = request.args.get('page', type=int, default=1)
                        limit = request.args.get('limit', type=int, default=20)
                        key_word = request.args.get('key_word')
                        start_time = request.args.get('start_time')
                        end_time = request.args.get('end_time')
                        is_pay =
                #### Returns::
                        {
                            'code': 20000,
                            'items': [u.to_dict() for u in order_list],
                            'total': total,
                            'total_amount': total_amount
                        }
            """

    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)
    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    charge_list = ChargeApply.query.filter_by(USER_ID=g.user.USER_ID)

    if key_word:
        charge_list = charge_list.filter(
            or_(ChargeApply.USER_ID.like('%{}%'.format(key_word)), ChargeApply.NICK_NAME.like('%{}%'.format(key_word)),
                ChargeApply.REMARK.like('%{}%'.format(key_word))))

    if start_time:
        start_time += ' 00:00:00'
        charge_list = charge_list.filter(ChargeApply.CREATE_TIME >= start_time)

    if end_time:
        end_time += ' 23:59:59'
        charge_list = charge_list.filter(ChargeApply.CREATE_TIME <= end_time)

    total_amount = charge_list.with_entities(func.sum(ChargeApply.MONEY)).scalar() or 0

    charge_list = charge_list.offset((current_page - 1) * limit).limit(limit).all()
    total = len(charge_list)

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in charge_list],
        'total': total,
        'total_amount': total_amount
    })
