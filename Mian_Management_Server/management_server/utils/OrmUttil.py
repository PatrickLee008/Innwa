class AppOpType:
    CHARGE = 0
    WITHDRAW = 1
    BET = 2
    SETTLEMENT = 3
    CANCEL = 4
    REVERSE = 5


AppOpType2Name = {
    0: 'CHARGE',
    1: 'WITHDRAW',
    2: 'BET',
    3: 'SETTLEMENT',
    4: 'CANCEL',
    5: 'REVERSE'
}


class PERMISSION:
    NONE = 0  # 无权限
    ADD = 0x01  # 增
    DELETE = 0x02  # 删
    EDIT = 0x04  # 改
    QUERY = 0x08  # 查
    CRUD = 0x0f  # 增删查改 需要异或

    @staticmethod
    def crud(per):
        return [PERMISSION.can_add(per), PERMISSION.can_delete(per), PERMISSION.can_edit(per),
                PERMISSION.can_query(per)]

    @staticmethod
    def li_to_per(li):
        permission = 0
        for i in range(len(li)):
            if li[i] is True:
                permission |= (1 << i)
        return permission

    @staticmethod
    def can_query(per):
        return per & PERMISSION.QUERY == PERMISSION.QUERY

    @staticmethod
    def can_add(per):
        return per & PERMISSION.ADD == PERMISSION.ADD

    @staticmethod
    def can_edit(per):
        return per & PERMISSION.EDIT == PERMISSION.EDIT

    @staticmethod
    def can_delete(per):
        return per & PERMISSION.DELETE == PERMISSION.DELETE


def set_field(obj_db, data, include=None, exclude=None):
    for key in obj_db.__table__.columns.keys():
        if include and key not in include:
            continue
        if exclude and key in exclude:
            continue
        if key in data:
            setattr(obj_db, key, data[key])
