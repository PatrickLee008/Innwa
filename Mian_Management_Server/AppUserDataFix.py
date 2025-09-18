# 2022-08-16 create to fix app user balance error
from management_server.model.AppUserModel import AppUser
from management_server.model.ChargeModel import Charge
from management_server.model.AppUserModel import AppUser
from management_server.model.ChargeModel import Charge
first_charge_time = Charge.query.with_entities(Charge.CREATOR_TIME).limit(1).scalar()
all_charge_user = Charge.query.with_entities(Charge.USER_ID).group_by(Charge.USER_ID).all()
print(len(all_charge_user), first_charge_time)
all_charge_user = {u[0] for u in all_charge_user}
all_balance_user = AppUser.query.with_entities(AppUser.USER_ID, AppUser.TOTAL_MONEY, AppUser.CREAT_TIME).filter(AppUser.TOTAL_MONEY != 0, AppUser.CREAT_TIME >= first_charge_time).all()
print(len(all_balance_user))
error_user = {}
for user_id, total_money, create_time in all_balance_user:
    if user_id not in all_charge_user:
        # error_user[user_id] = total_money
        print(user_id, total_money)

# print(error_user)
