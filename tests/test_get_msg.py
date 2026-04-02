from unittest.mock import MagicMock

import bin.rw.get_msg as gm


def test_get_msg_success():
    mock_vk_app = MagicMock()
    mock_vk_app.wall.get.return_value = {"items": [{"id": 1}]}
    gm.session = {"vk_app": mock_vk_app}

    res = gm.get_msg(-1, offset=0, count=1)
    assert isinstance(res, list)
    assert res == [{"id": 1}]


def test_get_msg_exception_returns_empty():
    mock_vk_app = MagicMock()
    mock_vk_app.wall.get.side_effect = Exception("invalid access_token")
    gm.session = {"vk_app": mock_vk_app}

    res = gm.get_msg(-1)
    assert res == []
