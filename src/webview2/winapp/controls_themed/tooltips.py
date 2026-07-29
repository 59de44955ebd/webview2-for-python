from ..controls.tooltips import *
from ..themes import *


########################################
# Wrapper Class
########################################
class Tooltips(Tooltips):

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        uxtheme.SetWindowTheme(self.hwnd, 'DarkMode_Explorer' if is_dark else 'Explorer', None)
