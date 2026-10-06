from unittest.mock import Mock, call

import pytest

from src import check_notion


def test_check_only_reads_schema_even_when_dry_run_is_enabled(monkeypatch, capsys):
    monkeypatch.setenv("NOTION_DATA_SOURCE_ID", "test-source")
    monkeypatch.setenv("NOTION_TOKEN", "test-token")
    monkeypatch.setenv("DRY_RUN", "true")
    client = Mock()
    monkeypatch.setattr(check_notion, "NotionClient", Mock(return_value=client))
    check_notion.main()
    assert client.mock_calls == [
        call.validate_sync_schema("test-source")
    ]
    assert "검사 성공" in capsys.readouterr().out


def test_check_failure_propagates_without_success_message(monkeypatch, capsys):
    monkeypatch.setenv("NOTION_DATA_SOURCE_ID", "test-source")
    client = Mock()
    client.validate_sync_schema.side_effect = RuntimeError("HTTP 404")
    monkeypatch.setattr(check_notion, "NotionClient", Mock(return_value=client))
    with pytest.raises(RuntimeError, match="HTTP 404"):
        check_notion.main()
    assert not capsys.readouterr().out


def test_check_requires_target_before_connecting(monkeypatch):
    monkeypatch.delenv("NOTION_DATA_SOURCE_ID", raising=False)
    constructor = Mock()
    monkeypatch.setattr(check_notion, "NotionClient", constructor)
    with pytest.raises(SystemExit, match="NOTION_DATA_SOURCE_ID"):
        check_notion.main()
    constructor.assert_not_called()
