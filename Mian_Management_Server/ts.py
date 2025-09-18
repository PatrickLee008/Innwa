from management_server.model.MatchSettleModel import MatchSettle, SettleStatus
from management_server.model.MatchModel import Match, MatchAttr, VipMatchAttr
from sqlalchemy import func

from management_server.model.AppUserModel import AppUser
from management_server import db
import hashlib

# ms = MatchSettle.query.with_entities(MatchSettle.STATUS, Match).join(Match, MatchSettle.MATCH_ID == Match.MATCH_ID).all()
# match_list = Match.query.with_entities(Match, MatchAttr, VipMatchAttr, MatchSettle).join(MatchAttr, MatchAttr.MATCH_ID == Match.MATCH_ID).join(VipMatchAttr, VipMatchAttr.MATCH_ID == Match.MATCH_ID).join(MatchSettle, MatchSettle.MATCH_ID == Match.MATCH_ID).order_by(Match.MATCH_TIME.desc()).limit(10).all()
# match_list = Match.query.with_entities(Match, MatchAttr).join(MatchAttr, MatchAttr.MATCH_ID == Match.MATCH_ID).all()
# max_priority = MatchSettle.query.with_entities(func.max(MatchSettle.PRIORITY)).scalar()
# xx = MatchSettle.query.all()
# mix_history_orders = session.query(OrderHistory).filter(OrderHistory.MATCH_ID == "1608347695581", Order.IS_MIX == "1").all()
user_id = "09798301683"
psw_sha1 = hashlib.sha1(("123" + user_id).encode(encoding='utf-8')).hexdigest()
AppUser.query.filter_by(USER_ID=user_id).update({"USER_PWD": psw_sha1})
db.session.commit()
