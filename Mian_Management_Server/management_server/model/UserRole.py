from management_server import db
from sqlalchemy import Column, String, Integer, Table, ForeignKey, DateTime

UserRole = Table('m_sys_user_role',
                 db.metadata,
                 db.Column('USER_ID', db.Integer, ForeignKey('m_sys_user.ID'), primary_key=True),
                 db.Column('ROLE_ID', db.Integer, ForeignKey('m_role.ID'), primary_key=True)
                 )
