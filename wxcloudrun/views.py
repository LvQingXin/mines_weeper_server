import json
from datetime import datetime
from flask import render_template, request
from wxcloudrun import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid, insert_clear_time_record, query_min_clear_time
from wxcloudrun.model import Counters, ClearTimeRecords
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response

logger = app.logger

# 排行榜类型常量
LEADERBOARD_TYPE_FRIEND = 'friend'
LEADERBOARD_TYPE_NATIONAL = 'national'


@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')


@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)


@app.route('/api/leaderboard', methods=['POST'])
def leaderboard():
    """
    :return: 排行榜列表
    """
    # 获取请求体参数
    params = request.get_json(silent=True) or {}

    # 检查type参数
    leaderboard_type = params.get('type') or request.args.get('type')
    if not leaderboard_type:
        return make_err_response('缺少type参数')

    if leaderboard_type not in [LEADERBOARD_TYPE_FRIEND, LEADERBOARD_TYPE_NATIONAL]:
        logger.warning('leaderboard invalid type: %s', leaderboard_type)
        return make_err_response('type参数错误')

    # mock数据
    mock_data = [
        {'avatar': 'https://example.com/avatar1.png', 'score': 100},
        {'avatar': 'https://example.com/avatar2.png', 'score': 95},
        {'avatar': 'https://example.com/avatar3.png', 'score': 90},
        {'avatar': 'https://example.com/avatar4.png', 'score': 85},
        {'avatar': 'https://example.com/avatar5.png', 'score': 80}
    ]

    logger.info('leaderboard type: %s, size: %s', leaderboard_type, len(mock_data))
    return make_succ_response(mock_data)


@app.route('/api/clear-time', methods=['POST'])
def record_clear_time():
    params = request.get_json(silent=True) or {}

    game_type = params.get('gameType') or params.get('game_type')
    if not game_type:
        return make_err_response('缺少gameType参数')
    if not isinstance(game_type, str):
        return make_err_response('gameType参数格式错误')
    game_type = game_type.strip()
    if not game_type:
        return make_err_response('gameType参数格式错误')

    clear_time_raw = params.get('clearTime') if 'clearTime' in params else params.get('clear_time')
    if clear_time_raw is None:
        return make_err_response('缺少clearTime参数')
    try:
        clear_time = int(clear_time_raw)
    except (TypeError, ValueError):
        return make_err_response('clearTime参数格式错误')
    if clear_time <= 0:
        return make_err_response('clearTime参数错误')

    user_info = params.get('userInfo') or params.get('user_info') or {}
    if user_info is None:
        user_info = {}
    if not isinstance(user_info, dict):
        return make_err_response('userInfo参数格式错误')

    def pick_value(keys):
        for k in keys:
            if k in params:
                return params.get(k)
        for k in keys:
            if k in user_info:
                return user_info.get(k)
        return None

    def validate_optional_str(value, max_len, err_name):
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError(f'{err_name}参数格式错误')
        if len(value) > max_len:
            raise ValueError(f'{err_name}参数错误')
        return value

    def validate_optional_int(value, err_name):
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError(f'{err_name}参数格式错误')

    try:
        open_id = validate_optional_str(pick_value(['openId', 'open_id']), 64, 'openId')
        union_id = validate_optional_str(pick_value(['unionId', 'union_id']), 64, 'unionId')
        nick_name = validate_optional_str(pick_value(['nickName', 'nick_name']), 64, 'nickName')
        avatar_url = validate_optional_str(pick_value(['avatarUrl', 'avatar_url']), 256, 'avatarUrl')
        country = validate_optional_str(pick_value(['country']), 64, 'country')
        province = validate_optional_str(pick_value(['province']), 64, 'province')
        city = validate_optional_str(pick_value(['city']), 64, 'city')
        language = validate_optional_str(pick_value(['language']), 32, 'language')
        gender = validate_optional_int(pick_value(['gender']), 'gender')
    except ValueError as e:
        return make_err_response(str(e))

    if gender is not None and gender not in [0, 1, 2]:
        return make_err_response('gender参数错误')

    extra = params.get('extra')
    if extra is not None and not isinstance(extra, (str, dict, list)):
        return make_err_response('extra参数格式错误')
    if isinstance(extra, (dict, list)):
        extra = json.dumps(extra, ensure_ascii=False, separators=(',', ':'))

    now = datetime.now()
    record = ClearTimeRecords()
    record.open_id = open_id
    record.union_id = union_id
    record.nick_name = nick_name
    record.avatar_url = avatar_url
    record.gender = gender
    record.country = country
    record.province = province
    record.city = city
    record.language = language
    record.game_type = game_type
    record.clear_time = clear_time
    record.extra = extra
    record.created_at = now
    record.updated_at = now

    insert_clear_time_record(record)
    if record.id is None:
        logger.error('clear-time insert failed, gameType=%s', game_type)
        return make_err_response('写入通关记录失败')
    return make_succ_response({'id': record.id})


@app.route('/api/clear-time/best', methods=['POST'])
def best_clear_time():
    params = request.get_json(silent=True) or {}

    open_id_present = 'openId' in params or 'open_id' in params
    if not open_id_present:
        return make_err_response('缺少openId参数')
    open_id = params.get('openId') if 'openId' in params else params.get('open_id')
    if not isinstance(open_id, str):
        return make_err_response('openId参数格式错误')
    open_id = open_id.strip()
    if not open_id:
        return make_err_response('openId参数格式错误')
    if len(open_id) > 64:
        return make_err_response('openId参数错误')

    game_type_present = 'gameType' in params or 'game_type' in params
    if not game_type_present:
        return make_err_response('缺少gameType参数')
    game_type = params.get('gameType') if 'gameType' in params else params.get('game_type')
    if not isinstance(game_type, str):
        return make_err_response('gameType参数格式错误')
    game_type = game_type.strip()
    if not game_type:
        return make_err_response('gameType参数格式错误')
    if len(game_type) > 32:
        return make_err_response('gameType参数错误')

    best_clear_time = query_min_clear_time(open_id, game_type)
    return make_succ_response({
        'openId': open_id,
        'gameType': game_type,
        'bestClearTime': best_clear_time
    })
