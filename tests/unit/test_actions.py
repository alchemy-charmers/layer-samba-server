import imp

import mock


class TestActions:
    def test_get_pass_action(
        self,
        smb,
        mock_action_get,
        mock_action_set,
        mock_action_fail,
        mock_juju_unit,
        monkeypatch,
    ):
        mock_function = mock.Mock()
        monkeypatch.setattr(smb, "get_password", mock_function)
        assert mock_function.call_count == 0
        imp.load_source("get-user-pass", "./actions/get-user-pass")
        assert mock_function.call_count == 1

    def test_set_pass_action(
        self,
        smb,
        mock_action_get,
        mock_action_set,
        mock_action_fail,
        mock_juju_unit,
        monkeypatch,
    ):
        mock_function = mock.Mock()
        monkeypatch.setattr(smb, "set_password", mock_function)
        assert mock_function.call_count == 0
        imp.load_source("set-user-pass", "./actions/set-user-pass")
        assert mock_function.call_count == 1
