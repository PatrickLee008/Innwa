from app_server import app, db, auth, app_opt
from flask import jsonify, Blueprint, request, g
from app_server.model.UploadedImageModel import UploadedImage
from sqlalchemy import or_, func

r_up_image = Blueprint('up_image', __name__)


@r_up_image.route('/get', methods=['GET'])
# @auth.login_required
def get_images():
    """
                    @@@
                    #### Args:
                           {
                                current_page: "",
                                limit: "",
                            }
                    #### Returns::
                            {
                                'code': 20000,
                                'items': [u.to_dict() for u in image_list],
                            }
                """
    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)

    image_list = UploadedImage.query

    image_list = image_list.offset((current_page - 1) * limit).limit(limit).all()

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in image_list],
    })

