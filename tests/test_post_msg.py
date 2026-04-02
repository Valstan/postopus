from unittest.mock import MagicMock

import bin.rw.post_msg as pm


def test_post_msg_success():
    mock_vk_app = MagicMock()
    mock_vk_app.wall.post.return_value = {"post_id": 123}

    pm.session = {"vk_app": mock_vk_app}

    res = pm.post_msg(-10, "hello", attachments="photo100_1", from_group=1, copy_right="")

    assert res is not None
    assert res["post_id"] == 123
    assert res["url"] == "https://vk.com/wall-10_123"
    mock_vk_app.wall.post.assert_called_once_with(
        owner_id=-10,
        from_group=1,
        message="hello",
        attachments="photo100_1",
        copyright="",
    )


def test_post_msg_handles_exception(monkeypatch):
    mock_vk_app = MagicMock()
    mock_vk_app.wall.post.side_effect = Exception("boom")

    pm.session = {"vk_app": mock_vk_app}
    # Avoid noisy error handling side-effects
    pm.send_error = lambda *args, **kwargs: None

    res = pm.post_msg(-10, "hello")
    assert res is None
