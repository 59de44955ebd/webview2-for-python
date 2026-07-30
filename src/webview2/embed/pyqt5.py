from .. import *

from ctypes import byref
from ctypes.wintypes import MSG, RECT

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget

from ..winapp.const import *
from ..winapp.dlls import user32
from ..winapp.themes import reg_should_use_dark_mode, dwm_use_dark_mode

SETTINGS.ALLOW_HOST_INPUT_PROCESSING = True


########################################
#
########################################
class WebViewWidget(QWidget):

    ########################################
    #
    ########################################
    def __init__(self, webview):
        self._webview = webview
        super().__init__()

	########################################
	#
	########################################
    def resizeEvent(self, event):
        s = self.size()  # event.size() is wrong when fullscreen
        self._webview.put_bounds(RECT(0, 0, s.width(), s.height()))


########################################
#
########################################
class WebView2(WebView2):

    ########################################
    #
    ########################################
    def __init__(self, *args, **kwargs):
        self.widget = WebViewWidget(self)

        self._fullscreen = False
        self._parent_hwnd = int(self.widget.winId())

        super().__init__(self._parent_hwnd, *args, **kwargs)

        QApplication.exec = QApplication.exec_ = self.run

    ########################################
    #
    ########################################
    def toggle_fullscreen(self):
        self._fullscreen = not self._fullscreen
        if self._fullscreen:
            self.widget.setWindowFlags(Qt.Window)
            self.widget.showFullScreen()
        else:
            self.widget.setWindowFlags(Qt.Widget)
            self.widget.show()
        self.set_focus()

	########################################
	#
	########################################
    def run(self):
        msg = MSG()
        while user32.GetMessageW(byref(msg), None, 0, 0):

            # Exit fullscreen mode
            if self._fullscreen:
                if msg.message == WM_KEYDOWN and msg.wParam in (VK_F11, VK_ESCAPE):
                    self.toggle_fullscreen()

            # Forward key events to Qt to make menu accelerators work
            elif msg.message in (WM_KEYDOWN, WM_KEYUP, WM_SYSKEYDOWN, WM_SYSKEYUP) and user32.GetFocus() == self.hwnd:
                user32.SendMessageW(self._parent_hwnd, msg.message, msg.wParam, msg.lParam)

            user32.TranslateMessage(byref(msg))
            user32.DispatchMessageW(byref(msg))
        return 0

	########################################
	#
	########################################
    def close(self):
        super().close()
        user32.PostQuitMessage(0)
