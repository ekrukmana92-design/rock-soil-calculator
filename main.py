"""Entry point — Calculator Estimasi Penyelesaian Pengujian
Mekanika Batuan & Tanah (PRD v1.0).

Arsitektur berlapis (PRD Bab 30):

    UI (screens/widgets)
        |
    Application Logic (Calculator)
        |
    Calculation Engine (Estimator / AdvancedEstimator)
        |
    Database Layer (Database)
        |
    SQLite

Jalankan di desktop:
    python main.py

Build APK Android:
    lihat README_BUILD_ANDROID.md
"""

import os
import sys
import traceback
from pathlib import Path

# Pastikan folder project ada di sys.path (penting untuk Android/buildozer)
sys.path.insert(0, str(Path(__file__).resolve().parent))

APP_TITLE = "Estimation Calculator"
WINDOW_SIZE = (420, 860)   # default ukuran smartphone


# ---------------------------------------------------------------------------
# Bootstrap Kivy
# ---------------------------------------------------------------------------
def _configure_kivy() -> None:
    """Atur environment Kivy sebelum diimpor.

    Ukuran jendela desktop dapat diubah lewat argumen ``--size=LEBARxTINGGI``
    (mis. ``--size=600x1000`` untuk simulasi smartphone, ``--size=1230x800``
    untuk tablet). Argumen ini diproses sendiri di sini — bukan oleh Kivy,
    karena ``KIVY_NO_ARGS=1`` mematikan parser bawaan Kivy.
    """
    os.environ.setdefault("KIVY_NO_ARGS", "1")

    # Bila ada --size=WxH, jadikan itu ukuran jendela.
    for arg in sys.argv[1:]:
        if arg.startswith("--size="):
            os.environ["KIVY_WINDOW_SIZE"] = arg.split("=", 1)[1]
            break
    else:
        # Di desktop, ukuran jendela default menyerupai smartphone.
        if sys.platform not in ("android", "ios"):
            os.environ.setdefault(
                "KIVY_WINDOW_SIZE", f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}"
            )


_configure_kivy()

from kivy.app import App                      # noqa: E402
from kivy.clock import Clock                  # noqa: E402
from kivy.core.window import Window           # noqa: E402
from kivy.metrics import dp                   # noqa: E402
from kivy.uix.boxlayout import BoxLayout      # noqa: E402
from kivy.uix.floatlayout import FloatLayout  # noqa: E402
from kivy.uix.label import Label              # noqa: E402
from kivy.uix.screenmanager import (          # noqa: E402
    FadeTransition,
    NoTransition,
    ScreenManager,
)

from calculation import Calculator                    # noqa: E402
from database import Database, DatabaseError          # noqa: E402
from screens import SCREEN_REGISTRY, NavDrawer        # noqa: E402
from widgets.theme import (                           # noqa: E402
    BACKGROUND,
    DANGER,
    FONT_CAPTION,
    NAVY,
    ORANGE,
    SUCCESS,
    SURFACE,
    TEAL,
    TEXT_ON_DARK,
)


# ---------------------------------------------------------------------------
# Snackbar sederhana (pengganti KivyMD Snackbar)
# ---------------------------------------------------------------------------
class Toast(Label):
    """Notifikasi mengambang singkat di bawah layar."""

    LEVEL_COLORS = {
        "info": TEAL,
        "success": SUCCESS,
        "warning": ORANGE,
        "danger": DANGER,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = FONT_CAPTION + 1
        self.color = TEXT_ON_DARK
        self.size_hint = (None, None)
        self.height = dp(44)
        self.padding = (dp(16), dp(12))
        self.opacity = 0
        self.disabled = True
        self.halign = "center"
        self.valign = "middle"
        self._hide_event = None
        self.bind(texture_size=self._adjust)

    def _adjust(self, *_a) -> None:
        self.width = max(dp(240), self.texture_size[0] + dp(40))
        self.text_size = (self.width - dp(32), None)

    def show(self, message: str, level: str = "info", duration: float = 2.6):
        self.text = message
        self.text_size = (None, None)
        color = self.LEVEL_COLORS.get(level, TEAL)
        from kivy.graphics import Color, RoundedRectangle
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*color)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size,
                                        radius=[dp(10)])
        self.bind(pos=self._sync_bg, size=self._sync_bg)
        self._adjust()
        self._reposition()
        self.opacity = 1

        if self._hide_event:
            self._hide_event.cancel()
        self._hide_event = Clock.schedule_once(
            lambda *_: setattr(self, "opacity", 0), duration
        )

    def _sync_bg(self, *_a) -> None:
        if hasattr(self, "_bg"):
            self._bg.pos = self.pos
            self._bg.size = self.size
            self._reposition()

    def _reposition(self) -> None:
        self.pos = (
            (Window.width - self.width) / 2,
            dp(24),
        )


# ---------------------------------------------------------------------------
# Aplikasi
# ---------------------------------------------------------------------------
class CalculatorApp(App):
    """Aplikasi utama."""

    title = APP_TITLE

    # ------------------------------------------------------------------
    def build(self):
        Window.clearcolor = BACKGROUND

        # --- Layer database & logic ------------------------------------
        self.db = Database()
        try:
            self.db.initialize()
        except DatabaseError as exc:  # pragma: no cover
            print(f"[FATAL] Gagal inisialisasi database: {exc}")
            raise

        self.calc = Calculator(self.db)

        # State navigasi antar-screen
        self.pending_category = None
        self.pending_prefill = None

        # --- Root layout ------------------------------------------------
        root = FloatLayout()

        main = BoxLayout(orientation="horizontal")

        self.drawer = NavDrawer(self)
        self.drawer.opacity = 0
        self.drawer.disabled = True
        self.drawer.size_hint_x = None
        self.drawer.width = 0
        main.add_widget(self.drawer)

        self.manager = ScreenManager(transition=NoTransition())
        for route, screen_cls in SCREEN_REGISTRY.items():
            self.manager.add_widget(screen_cls(self, name=route))
        main.add_widget(self.manager)

        root.add_widget(main)

        # --- Toast ------------------------------------------------------
        self.toast = Toast()
        root.add_widget(self.toast)

        # --- Transisi awal ----------------------------------------------
        Window.bind(on_keyboard=self._on_key)
        Clock.schedule_once(lambda *_: self.manager.switch_to(
            self.manager.get_screen("home"), duration=0
        ), 0)

        return root

    # ------------------------------------------------------------------
    def on_start(self) -> None:
        self.manager.current = "home"
        self.drawer.set_active("home")

    def on_stop(self) -> None:
        try:
            self.db.close()
        except Exception:  # pragma: no cover
            pass

    # ------------------------------------------------------------------
    # Navigasi
    # ------------------------------------------------------------------
    def navigate(self, route: str, **kwargs) -> None:
        """Pindah screen & opsional membawa data."""
        if "category" in kwargs:
            self.pending_category = kwargs["category"]
        if "prefill_history" in kwargs:
            self.pending_prefill = kwargs["prefill_history"]

        if route not in self.manager.screen_names:
            self.show_snackbar(f"Halaman '{route}' tidak tersedia.", "warning")
            return

        self.manager.current = route
        self.drawer.set_active(route)
        self._close_drawer()

    def toggle_nav(self, *_args) -> None:
        if self.drawer.width > 0:
            self._close_drawer()
        else:
            self._open_drawer()

    def _open_drawer(self) -> None:
        self.drawer.disabled = False
        self.drawer.opacity = 1
        self.drawer.width = dp(272)

    def _close_drawer(self) -> None:
        from kivy.animation import Animation
        anim = Animation(width=0, opacity=0, duration=0.18)
        anim.bind(on_complete=lambda *_: setattr(self.drawer, "disabled", True))
        anim.start(self.drawer)

    # ------------------------------------------------------------------
    # Notifikasi
    # ------------------------------------------------------------------
    def show_snackbar(self, message: str, level: str = "info") -> None:
        try:
            self.toast.show(message, level)
        except Exception:  # pragma: no cover
            print(f"[{level.upper()}] {message}")

    # ------------------------------------------------------------------
    # Tombol back Android
    # ------------------------------------------------------------------
    def _on_key(self, _window, key, *_args) -> bool:
        if key != 27:  # Esc / tombol back
            return False
        if self.drawer.width > 0:
            self._close_drawer()
            return True
        if self.manager.current != "home":
            self.navigate("home")
            return True
        return False


# ---------------------------------------------------------------------------
def main() -> int:
    try:
        CalculatorApp().run()
        return 0
    except Exception:  # pragma: no cover
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
