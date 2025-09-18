# -*- coding: utf-8 -*-
from app_server import app, app_opt, db
import datetime
from flask import current_app
from app_server.model.AppOperationModel import AppOperation
from app_server.controller.AppUserController import app_user
from app_server.controller.MatchController import match
from app_server.controller.MdictController import r_conf
from app_server.controller.OrderController import order
from app_server.controller.ChargeApplyController import charge_apply
from app_server.controller.WithDrawController import withdraw
from app_server.controller.BankCardController import bank_card
from app_server.controller.NoticeController import r_notice
from app_server.controller.UploadedImagesController import r_up_image
from app_server.controller.AppOperationController import app_operation
from app_server.utils.OrmUttil import AppOpType2Name
from app_server.controller.DigitalController import digital
from app_server.controller.Digital3DController import digital_3d
from app_server.controller.TechResultController import r_tech_result
from app_server.controller.ChargeController import r_charge
from app_server.controller.LiveController import live

app.register_blueprint(app_user, url_prefix='/app_user')
app.register_blueprint(match, url_prefix='/match')
app.register_blueprint(r_conf, url_prefix='/config')
app.register_blueprint(order, url_prefix='/order')
app.register_blueprint(charge_apply, url_prefix='/charge_apply')
app.register_blueprint(withdraw, url_prefix='/withdraw')
app.register_blueprint(bank_card, url_prefix='/bank_card')
app.register_blueprint(r_notice, url_prefix='/notice')
app.register_blueprint(r_up_image, url_prefix='/up_image')
app.register_blueprint(app_operation, url_prefix='/app_operation')
app.register_blueprint(digital, url_prefix='/digital')
app.register_blueprint(r_tech_result, url_prefix='/tech_result')
app.register_blueprint(digital_3d, url_prefix='/digital_3d')
app.register_blueprint(bank_card, url_prefix='/bank_card')
app.register_blueprint(r_charge, url_prefix='/charge')
app.register_blueprint(live, url_prefix='/live')


@app.route('/hello', methods=['GET'])
def hello():
    return "hello"


@app.route('/favicon.ico')
def favicon():
    # 后端返回文件给前端（浏览器），send_static_file是Flask框架自带的函数
    return current_app.send_static_file('static/favicon.ico')


@app_opt.connect
def on_app_opt(args):
    print("app opting something:", args["user_account"], datetime.datetime.now(), args["type"], args["amount"], args["balance"], args["source_id"])
    is_digit = "is_digit" in args
    opt = AppOperation(USER_ACCOUNT=args['user_account'], TYPE=args["type"], AMOUNT=args["amount"],
                       BALANCE=args["balance"], SOURCE_ID=args["source_id"], IS_DIGIT=is_digit, MATCH_ID=args.get('match_id') or "")
    opt.DESC = "%s do %s at %s make % amount change" % (args['user_name'], AppOpType2Name[args['type']], str(datetime.datetime.now().replace(microsecond=0)), args['amount'])
    db.session.add(opt)
    db.session.commit()


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=app.config['PORT'])
