import json
import os
import sys

from PyQt5.QtCore import Qt, QResource, PYQT_VERSION_STR
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QActionGroup, qApp, QFileDialog
from PyQt5 import uic

APP_NAME = 'WebView2 Demo PyQt5'
APP_DIR = os.path.dirname(__file__)
IS_FROZEN = getattr(sys, 'frozen', False)

if not IS_FROZEN:
    # Force local import
    sys.path.append(os.path.realpath(os.path.join(APP_DIR, '..', '..')))

from webview2.embed.qt5 import *

# In this demo we use a classic window status bar, so disable webview's inline status bar
SETTINGS.STATUS_BAR_ENABLED = False

if IS_FROZEN:
    SETTINGS.USER_DATA_FOLDER = os.path.join(APP_DIR, 'profile')

if os.path.isdir(os.path.join(APP_DIR, 'runtime')):
    SETTINGS.BROWSER_EXECUTABLE_FOLDER = os.path.join(APP_DIR, 'runtime')


########################################
#
########################################
class Main(QMainWindow):

    def __init__(self):
        super().__init__()

        QResource.registerResource(os.path.join(APP_DIR, 'main.rcc'))
        uic.loadUi(os.path.join(APP_DIR, 'main.ui'), self)

        self.setWindowTitle(APP_NAME)

        self.webview = WebView2(url = "https://59de44955ebd.github.io/map/")
        self.setCentralWidget(self.webview.widget)

        self.action_open_file.triggered.connect(self.open_file)
        self.action_save_html.triggered.connect(self.save_page)
        self.action_save_as_pdf.triggered.connect(self.save_as_pdf)
        self.action_save_as_image.triggered.connect(self.save_as_image)
        self.action_print.triggered.connect(self.webview.show_print_ui)
        self.action_fullscreen.triggered.connect(self.webview.toggle_fullscreen)
        ag = QActionGroup(self)
        ag.addAction(self.action_theme_auto)
        ag.addAction(self.action_theme_light)
        ag.addAction(self.action_theme_dark)
        ag.triggered.connect(self.set_theme)
        self.action_about.triggered.connect(self.about)
        self.action_open_dev_tools.triggered.connect(self.webview.open_dev_tools)

        self._is_dark = reg_should_use_dark_mode()
        if self._is_dark:
            self.set_theme(self.action_theme_auto)

        self.resize(1024, 768)
        self.show()

        self.webview.connect(EVENT.STATUS_BAR_TEXT_CHANGED, lambda webview: self.statusBar.showMessage(webview.get_status_bar_text()))

        ########################################
        # Since our app starts with theme = AUTO, always also reset local profile to AUTO.
        ########################################
        def _on_webview_ready(webview):
            webview.profile_apply_theme(PREFERRED_COLOR_SCHEME.AUTO)

        self.webview.connect(EVENT.WEBVIEW_READY, _on_webview_ready)

        ########################################
        #
        ########################################
        def _on_theme_changed():
            if self.action_theme_auto.isChecked():
                self.set_theme(self.action_theme_auto)

        self.webview.expose('theme_changed', _on_theme_changed)

        self.webview.add_script_to_execute_on_document_created("window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => chrome.webview.api.theme_changed());")

        self.webview.set_focus()

	########################################
	# IMPORTANT
	########################################
    def closeEvent(self, event):
        self.webview.close()

    ########################################
    #
    ########################################
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open File', None, 'HTML Files (*.html *.html);;All Files (*.*)')
        if filename:
            self.webview.load_url(f'file:///{filename}')

    ########################################
    #
    ########################################
    def save_page(self):
        self.webview.show_save_as_ui()

    ########################################
    #
    ########################################
    def save_as_pdf(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save as PDF', 'page.pdf', 'PDF Files (*.pdf)')
        if filename:
            self.webview.print_to_pdf(filename)

    ########################################
    #
    ########################################
    def save_as_image(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save as Image', 'page.png', 'PNG Files (*.png);;JPEG Files (*.jpg)')
        if filename:
            image_format = IMAGE_FORMAT.JPEG if filename.lower().endswith('.jpg') else IMAGE_FORMAT.PNG
            istream = POINTER(IStream)()
            hr = shlwapi.SHCreateStreamOnFileW(filename, STGM_CREATE | STGM_WRITE, byref(istream))
            self.webview.capture(image_format, istream)

	########################################
	#
	########################################
    def set_theme(self, action):
        if action == self.action_theme_auto:
            is_dark = reg_should_use_dark_mode()
            if self.webview.webview_ready:
                self.webview.profile_apply_theme(PREFERRED_COLOR_SCHEME.AUTO)
        else:
            is_dark = action == self.action_theme_dark
            if self.webview.webview_ready:
                self.webview.profile_apply_theme(PREFERRED_COLOR_SCHEME.DARK if is_dark else PREFERRED_COLOR_SCHEME.LIGHT)

        dwm_use_dark_mode(int(self.winId()), is_dark)
        pal = QPalette()
        if is_dark:
            # Minimal dark palette
            pal.setColor(QPalette.Window, QColor('#202020'))
            pal.setColor(QPalette.WindowText, Qt.white)
            pal.setColor(QPalette.Base, QColor('#2A2A2A'))
            pal.setColor(QPalette.ToolTipBase, Qt.white)
            pal.setColor(QPalette.ToolTipText, Qt.white)
            pal.setColor(QPalette.Text, Qt.white)
            pal.setColor(QPalette.Button, QColor('#3E3E3E'))
            pal.setColor(QPalette.ButtonText, Qt.white)
            pal.setColor(QPalette.Highlight, QColor('#2A82DA'))
        qApp.setPalette(pal)
        self._is_dark = is_dark

	########################################
	#
	########################################
    def about(self):
        # Messagebox with dark titlebar in dark mode
        dialog = QMessageBox(
            QMessageBox.Information,
            'About',
            (
                f'<b>{APP_NAME}</b><br><br>A simple demo based on Python, PyQt5 and WebView2.<br><br>'
                f'Python version: {sys.version.split()[0]}<br>'
                f'PyQt5 version: {PYQT_VERSION_STR}<br>'
                f'WebView2 version: {WebView2.environment.get_BrowserVersionString()}'
            ),
            QMessageBox.Ok,
            self
        )
        if self._is_dark:
            dwm_use_dark_mode(int(dialog.winId()), True)
        dialog.exec()
        self.webview.set_focus()


if __name__ == '__main__':
    QApplication.setStyle('Fusion')
    app = QApplication([])
    main = Main()
    app.exec()
