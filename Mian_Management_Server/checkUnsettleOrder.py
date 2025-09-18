from sqlalchemy import and_

from management_server import app_opt, db
from management_server.model.AppOperationModel import AppOperation
from management_server.model.AppUserModel import AppUser
from management_server.model.OrderHistoryModel import OrderHistory

order_history = OrderHistory.query.filter(OrderHistory.MATCH_ID == '1670720418461').all()
for o in order_history:
    coin_log = AppOperation.query.filter(and_(AppOperation.SOURCE_ID == o.ORDER_ID, AppOperation.TYPE == 3)).first()
    if not coin_log:

        app_user = AppUser.query.filter(AppUser.USER_ID == o.USER_ID).frist()
        if app_user:
            before_amount = str(app_user.TOTAL_MONEY)
            app_user.TOTAL_MONEY = AppUser.TOTAL_MONEY + o.BONUS
            after_amount = str(AppUser.TOTAL_MONEY + o.BONUS)

            db.session.commit()

            app_opt.send({
                "user_account": app_user.USER_ID,
                "user_name": app_user.NICK_NAME,
                "type": 3,
                "amount": before_amount,
                "balance": after_amount,
                "source_id": o.ORDER_ID
            })
