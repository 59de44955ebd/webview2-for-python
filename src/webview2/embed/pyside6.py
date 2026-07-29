from .. import *

from ctypes import byref
from ctypes.wintypes import MSG

from PySide6.QtCore import Qt, QMetaObject, QFile
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtUiTools import QUiLoader

from ..winapp.const import *
from ..winapp.dlls import user32

SETTINGS.ALLOW_HOST_INPUT_PROCESSING = True

#class UiLoader(QUiLoader):
#    """
#    Source: https://gist.github.com/cpbotha/1b42a20c8f3eb9bb7cb8
#    Subclass QUiLoader to create the user interface in a base instance.
#    Unlike QUiLoader itself this class does not create a new instance of
#    the top-level widget, but creates the user interface in an existing
#    instance of the top-level class.
#    """
#
#    def __init__(self, baseinstance, customWidgets=None):
#        QUiLoader.__init__(self, baseinstance)
#        self.baseinstance = baseinstance
#        self.customWidgets = customWidgets
#
#    def createWidget(self, class_name, parent=None, name=''):
#        """
#        Function that is called for each widget defined in ui file,
#        overridden here to populate baseinstance instead.
#        """
#        if parent is None and self.baseinstance:
#            return self.baseinstance
#        else:
#            if class_name in self.availableWidgets():
#                # create a new widget for child widgets
#                widget = QUiLoader.createWidget(self, class_name, parent, name)
#            else:
#                try:
#                    widget = self.customWidgets[class_name](parent)
#                except (TypeError, KeyError) as e:
#                    raise Exception('No custom widget ' + class_name + ' found in customWidgets param of UiLoader __init__.')
#            if self.baseinstance:
#                setattr(self.baseinstance, name, widget)
#            return widget
#
#
#def loadUi(filename, baseinstance=None, customWidgets=None):
#    loader = UiLoader(baseinstance, customWidgets)
#    ui_file = QFile(filename)
#    ui_file.open(QFile.ReadOnly)
#    widget = loader.load(ui_file)
#    ui_file.close()
#    QMetaObject.connectSlotsByName(widget)
#    return widget


class UiLoader(QUiLoader):
    """
    Source: https://gist.github.com/cpbotha/1b42a20c8f3eb9bb7cb8
    Subclass QUiLoader to create the user interface in a base instance.
    Unlike QUiLoader itself this class does not create a new instance of
    the top-level widget, but creates the user interface in an existing
    instance of the top-level class.
    """

    def __init__(self, baseinstance):
        QUiLoader.__init__(self, baseinstance)
        self.baseinstance = baseinstance

    def createWidget(self, class_name, parent=None, name=''):
        """
        Function that is called for each widget defined in ui file,
        overridden here to populate baseinstance instead.
        """
        if parent is None and self.baseinstance:
            return self.baseinstance
        else:
            # create a new widget for child widgets
            widget = QUiLoader.createWidget(self, class_name, parent, name)
            setattr(self.baseinstance, name, widget)
            return widget


def loadUi(filename: str, baseinstance: QWidget) -> QWidget:
    loader = UiLoader(baseinstance)
    ui_file = QFile(filename)
    ui_file.open(QFile.ReadOnly)
    widget = loader.load(ui_file)
    ui_file.close()
    QMetaObject.connectSlotsByName(widget)
    return widget

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
        s = self.size()  # event.size() is wrong when switching to fullscreen
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
            self._is_central_widget = self.widget.parentWidget().centralWidget() == self.widget
            self.widget.setWindowFlags(Qt.Window)
            self.widget.showFullScreen()
        else:
            self.widget.setWindowFlags(Qt.Widget)
            self.widget.show()
            if self._is_central_widget:
                # Quirk in PySide6 (not in PyQt5/6), we have to reassign the central widget
                self.widget.parentWidget().setCentralWidget(self.widget)
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
