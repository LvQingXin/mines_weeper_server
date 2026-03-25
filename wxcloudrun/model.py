from datetime import datetime

from wxcloudrun import db


# 计数表
class Counters(db.Model):
    # 设置结构体表格名称
    __tablename__ = 'Counters'

    # 设定结构体对应表格的字段
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=1)
    created_at = db.Column('createdAt', db.TIMESTAMP, nullable=False, default=datetime.now())
    updated_at = db.Column('updatedAt', db.TIMESTAMP, nullable=False, default=datetime.now())


class ClearTimeRecords(db.Model):
    __tablename__ = 'ClearTimeRecords'

    id = db.Column(db.Integer, primary_key=True)
    open_id = db.Column('openId', db.String(64))
    union_id = db.Column('unionId', db.String(64))
    nick_name = db.Column('nickName', db.String(64))
    avatar_url = db.Column('avatarUrl', db.String(256))
    gender = db.Column(db.SmallInteger)
    country = db.Column(db.String(64))
    province = db.Column(db.String(64))
    city = db.Column(db.String(64))
    language = db.Column(db.String(32))
    game_type = db.Column('gameType', db.String(32), nullable=False)
    clear_time = db.Column('clearTime', db.Integer, nullable=False)
    extra = db.Column(db.Text)
    created_at = db.Column('createdAt', db.TIMESTAMP, nullable=False, default=datetime.now())
    updated_at = db.Column('updatedAt', db.TIMESTAMP, nullable=False, default=datetime.now())
