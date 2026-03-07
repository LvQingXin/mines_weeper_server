from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response

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
    params = request.get_json()

    # 检查type参数
    if 'type' not in params:
        return make_err_response('缺少type参数')

    leaderboard_type = params['type']

    if leaderboard_type not in [LEADERBOARD_TYPE_FRIEND, LEADERBOARD_TYPE_NATIONAL]:
        return make_err_response('type参数错误')

    # mock数据
    mock_data = [
        {'avatar': 'https://example.com/avatar1.png', 'score': 100},
        {'avatar': 'https://example.com/avatar2.png', 'score': 95},
        {'avatar': 'https://example.com/avatar3.png', 'score': 90},
        {'avatar': 'https://example.com/avatar4.png', 'score': 85},
        {'avatar': 'https://example.com/avatar5.png', 'score': 80}
    ]

    return make_succ_response(mock_data)
