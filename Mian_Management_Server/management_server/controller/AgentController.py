from management_server import app, auth, db, user_opt
from sqlalchemy import or_, func, and_
from management_server.model.SysUserModel import SysUser
from management_server.model.AgentModel import Agent
from management_server.model.RoleModel import Role
from management_server.model.ChargeModel import Charge
from management_server.model.WithDrawModel import WithDraw
from flask import g, request, jsonify, Blueprint
from management_server.model.AppUserModel import AppUser
from management_server.model.OrderModel import Order
from management_server.utils import OrmUttil
from management_server.utils.sphinxapi import *
import time

r_agent = Blueprint('agent', __name__)


# 获取管理员列表
@r_agent.route('/get', methods=['GET'])
@auth.login_required
def get_agents():
    """
                @@@
                #### Args:
                        current_page = request.args.get('page', type=int, default=1)
                        limit = request.args.get('limit', type=int, default=20)

                        key_word = request.args.get('key_word')
                        start_time = request.args.get('start_time')
                        end_time = request.args.get('end_time')
                #### Returns::
                        {
                            'code': 20000,
                            'items': [u.to_dict() for u in agents],
                        }
            """

    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)

    agents = Agent.query

    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    if key_word:
        agents = agents.filter(or_(Agent.AGENT_CODE.like('%{}%'.format(key_word)), Agent.AGENT_NAME.like('%{}%'.format(key_word)), Agent.CREATOR.like('%{}%'.format(key_word))))

    if start_time:
        agents = agents.filter(Agent.CREATOR_TIME >= start_time)

    if end_time:
        end_time += ' 23:59:59'
        agents = agents.filter(Agent.CREATOR_TIME <= end_time)

    agents = agents.offset((current_page - 1) * limit).limit(limit).all()
    
    print(f"Found {len(agents)} agents")
    for agent in agents:
        print(f"Agent: {agent.AGENT_CODE}, {agent.AGENT_NAME}, Account: {agent.ACCOUNT}")

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in agents],
    })


# 获取管理员列表
@r_agent.route('/get_one', methods=['GET'])
@auth.login_required
def get_one_agent():
    """
                @@@
                #### Args:
                        agent_code = ""
                        account = ""
                #### Returns::
                        {
                            'code': 20000,
                            'agent': agent.to_dict(),
                        }
            """

    agent_code = request.args.get('agent_code')
    account = request.args.get('account')
    if agent_code:
        agent = Agent.query.filter_by(AGENT_CODE=agent_code).one_or_none()
    else:
        sys_user = SysUser.query.filter_by(ACCOUNT=account).one_or_none()
        if not sys_user:
            return jsonify({
                'code': 50002,
                'message': 'no agent with this account'
            })
        agent = sys_user.AGENT
    if not agent:
        return jsonify({
            'code': 50002,
            'message': 'no agent with this agent code'
        })

    return jsonify({
        'code': 20000,
        'agent': agent.to_dict(),
    })


# 获取管理员列表
@r_agent.route('/get_report', methods=['GET'])
@auth.login_required
def get_report():
    """
                @@@
                #### Args:
                        start_time = request.args.get('start_time')
                        end_time = request.args.get('end_time')

                #### Returns::
                        {
                            'code': 20000,
                            'items': {
                                "surplus_money": agent.SURPLUS_MONEY,
                                "users_count": len(users_under),
                                "total_charge_under": total_charge_under,
                                "total_withdraw_under": total_withdraw_under,
                                "total_benefit": total_benefit
                            }
                        }
            """

    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    if not g.user.AGENT_CODE:
        return jsonify({'code': 50002, "message": "this is not an agent account!"})
    agent = Agent.query.filter_by(AGENT_CODE=g.user.AGENT_CODE).first()
    users_under = AppUser.query.filter_by(AGENT_ID=g.user.AGENT_CODE).all()
    users_under = set([u.USER_ID for u in users_under])
    total_charge_under = Charge.query
    withdraw_list = WithDraw.query

    # 订单盈利统计更改为sphinx
    cl = SphinxClient()
    cl.SetServer('localhost', 9312)
    cl.SetConnectTimeout(10.0)
    cl.SetSortMode(SPH_SORT_ATTR_DESC, "id")

    if start_time:
        total_charge_under = total_charge_under.filter(db.cast(Order.CREATE_TIME, db.Date) >= start_time)
        withdraw_list = withdraw_list.filter(db.cast(Order.CREATE_TIME, db.Date) >= start_time)

        time_array = time.strptime(start_time + " 00:00:00", "%Y-%m-%d %H:%M:%S")
        now_ts = int(time.time())
        start_time = int(time.mktime(time_array))
        cl.SetFilterRange('CREATE_TIME', start_time, now_ts)

    if end_time:
        total_charge_under = total_charge_under.filter(db.cast(Order.CREATE_TIME, db.Date) <= end_time)
        withdraw_list = withdraw_list.filter(db.cast(Order.CREATE_TIME, db.Date) <= end_time)

        end_time += " 23:59:59"
        time_array = time.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        ts = int(time.mktime(time_array))
        cl.SetFilterRange('CREATE_TIME', start_time or 0, ts)

    order_res = cl.Query("@AGENT_CODE %s" % g.user.AGENT_CODE, 'order_history;order_history_add')

    total_benefit = 0
    if order_res and order_res['total_found']:
        cl.SetLimits(0, order_res['total_found'], order_res['total_found'])
        order_res = cl.Query("@AGENT_CODE %s" % g.user.AGENT_CODE, 'order_history;order_history_add')
        for o in order_res['matches']:
            total_benefit += o['attrs']['bet_money'] - o['attrs']['bonus']

    total_charge_under = total_charge_under.with_entities(func.sum(Charge.MONEY)).filter(Charge.USER_ID.in_(users_under), Charge.CHARGE_TYPE == "0", Charge.CREATOR == g.user.AGENT_CODE).scalar()
    print("uuuuu.....", g.user.AGENT_CODE, agent.AGENT_CODE, users_under, total_charge_under)

    total_withdraw_under = withdraw_list.with_entities(func.sum(WithDraw.MONEY)).filter(and_(WithDraw.USER_ID.in_(users_under), WithDraw.OPERATOR == g.user.ACCOUNT,
                                                                                             WithDraw.IS_PAY == "1")).scalar()

    user_opt.send({
        "operate": "查询代理",
        "route": "代理管理",
        "key_word": g.user.AGENT_CODE,
        "user": g.user.ACCOUNT
    })

    return jsonify({
        'code': 20000,
        'items': {
            "surplus_money": agent.SURPLUS_MONEY,
            "users_count": len(users_under),
            "total_charge_under": total_charge_under,
            "total_withdraw_under": total_withdraw_under,
            "total_benefit": total_benefit
        }
    })


@r_agent.route('/edit', methods=['POST'])
@auth.login_required
def edit_agent():
    """
        @@@
        #### Args:
                {
                    AGENT_CODE: "",     //必填
                    AGENT_NAME: "",
                    SEX: "",
                    PHONE_NO: "",
                    PROFIT: "",
                    PASSWORD: "",
                }
        #### Returns::
                {'code': 20000, 'message': "修改成功"}
                {'code': 50001, 'message': "未知错误"}
        """
    args = request.get_json()
    edit_id = args.get('AGENT_CODE')
    password = args.get('PASSWORD')
    try:
        agent = Agent.query.filter_by(AGENT_CODE=edit_id).one_or_none()
        user = agent.ACCOUNT

        args['UPDATOR'] = g.user.NAME

        if password:
            args.pop('PASSWORD')
            user.set_psw(password)

        OrmUttil.set_field(agent, args)

        db.session.commit()

        user_opt.send({
            "operate": "修改代理",
            "route": "代理管理",
            "key_word": edit_id,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "修改成功"})
    except Exception as e:
        print(e)
        return jsonify({
            'code': 50001,
            'message': "未知错误"
        })


@r_agent.route('/add', methods=['POST'])
@auth.login_required
def add_agent():
    """
        @@@
        #### Args:
                {
                    AGENT_NAME: "",
                    SEX: "",
                    PHONE_NO: "",
                    PROFIT: "",        //分润比列
                    ACCOUNT: "",        //账号
                    PASSWORD: "",        //密码
                    ROLES: "",        //角色id数组
                    REMARK: "",        //备注
                }
        #### Returns::
                {'code': 20000, 'message': "添加成功"}
                {'code': 50001, 'message': "未知错误"}
        """

    args = request.get_json()
    account = args.get('ACCOUNT')
    agent_name = args.get('AGENT_NAME')
    password = args.get('PASSWORD')
    print(args)

    try:
        user = SysUser.query.filter_by(ACCOUNT=account).one_or_none()
        if user:
            return jsonify({
                'code': 50001,
                'message': 'agent account repeated!'
            })
        
        # 获取下一个可用的ID
        max_id = db.session.query(db.func.max(SysUser.ID)).scalar()
        next_id = (max_id or 0) + 1
        
        user = SysUser(ID=next_id, ACCOUNT=account)
        args['CREATOR'] = g.user.NAME
        db.session.add(user)
        user.set_psw(password)
        user.NAME = agent_name

        # 查找代理角色，优先查找名称为"agent"的角色
        role = Role.query.filter_by(NAME='agent').first()
        
        if not role:
            # 如果没有找到agent角色，创建一个ID为2的agent角色（因为ID=2是空缺的）
            role = Role(ID=2, NAME='agent', DESCRIPTION='代理角色')
            db.session.add(role)
            db.session.flush()  # 立即写入数据库以获取ID
            print(f"Created agent role: ID={role.ID}, NAME={role.NAME}")
        
        user.ROLES.append(role)

        agent_code = int(round(time.time() * 1000))
        agent = Agent(AGENT_CODE=agent_code, AGENT_NAME=agent_name)
        db.session.add(agent)
        args.pop('ACCOUNT')
        args.pop('PASSWORD')
        # 代理级别判断
        if g.user.ACCOUNT == "admin":
            args['LEVEL'] = '1'
        else:
            # 检查当前用户是否有关联的代理记录
            if not g.user.AGENT:
                return jsonify({'code': 50001, 'message': "只有代理账户才能创建子代理"})
            
            if int(g.user.AGENT.LEVEL) >= 2:
                return jsonify({'code': 50001, 'message': "2级代理不能创建代理"})
            parent_agent = g.user.AGENT
            agent.PARENT = parent_agent
            args['LEVEL'] = '2'
            g.user.AGENT.CHILDREN.append(agent)

        OrmUttil.set_field(agent, args)
        agent.ACCOUNT = user

        db.session.commit()
        user_opt.send({
            "operate": "添加代理",
            "route": "代理管理",
            "key_word": agent_code,
            "user": g.user.ACCOUNT
        })

        return jsonify({'code': 20000, 'message': "添加成功"})
    except Exception as e:
        print("add_agent error:", e)
        db.session.rollback()  # 回滚事务
        return jsonify({'code': 50001, 'message': str(e)})


@r_agent.route('/remove', methods=['POST'])
@auth.login_required
def remove_agent():
    """
        @@@
        #### Args:
                {
                   "AGENT_CODE": 1,
                }
        #### Returns::
                {'code': 20000, 'message': "删除成功"}
                {'code': 50001, 'message': "未知错误"}
        """
    args = request.get_json()
    remove_id = args.get('AGENT_CODE')
    print("remove_agent args", args)
    try:
        agent = Agent.query.filter_by(AGENT_CODE=remove_id).one_or_none()
        if not agent:
            return jsonify({'code': 50002, 'message': "agent not exist."})
        print(agent.ACCOUNT)
        if agent.ACCOUNT:
            db.session.delete(agent.ACCOUNT)
        db.session.delete(agent)
        db.session.commit()

        user_opt.send({
            "operate": "删除代理",
            "route": "代理管理",
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
