# -*- coding: utf-8 -*-
from management_server import app, user_opt, db, app_opt
import datetime
from management_server.model.AppOperationModel import AppOperation
from management_server.utils.OrmUttil import AppOpType2Name
from management_server.model.OperationModel import Operation
from management_server.controller.AdminController import admin
from management_server.controller.AgentController import r_agent
from management_server.controller.MatchController import r_match
from management_server.controller.OrderController import r_order
from management_server.controller.ChargeController import charge
from management_server.controller.WithDrawController import withdraw
from management_server.controller.AppUserController import app_user
from management_server.controller.RouteController import menu
from management_server.controller.RoleController import r_role
from management_server.controller.NoticeController import r_notice
from management_server.controller.MdictController import r_conf
from management_server.controller.SettlementController import settlement
from management_server.controller.ReportController import report
from management_server.controller.OperationController import operation
from management_server.controller.AppOperationController import app_operation
from management_server.controller.LoginRecordController import login_record
from management_server.controller.ContactFuncController import r_contact_fun
from management_server.controller.BankTypeController import r_bank_type
from management_server.controller.UploadedImageController import r_up_image
from management_server.controller.DeviceController import r_device
from management_server.controller.MatchSettleController import r_match_settle
from management_server.controller.WithDrawGroupController import withdraw_group
from management_server.controller.DigitalController import r_digital
from management_server.controller.Digital3DController import r_digital_3d
from management_server.controller.SysBankcardController import r_sys_bankcard
from management_server.controller.ChargeCallBackController import r_charge_callback
from management_server.controller.OrderCopyController import r_order_copy


app.register_blueprint(report, url_prefix='/report')
app.register_blueprint(r_match, url_prefix='/match')
app.register_blueprint(r_order, url_prefix='/order')
app.register_blueprint(charge, url_prefix='/charge')
app.register_blueprint(withdraw, url_prefix='/withdraw')
app.register_blueprint(app_user, url_prefix='/app_user')
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(r_agent, url_prefix='/agent')
app.register_blueprint(menu, url_prefix='/menu')
app.register_blueprint(r_role, url_prefix='/role')
app.register_blueprint(r_notice, url_prefix='/notice')
app.register_blueprint(r_conf, url_prefix='/config')
app.register_blueprint(settlement, url_prefix='/settlement')
app.register_blueprint(operation, url_prefix='/operation')
app.register_blueprint(app_operation, url_prefix='/app_operation')
app.register_blueprint(login_record, url_prefix='/login_record')
app.register_blueprint(r_contact_fun, url_prefix='/contact_fun')
app.register_blueprint(r_bank_type, url_prefix='/bank_type')
app.register_blueprint(r_up_image, url_prefix='/up_image')
app.register_blueprint(r_device, url_prefix='/device')
app.register_blueprint(r_match_settle, url_prefix='/match_settle')
app.register_blueprint(withdraw_group, url_prefix='/withdraw_group')
app.register_blueprint(r_digital, url_prefix='/digit')
app.register_blueprint(r_digital_3d, url_prefix='/digital_3d')
app.register_blueprint(r_sys_bankcard, url_prefix='/sys_bankcard')
app.register_blueprint(r_charge_callback, url_prefix='/charge_callback')
app.register_blueprint(r_order_copy, url_prefix='/order_copy')

@app.route('/hello', methods=['GET'])
def hello():
    return "hello"


@user_opt.connect
def on_user_opt(args):
    print("user opting something:", args["user"], datetime.datetime.now(), args["route"], args["key_word"])
    opt = Operation(USER_ACCOUNT=args['user'], ROUTE=args["route"], OPERATION=args["operate"], TARGET=args["key_word"])
    db.session.add(opt)
    db.session.commit()


@app_opt.connect
def on_app_opt(args):
    print("app opting something:", args["user_account"], datetime.datetime.now(), args["type"], args["amount"], args["balance"], args["source_id"])

    is_digit = "is_digit" in args
    opt = AppOperation(USER_ACCOUNT=args['user_account'], TYPE=args["type"], AMOUNT=args["amount"],
                       BALANCE=args["balance"], SOURCE_ID=args["source_id"], IS_DIGIT=is_digit, MATCH_ID=args.get('match_id') or "")
    group = args.get("work_group") or ""
    opt.DESC = "%s%s do %s at %s make % amount change" % (group, args['user_name'], AppOpType2Name[args['type']], str(datetime.datetime.now().replace(microsecond=0)), args['amount'])
    db.session.add(opt)
    db.session.commit()


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=app.config['PORT'])
