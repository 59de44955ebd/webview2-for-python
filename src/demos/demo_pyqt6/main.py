import json
import os
import sys

from PyQt6.QtCore import Qt, QResource, PYQT_VERSION_STR
from PyQt6.QtGui import QPalette, QColor, QActionGroup
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from PyQt6 import uic

APP_NAME = 'WebView2 Demo PyQt6'
APP_DIR = os.path.dirname(__file__)
IS_FROZEN = getattr(sys, 'frozen', False)

if not IS_FROZEN:
    # Force local import
    sys.path.append(os.path.realpath(os.path.join(APP_DIR, '..', '..')))

from webview2.embed.pyqt6 import *

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

        self.set_theme(self.action_theme_auto)

        self.resize(1024, 768)
        self.show()

        self.webview.connect(EVENT.STATUS_BAR_TEXT_CHANGED, lambda webview: self.statusBar.showMessage(webview.get_status_bar_text()))

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
            QApplication.instance().styleHints().setColorScheme(Qt.ColorScheme.Unknown)
            if self.webview.webview_ready:
                self.webview.profile_apply_theme(PREFERRED_COLOR_SCHEME.AUTO)
        else:
            is_dark = action == self.action_theme_dark
            QApplication.instance().styleHints().setColorScheme(Qt.ColorScheme.Dark if is_dark else Qt.ColorScheme.Light)
            if self.webview.webview_ready:
                self.webview.profile_apply_theme(PREFERRED_COLOR_SCHEME.DARK if is_dark else PREFERRED_COLOR_SCHEME.LIGHT)

	########################################
	#
	########################################
    def about(self):
        QMessageBox.about(
            self,
            'About',
            (
                f'<b>{APP_NAME}</b><br><br>A simple demo based on Python, PyQt6 and WebView2.<br><br>'
                f'Python version: {sys.version.split()[0]}<br>'
                f'PyQt6 version: {PYQT_VERSION_STR}<br>'
                f'WebView2 version: {WebView2.environment.get_BrowserVersionString()}'
            )
        )
        self.webview.set_focus()


if __name__ == '__main__':
    QApplication.setStyle('Fusion')
    app = QApplication([])
    main = Main()
    app.exec()
