# -*- coding: utf-8 -*-
from management_server import app_opt, app
from management_server.model.OrderModel import Order
from management_server.model.OrderHistoryModel import OrderHistory
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, create_engine, func
from multiprocessing.dummy import Pool
import time
import uuid
import traceback
from sqlalchemy import event
from sqlalchemy import exc
import os

engine = create_engine('mysql+pymysql://%s:%s@%s:3306/%s?charset=utf8' % (app.config["DB_USER"], app.config["DB_PASSWORD"], app.config["DB_ADDRESS"], app.config["DATABASE"]),
                       pool_recycle=10600, pool_size=10600, max_overflow=200)


# 多进程相关配置,Pool使用事件来检测自身，以便在子进程中自动使连接无效
@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    connection_record.info['pid'] = os.getpid()


@event.listens_for(engine, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxy):
    pid = os.getpid()
    if connection_record.info['pid'] != pid:
        connection_record.connection = connection_proxy.connection = None
        raise exc.DisconnectionError(
            "Connection record belongs to pid %s, "
            "attempting to check out in pid %s" %
            (connection_record.info['pid'], pid)
        )


def get_session():
    session_class = sessionmaker(bind=engine)
    session = session_class()

    return session


def settle():
    try:
        session = get_session()
        start = time.time()
        count = 1
        while count:
            old_orders = session.query(Order).filter(Order.STATUS == "0").limit(100000).all()
            count = len(old_orders)
            print("开始执行:", count)
            session.execute(
                OrderHistory.__table__.insert(),
                [o.to_history() for o in old_orders]
                # Creator需要修改
            )
            ids = {o.ID for o in old_orders}
            session.query(Order).filter(Order.ID.in_(ids)).delete(synchronize_session=False)
            session.commit()
            end = time.time()
            print("---转换Order执行:[", count, "]条的用时----:", end - start, "秒")
        session.close()
    except Exception as e:
        print("settle error:", e)
        traceback.print_exc()

    return 1


if __name__ == '__main__':
    settle()
