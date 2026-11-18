"""Desktop entry point for LingoFlow English Learning App."""

from __future__ import annotations

import sys
import threading
from pathlib import Path
from PIL import Image
import pystray
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

    resource_dir = get_resource_dir()
    html_path = resource_dir / "frontend" / "index.html"
    assets_dir = resource_dir / "frontend" / "assets"
    ico_path = assets_dir / "lingoflow.ico"
    png_path = assets_dir / "lingoflow.png"

    if "--self-test" in sys.argv:
        assert html_path.is_file(), f"Missing frontend entry: {html_path}"
        assert (resource_dir / "frontend" / "pronunciation.js").is_file(), "Missing pronunciation.js"
        assert ico_path.is_file(), f"Missing app ico: {ico_path}"
        assert png_path.is_file(), f"Missing app png: {png_path}"
        with Image.open(png_path) as img:
            assert img.size[0] >= 64 and img.size[1] >= 64
        dashboard = api.get_dashboard()
        assert dashboard["total_words"] >= 60, f"Unexpected word count: {dashboard['total_words']}"
        print("SELF_TEST_OK")
        return

    window = webview.create_window(
        title="LingoFlow - 英语学习桌面助手",
        url=str(html_path),
        js_api=api,
        width=1220,
        height=820,
        min_size=(960, 660),
    )

    is_quitting = threading.Event()
    tray_holder: dict[str, pystray.Icon | None] = {"icon": None}

    def show_window(_icon: pystray.Icon | None = None, _item: pystray.MenuItem | None = None) -> None:
        window.show()
        window.restore()

    def hide_window(_icon: pystray.Icon | None = None, _item: pystray.MenuItem | None = None) -> None:
        window.hide()

    def quit_app(icon: pystray.Icon, _item: pystray.MenuItem | None = None) -> None:
        is_quitting.set()
        icon.stop()
        window.destroy()

    def on_closing() -> bool:
        if is_quitting.is_set():
            return True
        window.hide()
        return False

    def on_closed() -> None:
        is_quitting.set()
        tray = tray_holder.get("icon")
        if tray is not None:
            try:
                tray.stop()
            except Exception:
                pass

    def on_loaded() -> None:
        try:
            from Microsoft.Web.WebView2.Core import (
                CoreWebView2PermissionKind,
                CoreWebView2PermissionState,
            )

            core = window.native.browser.webview.CoreWebView2
            if core is not None:
                def _on_perm(_sender, args) -> None:
                    if args.PermissionKind == CoreWebView2PermissionKind.Microphone:
                        args.State = CoreWebView2PermissionState.Allow
                        args.Handled = True

                core.PermissionRequested += _on_perm
        except Exception:
            pass

    window.events.closing += on_closing
    window.events.closed += on_closed
    window.events.loaded += on_loaded

    def start_tray() -> None:
        tray_image = Image.open(png_path if png_path.is_file() else ico_path)
        menu = pystray.Menu(
            pystray.MenuItem("显示主窗口", show_window, default=True),
            pystray.MenuItem("隐藏到托盘", hide_window),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出 LingoFlow", quit_app),
        )
        tray = pystray.Icon("LingoFlow", tray_image, "LingoFlow 英语学习桌面助手", menu)
        tray_holder["icon"] = tray
        threading.Thread(target=tray.run, daemon=True, name="LingoFlowTray").start()

    webview.start(
        func=start_tray,
        http_server=True,
        icon=str(ico_path) if ico_path.is_file() else None,
    )


if __name__ == "__main__":
    main()
