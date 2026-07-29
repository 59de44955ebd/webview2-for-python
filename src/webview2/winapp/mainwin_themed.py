from .mainwin import *
from .menu_structs import *
from .themes import *
#from .window import *


class MainWin(MainWin):

    ########################################
    #
    ########################################
    def __init__(
        self,
        *args,
        h_brush_dark = DARK_BG_BRUSH,
        **kwargs
    ):
        self.h_brush_dark = h_brush_dark
        super().__init__(*args, **kwargs)

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        if self.is_dark == is_dark:
            return

        # Update colors of window titlebar
        dwm_use_dark_mode(self.hwnd, is_dark)

        user32.SetClassLongPtrW(self.hwnd, GCL_HBRBACKGROUND, self.h_brush_dark if is_dark else self.h_brush)

        # Update colors of menus
        uxtheme.SetPreferredAppMode(PreferredAppMode.ForceDark if is_dark else PreferredAppMode.ForceLight)
        uxtheme.FlushMenuThemes()

        super().apply_theme(is_dark)

        if self.h_menu:
            theme_menubar(self, is_dark)

        self.redraw_window()
