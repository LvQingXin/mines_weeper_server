import os
import sys
import json
from unittest import mock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import run
import wxcloudrun.views as views


def _post_json(client, path, payload):
    resp = client.post(path, data=json.dumps(payload), content_type="application/json")
    assert resp.status_code == 200, resp.status_code
    return json.loads(resp.data.decode("utf-8"))


def main():
    app = run.app
    app.testing = True
    client = app.test_client()

    def fake_insert(record):
        record.id = 123

    def fake_query_min(open_id, game_type):
        if open_id == "no_record":
            return None
        return 9

    with mock.patch.object(views, "insert_clear_time_record", side_effect=fake_insert), \
            mock.patch.object(views, "query_min_clear_time", side_effect=fake_query_min):
        ok = _post_json(
            client,
            "/api/clear-time",
            {"gameType": "classic", "clearTime": 12, "userInfo": {"openId": "openid_1"}},
        )
        assert ok["code"] == 0, ok
        assert ok["data"]["id"] == 123, ok

        missing_game_type = _post_json(client, "/api/clear-time", {"clearTime": 12})
        assert missing_game_type["code"] == -1, missing_game_type
        assert missing_game_type["errorMsg"] == "缺少gameType参数", missing_game_type

        missing_clear_time = _post_json(client, "/api/clear-time", {"gameType": "classic"})
        assert missing_clear_time["code"] == -1, missing_clear_time
        assert missing_clear_time["errorMsg"] == "缺少clearTime参数", missing_clear_time

        best_ok = _post_json(
            client,
            "/api/clear-time/best",
            {"openId": "openid_1", "gameType": "classic"},
        )
        assert best_ok["code"] == 0, best_ok
        assert best_ok["data"]["bestClearTime"] == 9, best_ok

        best_none = _post_json(
            client,
            "/api/clear-time/best",
            {"openId": "no_record", "gameType": "classic"},
        )
        assert best_none["code"] == 0, best_none
        assert best_none["data"]["bestClearTime"] is None, best_none

        missing_open_id = _post_json(
            client,
            "/api/clear-time/best",
            {"gameType": "classic"},
        )
        assert missing_open_id["code"] == -1, missing_open_id
        assert missing_open_id["errorMsg"] == "缺少openId参数", missing_open_id

        missing_game_type = _post_json(
            client,
            "/api/clear-time/best",
            {"openId": "openid_1"},
        )
        assert missing_game_type["code"] == -1, missing_game_type
        assert missing_game_type["errorMsg"] == "缺少gameType参数", missing_game_type

    print("self_check_record_clear_time: OK")


if __name__ == "__main__":
    main()
