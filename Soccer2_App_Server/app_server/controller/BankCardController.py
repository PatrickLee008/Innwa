from app_server import app, db, auth, app_opt
from app_server.model.BankCardModel import BankCard
from app_server.model.BankTypeModel import BankType
from flask import g, request, jsonify, Blueprint
from app_server.utils import OrmUttil
import uuid
import hashlib

bank_card = Blueprint('bank_card', __name__)


@bank_card.route('/get', methods=['GET'])
@auth.login_required
def get_bank_cards():
    """
        @@@
        #### Args:
                None
        #### Returns::
                {'code': 20000, 'bank_cards': [{BankCardModel},...]}
                {'code': 50001, 'message': "unknown error."}
        """
    try:
        bank_cards = BankCard.query.filter_by(USER_ID=g.user.USER_ID).all()
        return jsonify({'code': 20000, 'bank_cards': [u.to_dict() for u in bank_cards]})
    except Exception as e:
        print("user info error:", e)


@bank_card.route('/add', methods=['POST'])
@auth.login_required
def add_bank_card():
    """
    @@@
    #### Args:
            CARD_NUM = Column(String(64), comment="银行卡号")              必填
            BANK_TYPE = Column(String(64), comment="银行")
    #### Returns::
            {'code': 20000, 'message': "add successful."}
            {'code': 50001, 'message': "unknown error."}
    """

    args = request.get_json()
    card_num = args.get("CARD_NUM")

    try:
        card = BankCard.query.filter_by(CARD_NUM=card_num).one_or_none()
        if card:
            return jsonify({'code': 50002, 'message': "该银行卡已经被绑定"})
        card = BankCard(CARD_NUM=card_num, USER_ID=g.user.USER_ID, BANK_TYPE=args.get("BANK_TYPE"))
        db.session.add(card)

        db.session.commit()
        return jsonify({'code': 20000, 'message': "绑定成功"})
    except Exception as e:
        db.session.rollback()
        print("add card error:", e)

    return jsonify({'code': 50001, 'message': "unknown error."})


@bank_card.route('/edit', methods=['POST'])
@auth.login_required
def edit_bank_card():
    """
            @@@
            #### Args:
                    ID : Integer
                    CARD_NUM = Column(String(64), comment="银行卡号")
                    BANK_TYPE = Column(String(64), comment="银行类型")
            #### Returns::
                    {'code': 20000, 'message': "edit successful."}
                    {'code': 50001, 'message': "unknown error."}
        """
    args = request.get_json()
    edit_id = args.get("ID")

    try:
        card = BankCard.query.filter_by(ID=edit_id).one_or_none()
        args.pop("ID")
        OrmUttil.set_field(card, args)
        db.session.commit()
        return jsonify({'code': 20000, 'message': "edit successful."})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 50001, 'message': "unknown error."})


@bank_card.route('/delete', methods=['POST'])
@auth.login_required
def delete_bank_card():
    """
            @@@
            #### Args:
                    ID : Integer
            #### Returns::
                    {'code': 20000, 'message': "解绑成功"}
                    {'code': 50001, 'message': "unknown error."}
        """
    args = request.get_json()
    edit_id = args.get("ID")

    try:
        BankCard.query.filter_by(ID=edit_id).delete()
        db.session.commit()
        return jsonify({'code': 20000, 'message': "解绑成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 50001, 'message': "unknown error."})


@bank_card.route('/set_default', methods=['POST'])
@auth.login_required
def set_default_bank_card():
    """
            @@@
            #### Args:
                    ID : Integer
            #### Returns::
                    {'code': 20000, 'message': "解绑成功"}
                    {'code': 50001, 'message': "unknown error."}
        """
    args = request.get_json()
    edit_id = args.get("ID")

    try:
        card = BankCard.query.filter_by(ID=edit_id).one_or_none()
        card.PRIMARY_CARD = True
        BankCard.query.filter(BankCard.USER_ID == card.USER_ID, BankCard.BANK_TYPE == card.BANK_TYPE, BankCard.ID != card.ID).update({'PRIMARY_CARD': False}, synchronize_session=False)
        db.session.commit()
        return jsonify({'code': 20000, 'message': "设置成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 50001, 'message': "unknown error."})
