"""Desktop entry point for LingoFlow English Learning App."""

from __future__ import annotations

import sys
from pathlib import Path
import webview

from backend.api import LingoFlowApi
from backend.database import Database


def get_resource_dir() -> Path:
    """Return directory containing bundled frontend resources."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parent


def get_data_dir() -> Path:
    """Return persistent directory for the SQLite database."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "data"
    return Path(__file__).resolve().parent / "data"


def main() -> None:
    db = Database(get_data_dir() / "lingoflow.db")
    api = LingoFlowApi(db)

    html_path = get_resource_dir() / "frontend" / "index.html"
    if "--self-test" in sys.argv:
        assert html_path.is_file(), f"Missing frontend entry: {html_path}"
        dashboard = api.get_dashboard()
        assert dashboard["total_words"] >= 60, f"Unexpected word count: {dashboard['total_words']}"
        print("SELF_TEST_OK")
        return

    entry_html = html_path.as_uri()
    webview.create_window(
        title="LingoFlow - 英语学习桌面助手",
        url=entry_html,
        js_api=api,
        width=1220,
        height=820,
        min_size=(960, 660),
    )
    webview.start()


if __name__ == "__main__":
    main()
