# https://learn.microsoft.com/en-us/windows/win32/controls/toolbar-control-reference
from ..window import *

TOOLBAR_BORDER_BRUSH = gdi32.CreateSolidBrush(0xD7D7D7)  # 0xA0A0A0

TBBUTTON_RESERVED_SIZE = 6

class TBBUTTON(Structure):
    def __init__(self, iBitmap = 0, idCommand = 0, iString = '', fsState = TBSTATE_ENABLED, fsStyle = BTNS_BUTTON, dwData = 0):
        super(TBBUTTON, self).__init__(
            iBitmap,
            idCommand,
            fsState,
            fsStyle,
            (BYTE * TBBUTTON_RESERVED_SIZE)(),
            dwData,
            iString
        )
    _fields_ = [
        ("iBitmap", INT),
        ("idCommand", INT),
        ("fsState", BYTE),
        ("fsStyle", BYTE),
        ("bReserved", BYTE * TBBUTTON_RESERVED_SIZE),
        ("dwData", DWORD_PTR),
        ("iString", c_wchar_p),  # INT_PTR
    ]

class TBMETRICS(Structure):
    def __init__(self, *args, **kwargs):
        super(TBMETRICS, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = [
        ("cbSize", UINT),
        ("dwMask", DWORD),
        ("cxPad", INT),
        ("cyPad", INT),
        ("cxBarPad", INT),
        ("cyBarPad", INT),
        ("cxButtonSpacing", INT),
        ("cyButtonSpacing", INT),
    ]

class TBADDBITMAP(Structure):
    _fields_ = [
        ("hInst", HINSTANCE),
        ("nID", UINT_PTR),
    ]

class TBBUTTONINFOW(Structure):
    def __init__(self, *args, **kwargs):
        super(TBBUTTONINFOW, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = [
        ("cbSize", UINT),
        ("dwMask", DWORD),
        ("idCommand", INT),
        ("iImage", INT),
        ("fsState", BYTE),
        ("fsStyle", BYTE),
        ("cx", WORD),
        ("lParam", DWORD_PTR),
        ("pszText", LPWSTR),
        ("cchText", INT)
    ]

class NMTBCUSTOMDRAW(Structure):
    _fields_ = [
        ("nmcd", NMCUSTOMDRAW),
        ("hbrMonoDither", HBRUSH),
        ("hbrLines", HBRUSH),
        ("hpenLines", HPEN),
        ("clrText", COLORREF),
        ("clrMark", COLORREF),
        ("clrTextHighlight", COLORREF),
        ("clrBtnFace", COLORREF),
        ("clrBtnHighlight", COLORREF),
        ("clrHighlightHotTrack", COLORREF),
        ("rcText", RECT),
        ("nStringBkMode", INT),
        ("nHLStringBkMode", INT),
        ("iListGap", INT),
    ]

class TBREPLACEBITMAP(Structure):
    _fields_ = [
        ("hInstOld", HINSTANCE),
        ("nIDOld", UINT_PTR),
        ("hInstNew", HINSTANCE),
        ("nIDNew", UINT_PTR),
        ("nButtons", INT),
    ]

class NMTOOLBARW(Structure):
    _fields_ = [
        ("hdr", NMHDR),
        ("iItem", INT),
        ("tbButton", TBBUTTON),
        ("cchText", INT),
        ("pszText", LPWSTR),
        ("rcButton", RECT),
    ]

class NMTBGETINFOTIPW(Structure):
    _fields_ = [
        ("hdr", NMHDR),
        ("pszText", LPVOID),
        ("cchTextMax", INT),
        ("iItem", INT),
        ("lParam", LPARAM),
    ]

class NMTBHOTITEM(Structure):
    _fields_ = [
        ("hdr", NMHDR),
        ("idOld", INT),
        ("idNew", INT),
        ("dwFlags", DWORD),
    ]

class TBINSERTMARK(Structure):
    _fields_ = [
        ("iButton", INT),
        ("dwFlags", DWORD),
    ]


########################################
# Wrapper Class
########################################
class ToolBar(Window):

    ########################################
    #
    ########################################
    def __init__(
        self,
        parent_window = None,
        style = WS_CHILD | WS_VISIBLE | CCS_NODIVIDER,
        ex_style = 0,  # WS_EX_COMPOSITED,
        left = 0, top = 0, width = 0, height = 0,
        window_title = None,
        wrap_hwnd = None,
        h_font = H_FONT_SHELL,

        bg_brush = COLOR_3DFACE + 1,
        toolbar_buttons = None,

        h_bitmap = None,
        h_imagelist = None,

        h_imagelist_disabled = None,
#        icon_size = 16,
        bitmap_size = (16, 16),
        hide_text = False,
        num_images = None,
        bottom_divider = False,
        padding = None,

        **kwargs
    ):

        super().__init__(
            WC_TOOLBAR,
            parent_window = parent_window,
            style = style,
            ex_style = ex_style,
            left = left, top = top, width = width, height = height,
            window_title = window_title,
            wrap_hwnd = wrap_hwnd,
            h_font = h_font,
        )

        if window_title:
            user32.SetWindowTextW(self.hwnd, window_title)

#        user32.SendMessageW(self.hwnd, TB_SETEXTENDEDSTYLE, 0, TBSTYLE_EX_MIXEDBUTTONS)

        # The size can be set only before adding any bitmaps to the toolbar.
        # If an application does not explicitly set the bitmap size, the size defaults to 16 by 15 pixel
        user32.SendMessageW(self.hwnd, TB_SETBITMAPSIZE, 0, MAKELONG(*bitmap_size))

        if padding:
            user32.SendMessageW(self.hwnd, TB_SETPADDING, 0, MAKELONG(*padding))

        # Do not forget to send TB_BUTTONSTRUCTSIZE if the toolbar was created by using CreateWindowEx.
        user32.SendMessageW(self.hwnd, TB_BUTTONSTRUCTSIZE, sizeof(TBBUTTON), 0)

        self.bg_brush = bg_brush

        self.h_bitmap = h_bitmap
        self.h_imagelist = h_imagelist
        self.h_imagelist_disabled = h_imagelist_disabled

        self.is_vertical = style & CCS_VERT

        self.has_devider = (style & CCS_NODIVIDER) == 0
        self.bottom_divider = bottom_divider

        num_buttons = len(toolbar_buttons) if toolbar_buttons else 0
        self.num_images = num_images or num_buttons

        self.wholedropdown_button_ids = []
        self.dropdown_button_ids = []

        if toolbar_buttons:

            image_list_id = 0
            if h_bitmap:
                tb = TBADDBITMAP()
                tb.hInst = 0
                tb.nID = self.h_bitmap
                image_list_id = user32.SendMessageW(self.hwnd, TB_ADDBITMAP, num_images or num_buttons, byref(tb))

            elif h_imagelist:
                user32.SendMessageW(self.hwnd, TB_SETIMAGELIST, 0, h_imagelist)

            tb_buttons = (TBBUTTON * num_buttons)()

            j = 0
            for (i, btn) in enumerate(toolbar_buttons):

                if btn[0] == '|':
                    tb_buttons[i] = TBBUTTON(
                        iBitmap = -1,
                        fsState = 0,
                        fsStyle = BTNS_BUTTON,
                        idCommand = btn[1],
                    )

                elif btn[0] == '-':
                    tb_buttons[i] = TBBUTTON(
                        iBitmap = btn[1] if len(btn) > 1 else 0,
                        fsState = TBSTATE_ENABLED | (TBSTATE_WRAP if self.is_vertical else 0),
                        fsStyle = BTNS_SEP,
                        idCommand = btn[2] if len(btn) > 2 else 0,
                    )
                else:
                    tb_buttons[i] = TBBUTTON(
                        MAKELONG(j, image_list_id),                     # iBitmap
                        btn[1],                                         # idCommand,
                        btn[0],                                         # iString
                        btn[3] if len(btn) > 3 else TBSTATE_ENABLED,    # fsState
                        btn[2] if len(btn) > 2 else BTNS_BUTTON,        # fsStyle
                        btn[4] if len(btn) > 4 else 0,                  # dwData
                    )

                    if len(btn) > 2:
                        if btn[2] & BTNS_DROPDOWN or btn[2] & BTNS_WHOLEDROPDOWN:
                            self.dropdown_button_ids.append(btn[1])
                        if btn[2] & BTNS_WHOLEDROPDOWN:
                            self.wholedropdown_button_ids.append(btn[1])

                    j += 1

            # add buttons
            ok = user32.SendMessageW(self.hwnd, TB_ADDBUTTONS, num_buttons, tb_buttons)

            if self.h_imagelist_disabled is not None:
                user32.SendMessageW(self.hwnd, TB_SETDISABLEDIMAGELIST, 0, self.h_imagelist_disabled)

        # Remove text from buttons
        if hide_text:
            user32.SendMessageW(self.hwnd, TB_SETMAXTEXTROWS, 0, 0)

        rc = RECT()
        user32.GetWindowRect(self.hwnd, byref(rc))
        self.height = rc.bottom - rc.top

#        if self.bottom_divider:
        self.parent_window.register_message_callback(WM_NOTIFY, self._on_WM_NOTIFY)

    ########################################
    #
    ########################################
    def destroy_window(self):
        #if self.bottom_divider:
        self.parent_window.unregister_message_callback(WM_NOTIFY, self._on_WM_NOTIFY)
        super().destroy_window()

    ########################################
    #
    ########################################
    def update_size(self, *args):
        user32.SendMessageW(self.hwnd, WM_SIZE, 0, 0)

#    ########################################
#    #
#    ########################################
#    def check_button(self, button_id, flag):
#        user32.SendMessageW(self.hwnd, TB_CHECKBUTTON, button_id, flag)
#
#    ########################################
#    #
#    ########################################
#    def set_indent(self, indent):
#        user32.SendMessageW(self.hwnd, TB_SETINDENT, indent, 0)
#
#    ########################################
#    #
#    ########################################
#    def set_imagelist(self, h_imagelist):
#        user32.SendMessageW(self.hwnd, TB_SETIMAGELIST, 0, h_imagelist)

    ########################################
    #
    ########################################
    def _on_WM_NOTIFY(self, hwnd, wparam, lparam):
        nmhdr = cast(lparam, POINTER(NMHDR)).contents
        msg = nmhdr.code
        if nmhdr.hwndFrom == self.hwnd and msg == NM_CUSTOMDRAW:
            nmtb = cast(lparam, POINTER(NMTBCUSTOMDRAW)).contents
            nmcd = nmtb.nmcd

            if nmcd.dwDrawStage == CDDS_PREPAINT:
                if self.bottom_divider:
                    rc = self.get_client_rect()
                    if self.is_vertical:
                        rc.left = rc.right - 1
                    else:
                        rc.top = rc.bottom - 1
                    user32.FillRect(nmtb.nmcd.hdc, byref(rc), TOOLBAR_BORDER_BRUSH)

            return CDRF_DODEFAULT
