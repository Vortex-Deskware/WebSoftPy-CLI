#!/usr/bin/env python3
import sys
import os
import shutil
import subprocess
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.text import Text
from rich import box


def sanitize_filename(title: str) -> str:
    sanitized = title.lower().replace(' ', '_')
    return ''.join(c for c in sanitized if c.isalnum() or c == '_')


def copy_elements_to_webapps():
    script_dir = Path(__file__).parent.resolve()
    src_elements = script_dir / "elements"
    webapps_dir = script_dir / "webapps"
    dest_elements = webapps_dir / "elements"

    if not webapps_dir.exists():
        webapps_dir.mkdir(exist_ok=True)

    if src_elements.exists() and not dest_elements.exists():
        shutil.copytree(src_elements, dest_elements)


def generate_webapp_script(title: str, url: str, use_persistent: bool, titlebar_mode: str, theme_name: str, filename: str):
    url = url.strip()

    webengine_core_imports = ["QWebEnginePage"]
    if use_persistent:
        webengine_core_imports.append("QWebEngineProfile")
    webengine_core_line = f"from PyQt6.QtWebEngineCore import {', '.join(webengine_core_imports)}"

    extra_imports = []
    if titlebar_mode.startswith("WebSoftPy"):
        extra_imports.extend([
            "from PyQt6.QtGui import QIcon, QFont",
            "from PyQt6.QtCore import QSize"
        ])

    base_imports = f"""import sys
from pathlib import Path
from PyQt6.QtCore import Qt, QPoint, QUrl{", QSize" if titlebar_mode.startswith("WebSoftPy") else ""}
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
{webengine_core_line}"""

    if extra_imports:
        base_imports += "\n" + "\n".join(extra_imports)

    if use_persistent:
        storage_code = f'''
        from pathlib import Path
        profile = QWebEngineProfile("CustomProfile", self)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        profile.setCachePath(str(Path.home() / ".{sanitize_filename(title)}" / "cache"))
        profile.setPersistentStoragePath(str(Path.home() / ".{sanitize_filename(title)}" / "storage"))
        page = QWebEnginePage(profile, self)
        self.webview.setPage(page)
'''
    else:
        storage_code = '''
        page = QWebEnginePage(self)
        self.webview.setPage(page)
'''

    if titlebar_mode == "normal":
        class_code = f'''
class SingleSiteBrowser(QMainWindow):
    def __init__(self, start_url: str, app_title: str):
        super().__init__()
        self.setWindowTitle(app_title)
        self.setMinimumSize(900, 600)

        self.webview = QWebEngineView()
{storage_code}
        self.webview.setUrl(QUrl(start_url))
        self.setCentralWidget(self.webview)
'''

    elif titlebar_mode.startswith("WebSoftPy"):
        class_code = f'''
class TitleBar(QWidget):
    def __init__(self, parent, app_title):
        super().__init__(parent)
        self.parent = parent
        self._drag_pos = QPoint()
        self.setFixedHeight(40)
        self.setStyleSheet("background-color: #2d2d2d; color: white;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)

        title_label = QLabel(app_title)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(title_label)
        layout.addStretch()

        btn_size = 36
        btn_min = QPushButton()
        btn_min.setFixedSize(btn_size, btn_size)
        btn_min.setIcon(QIcon("elements/{theme_name}/minimize.svg"))
        btn_min.setIconSize(QSize(btn_size - 12, btn_size - 12))
        btn_min.clicked.connect(parent.showMinimized)

        self.btn_max = QPushButton()
        self.btn_max.setFixedSize(btn_size, btn_size)
        self.btn_max.setIcon(QIcon("elements/{theme_name}/maximize.svg"))
        self.btn_max.setIconSize(QSize(btn_size - 12, btn_size - 12))
        self.btn_max.clicked.connect(self.toggle_max_restore)

        btn_close = QPushButton()
        btn_close.setFixedSize(btn_size, btn_size)
        btn_close.setIcon(QIcon("elements/{theme_name}/close.svg"))
        btn_close.setIconSize(QSize(btn_size - 12, btn_size - 12))
        btn_close.clicked.connect(parent.close)

        for btn in (btn_min, self.btn_max, btn_close):
            btn.setStyleSheet("""
                QPushButton {{ background: transparent; border: none; }}
                QPushButton:hover {{ background: #444; border-radius: 6px; }}
            """)

        layout.addWidget(btn_min)
        layout.addWidget(self.btn_max)
        layout.addWidget(btn_close)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            diff = event.globalPosition().toPoint() - self._drag_pos
            self.parent.move(self.parent.pos() + diff)
            self._drag_pos = event.globalPosition().toPoint()

    def toggle_max_restore(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.btn_max.setIcon(QIcon("elements/{theme_name}/maximize.svg"))
        else:
            self.parent.showMaximized()
            self.btn_max.setIcon(QIcon("elements/{theme_name}/maximize.svg"))


class SingleSiteBrowser(QMainWindow):
    def __init__(self, start_url: str, app_title: str):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(900, 600)

        self.webview = QWebEngineView()
{storage_code}
        self.webview.setUrl(QUrl(start_url))

        main_widget = QWidget()
        vbox = QVBoxLayout(main_widget)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(TitleBar(self, app_title))
        vbox.addWidget(self.webview)
        self.setCentralWidget(main_widget)
'''

    elif titlebar_mode == "frameless":
        class_code = f'''
class SingleSiteBrowser(QMainWindow):
    def __init__(self, start_url: str, app_title: str):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(900, 600)

        self.webview = QWebEngineView()
{storage_code}
        self.webview.setUrl(QUrl(start_url))
        self.setCentralWidget(self.webview)

        self._drag_pos = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            diff = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + diff)
            self._drag_pos = event.globalPosition().toPoint()
'''

    else:
        raise ValueError("Invalid title bar mode")

    code = f'''{base_imports}

{class_code}

def main():
    app = QApplication(sys.argv)
    window = SingleSiteBrowser("{url}", "{title}")
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
'''
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code.strip())


def build_executable(script_path: Path, use_custom_theme: bool):
    exe_name = script_path.stem
    output_dir = Path("webapps").resolve()

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--name', exe_name,
        '--distpath', str(output_dir),
        '--hidden-import', 'PyQt6.QtWebEngineCore',
        '--hidden-import', 'PyQt6.QtNetwork',
        '--hidden-import', 'PyQt6.sip',
        '--hidden-import', 'PyQt6.QtSvgWidgets',
    ]

    if use_custom_theme:
        if sys.platform.startswith('win'):
            cmd += ['--add-data', 'webapps/elements;elements']
        else:
            cmd += ['--add-data', 'webapps/elements:elements']

    cmd.append(str(script_path))

    console.print("\n[bold cyan]🛠️  Building executable...[/bold cyan]")
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        console.print(f"\n[bold green]✅ Success! Executable saved to:[/bold green]\n{output_dir / exe_name}")
    except subprocess.CalledProcessError:
        console.print("\n[bold red]❌ Build failed.[/bold red]")
    except FileNotFoundError:
        console.print("\n[bold red]❌ PyInstaller not found. Run: pip install pyinstaller[/bold red]")


def main():
    global console
    console = Console()

    # Banner
    banner = Text("WebSoftPy 2.5 CLI | Expressional", style="bold magenta")
    console.print(Panel(banner, expand=False, box=box.ROUNDED))

    # Ensure elements are copied
    copy_elements_to_webapps()

    # 1. App Title
    title = Prompt.ask("[bold yellow]Enter application title[/bold yellow]")
    if not title.strip():
        console.print("[red]Title cannot be empty.[/red]")
        return

    # 2. URL
    url = Prompt.ask("[bold yellow]Enter target URL (https://...)[/bold yellow]")
    if not url.strip().startswith(("http://", "https://")):
        console.print("[red]URL must start with http:// or https://[/red]")
        return

    # 3. Window Style
    console.print("\n[bold]Choose window style:[/bold]")
    console.print("  [1] Normal (Standard OS window)")
    console.print("  [2] Custom Title Bar (Theme-based controls)")
    console.print("  [3] Frameless Window (No controls)")
    style_choice = IntPrompt.ask("[bold yellow]Select (1-3)[/bold yellow]", choices=["1", "2", "3"])

    titlebar_mode = {1: "normal", 2: "custom", 3: "frameless"}[style_choice]

    theme_name = ""
    if titlebar_mode == "custom":
        console.print("\n[bold]Available themes:[/bold]")
        themes = [
            "WebSoftPy Flow",
            "WebSoftPy Desk",
            "WebSoftPy Color",
            "WebSoftPy Fizz",
            "WebSoftPy Text",
            "WebSoftPy Draw"
        ]
        for i, t in enumerate(themes, 1):
            console.print(f"  [{i}] {t}")
        theme_idx = IntPrompt.ask("[bold yellow]Select theme (1-6)[/bold yellow]", choices=[str(i) for i in range(1, 7)])
        theme_name = themes[theme_idx - 1]
        titlebar_mode = theme_name  # e.g., "WebSoftPy Flow"

    # 4. Persistent Storage
    use_persist = Confirm.ask("\n[bold yellow]Enable persistent storage? (cookies, cache)[/bold yellow]", default=True)

    # Generate
    filename_base = sanitize_filename(title)
    if not filename_base:
        console.print("[red]Invalid title.[/red]")
        return

    script_path = Path("webapps") / f"{filename_base}.py"
    try:
        generate_webapp_script(title, url, use_persist, titlebar_mode, theme_name, script_path)
        console.print(f"\n[bold green]✅ Script generated: {script_path}[/bold green]")
    except Exception as e:
        console.print(f"\n[bold red]❌ Generation failed: {e}[/bold red]")
        return

    # Build?
    if Confirm.ask("\n[bold yellow]Build executable with PyInstaller?[/bold yellow]", default=False):
        build_executable(script_path, use_custom_theme=(titlebar_mode != "normal" and titlebar_mode != "frameless"))

    console.print("\n[bold blue]✨ Done! Your web app is ready.[/bold blue]")


if __name__ == "__main__":
    main()
