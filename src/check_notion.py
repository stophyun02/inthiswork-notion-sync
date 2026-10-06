"""Read-only access/schema check using the same credentials as synchronization."""
from __future__ import annotations

from .config import Settings
from .notion_api import NotionClient


def main() -> None:
    settings = Settings.from_env()
    if not settings.notion_data_source_id:
        raise SystemExit("NOTION_DATA_SOURCE_ID가 비어 있습니다.")
    client = NotionClient(settings.notion_token, settings.notion_api_version)
    client.validate_sync_schema(settings.notion_data_source_id)
    print("Notion 접근·필수 속성 검사 성공. 수집 및 쓰기는 수행하지 않았습니다.")


if __name__ == "__main__":
    main()
