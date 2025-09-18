from management_server import app, db, auth, user_opt
from flask import jsonify, Blueprint, request, g
from management_server.model.UploadedImageModel import UploadedImage
from sqlalchemy import or_, func
import time
import os

r_up_image = Blueprint('up_image', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'JPG', 'PNG', 'gif', 'GIF'}


@r_up_image.route('/get', methods=['GET'])
@auth.login_required
def get_up_images():
    """
                    @@@
                    #### Args:
                           {
                                current_page: "",
                                limit: "",
                                key_word: "",
                                start_time: "",
                                end_time: "",
                            }
                    #### Returns::
                            {
                                'code': 20000,
                                'items': [u.to_dict() for u in up_image_list],
                            }
                """
    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)
    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    up_image_list = UploadedImage.query
    if key_word:
        up_image_list = up_image_list.filter(or_(UploadedImage.ID.like('%{}%'.format(key_word)), UploadedImage.TITLE.like('%{}%'.format(key_word)), UploadedImage.CONTENT.like('%{}%'.format(key_word))))

    if start_time:
        up_image_list = up_image_list.filter(UploadedImage.CREATE_TIME >= start_time)

    if end_time:
        end_time += ' 23:59:59'
        up_image_list = up_image_list.filter(UploadedImage.CREATE_TIME <= end_time)

    up_image_list = up_image_list.offset((current_page - 1) * limit).limit(limit).all()

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in up_image_list],
    })


@r_up_image.route('/edit', methods=['POST'])
@auth.login_required
def edit_up_image():
    """
    @@@
    #### Args:
            {
               "ID": 1,
               "NAME": "ad_1",
               file : File "图片"
            }
    #### Returns::
            {'code': 20000, 'message': "修改成功"}
            {'code': 50001, 'message': "未知错误"}
    """
    args = request.form.to_dict()
    edit_id = args.get('ID')
    name = args.get('NAME')
    try:
        up_image = UploadedImage.query.filter_by(ID=edit_id).one_or_none()
        if name:
            up_image.NAME = name
        picture = request.files.get('file')
        if picture:
            path = app.config['APP_IMAGE_DIR']
            # 图片后缀
            suffix = picture.filename.rsplit('.', 1)[1]
            if suffix not in ALLOWED_EXTENSIONS:
                return jsonify({
                    'code': 50002,
                    'message': "文件格式不正确"
                })

            # 删除原有图片
            if os.path.isfile(os.path.join(path, up_image.ADDRESS)):
                os.remove(os.path.join(path, up_image.ADDRESS))

            pic_name = "%s_%s.%s" % (up_image.NAME, int(round(time.time() * 1000)), suffix)

            up_image.ADDRESS = pic_name
            picture.save(os.path.join(path, pic_name))

        db.session.commit()
        # user_opt.send({
        #     "operate": "修改图片",
        #     "route": "图片管理",
        #     "key_word": edit_id,
        #     "user": g.user.ACCOUNT
        # })
        return jsonify({'code': 20000, 'message': "修改成功"})
    except Exception as e:
        print(e)
    return jsonify({
        'code': 50001,
        'message': "未知错误"
    })


@r_up_image.route('/add', methods=['POST'])
@auth.login_required
def add_up_image():
    """
    @@@
    #### Args:
            {
               "NAME": 'ad_1',
                file : File "图片"
            }
    #### Returns::
            {'code': 20000, 'message': "添加成功"}
            {'code': 50001, 'message': "未知错误"}
    """

    args = request.form

    try:
        up_image = UploadedImage(NAME=args.get('NAME'))
        picture = request.files.get('file')

        if not picture:
            return jsonify({
                'code': 50002,
                'message': "图片不能为空"
            })

        path = app.config['APP_IMAGE_DIR']
        # 图片后缀
        suffix = picture.filename.rsplit('.', 1)[1]
        if suffix not in ALLOWED_EXTENSIONS:
            return jsonify({
                'code': 50002,
                'message': "文件格式不正确"
            })
        rand_id = int(round(time.time() * 1000))
        pic_name = "%s_%s.%s" % (args.get('NAME'), rand_id, suffix)
        picture.save(os.path.join(path, pic_name))

        up_image.ADDRESS = pic_name
        
        db.session.add(up_image)
        db.session.commit()
        user_opt.send({
            "operate": "添加图片",
            "route": "图片管理",
            "key_word": up_image.ID,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "添加成功"})
    except Exception as e:
        print("add match error:", e)

    return jsonify({'code': 50001, 'message': "未知错误"})


@r_up_image.route('/remove', methods=['POST'])
@auth.login_required
def remove_up_image():
    """
        @@@
        #### Args:
                {
                   "ID": 1,
                }
        #### Returns::
                {'code': 20000, 'message': "删除成功"}
                {'code': 50001, 'message': "未知错误"}
        """
    args = request.get_json()
    remove_id = args.get('ID')
    
    try:
        up_image = UploadedImage.query.filter_by(ID=remove_id).one_or_none()
        # 删除原有图片
        if up_image.ADDRESS:
            path = app.config['APP_IMAGE_DIR']

            if os.path.isfile(os.path.join(path, up_image.ADDRESS)):
                os.remove(os.path.join(path, up_image.ADDRESS))

        db.session.remove(up_image)
        db.session.commit()
        user_opt.send({
            "operate": "删除图片",
            "route": "图片管理",
            "key_word": remove_id,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "删除成功"})
    except Exception as e:
        print(e)
        return jsonify({
            'code': 50001,
            'message': "未知错误"
        })
