from ctypes import *
from ctypes.wintypes import *

from .common_structs import *
from .const import *
from .dlls import *
from .menu_structs import *
from .types import LONG_PTR


#from .window import HIGHLIGHT_COLOR, HIGHLIGHT_BRUSH

DIALOG_FOOTER_HEIGHT = 42

########################################
# UxTheme
########################################
uxtheme = windll.uxtheme
# using fnAllowDarkModeForWindow = bool (WINAPI*)(HWND hWnd, bool allow); // ordinal 133
uxtheme.AllowDarkModeForWindow = uxtheme[133]
uxtheme.AllowDarkModeForWindow.argtypes = (HWND, BOOL)
uxtheme.AllowDarkModeForWindow.restype = BOOL
# https://learn.microsoft.com/en-us/windows/win32/api/uxtheme/nf-uxtheme-drawthemebackground
# HTHEME, HDC
uxtheme.DrawThemeBackground.argtypes = (HANDLE, HDC, INT, INT, LPRECT, LPRECT)
uxtheme.FlushMenuThemes = uxtheme[136]
# https://learn.microsoft.com/en-us/windows/win32/api/uxtheme/nf-uxtheme-getthemepartsize
# HTHEME, THEMESIZE
uxtheme.GetThemePartSize.argtypes = (HANDLE, HDC, INT, INT, LPRECT, UINT, LPSIZE)
uxtheme.OpenThemeData.argtypes = (HWND, LPCWSTR)
uxtheme.OpenThemeData.restype = HANDLE
# SetPreferredAppMode = PreferredAppMode(WINAPI*)(PreferredAppMode appMode);
uxtheme.SetPreferredAppMode = uxtheme[135]
uxtheme.SetWindowTheme.argtypes = (HANDLE, LPCWSTR, LPCWSTR)
uxtheme.ShouldAppsUseDarkMode = uxtheme[136]
uxtheme.ShouldSystemUseDarkMode = uxtheme[138]

DWMWA_USE_IMMERSIVE_DARK_MODE = 20

# Window messages related to menu bar drawing
WM_UAHDESTROYWINDOW    = 0x0090	# handled by DefWindowProc
WM_UAHDRAWMENU         = 0x0091	# lParam is UAHMENU
WM_UAHDRAWMENUITEM     = 0x0092	# lParam is UAHDRAWMENUITEM
WM_UAHINITMENU         = 0x0093	# handled by DefWindowProc
WM_UAHMEASUREMENUITEM  = 0x0094	# lParam is UAHMEASUREMENUITEM
WM_UAHNCPAINTMENUPOPUP = 0x0095	# handled by DefWindowProc

# Dark colors and brushes

DARK_BG_COLOR = 0x202020  # 0x101010
DARK_BG_BRUSH = gdi32.CreateSolidBrush(DARK_BG_COLOR)

#DARKER_BG_BRUSH = gdi32.CreateSolidBrush(0x101010)

DARK_CONTROL_BG_COLOR = 0x383838  #0x333333
DARK_CONTROL_BG_BRUSH = gdi32.CreateSolidBrush(DARK_CONTROL_BG_COLOR)

#DARK_TEXT_COLOR = 0xe0e0e0
DARK_TEXT_COLOR = 0xffffff

DARK_SEPARATOR_COLOR = 0x424242
DARK_SEPARATOR_BRUSH = gdi32.CreateSolidBrush(DARK_SEPARATOR_COLOR)

DARK_BORDER_COLOR = 0x646464
DARK_BORDER_BRUSH = gdi32.CreateSolidBrush(DARK_BORDER_COLOR)

DARK_MENU_HOT_BG_COLOR = 0x3e3e3e
DARK_MENU_HOT_BG_BRUSH = gdi32.CreateSolidBrush(DARK_MENU_HOT_BG_COLOR)

DARK_HIGHLIGHT_COLOR = 0xD47800
DARK_HIGHLIGHT_BRUSH = gdi32.CreateSolidBrush(DARK_HIGHLIGHT_COLOR)


class PreferredAppMode():
    Default = 0
    AllowDark = 1
    ForceDark = 2
    ForceLight = 3
    Max = 4

def dwm_use_dark_mode(hwnd, flag):
    value = c_int(1 if flag else 0)
    windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, byref(value), sizeof(value))

UAHDarkModeWndProc = WINFUNCTYPE(BOOL, HWND, UINT, WPARAM, LPARAM, POINTER(LONG_PTR))

class _METRICS(Structure):
    _fields_ = [
        ("cx", DWORD),
        ("cy", DWORD),
    ]

# Describes the sizes of the menu bar or menu item
class UAHMENUITEMMETRICS(Structure):
    _fields_ = [
        ("rgsizeBar", _METRICS * 2),
        ("rgsizePopup", _METRICS * 4),
    ]

# Not really used in our case but part of the other structures
class UAHMENUPOPUPMETRICS(Structure):
    _fields_ = [
        ("rgcx", DWORD * 4),
        ("fUpdateMaxWidths", DWORD),
    ]

# hmenu is the main window menu; hdc is the context to draw in
class UAHMENU(Structure):
    _fields_ = [
        ("hmenu", HMENU),
        ("hdc", HDC),
        ("dwFlags", DWORD),
    ]

# Menu items are always referred to by iPosition here
class UAHMENUITEM(Structure):
    _fields_ = [
        ("iPosition", INT),
        ("umim", UAHMENUITEMMETRICS),
        ("umpm", UAHMENUPOPUPMETRICS),
    ]

# The DRAWITEMSTRUCT contains the states of the menu items, as well as
# the position index of the item in the menu, which is duplicated in
# the UAHMENUITEM's iPosition as well
class UAHDRAWMENUITEM(Structure):
    _fields_ = [
        ("dis", DRAWITEMSTRUCT),
        ("um", UAHMENU),
        ("umi", UAHMENUITEM),
    ]

# The MEASUREITEMSTRUCT is intended to be filled with the size of the item
# height appears to be ignored, but width can be modified
class UAHMEASUREMENUITEM(Structure):
    _fields_ = [
        ("mis", MEASUREITEMSTRUCT),
        ("um", UAHMENU),
        ("umi", UAHMENUITEM),
    ]

########################################
#
########################################
def reg_should_use_dark_mode(use_system = False):
    use_dark_mode = False
    hkey = HKEY()
    if advapi32.RegOpenKeyW(HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize' , byref(hkey)) == ERROR_SUCCESS:
        data = (BYTE * sizeof(DWORD))()
        cbData = DWORD(sizeof(data))
        if advapi32.RegQueryValueExW(hkey, 'SystemUsesLightTheme' if use_system else 'AppsUseLightTheme', None, None, byref(data), byref(cbData)) == ERROR_SUCCESS:
            use_dark_mode = cast(data, POINTER(DWORD)).contents.value == 0
        advapi32.RegCloseKey(hkey)
    return use_dark_mode

########################################
# Update colors of menubar
########################################
def theme_menubar(window, is_dark):

    # Update colors of menubar
    if is_dark:
        ########################################
        #
        ########################################
        def _on_WM_UAHDRAWMENU(hwnd, wparam, lparam):
            pUDM = cast(lparam, POINTER(UAHMENU)).contents
            mbi = MENUBARINFO()
            ok = user32.GetMenuBarInfo(hwnd, OBJID_MENU, 0, byref(mbi))
            rc_win = RECT()
            user32.GetWindowRect(hwnd, byref(rc_win))
            rc = mbi.rcBar
            user32.OffsetRect(byref(rc), -rc_win.left, -rc_win.top)

            #user32.FillRect(pUDM.hdc, byref(rc), MENUBAR_BG_BRUSH_DARK)
            user32.FillRect(pUDM.hdc, byref(rc), DARK_BG_BRUSH)

            return TRUE
        window.register_message_callback(WM_UAHDRAWMENU, _on_WM_UAHDRAWMENU)

        ########################################
        #
        ########################################
        def _on_WM_UAHDRAWMENUITEM(hwnd, wparam, lparam):
            pUDMI = cast(lparam, POINTER(UAHDRAWMENUITEM)).contents
            mii = MENUITEMINFOW()
            mii.fMask = MIIM_STRING
            buf = create_unicode_buffer('', 256)
            mii.dwTypeData = cast(buf, LPWSTR)
            mii.cch = 256
            ok = user32.GetMenuItemInfoW(pUDMI.um.hmenu, pUDMI.umi.iPosition, TRUE, byref(mii))
            if pUDMI.dis.itemState & ODS_HOTLIGHT or pUDMI.dis.itemState & ODS_SELECTED:
                user32.FillRect(pUDMI.um.hdc, byref(pUDMI.dis.rcItem), DARK_MENU_HOT_BG_BRUSH)
            else:
                #user32.FillRect(pUDMI.um.hdc, byref(pUDMI.dis.rcItem), MENUBAR_BG_BRUSH_DARK)
                user32.FillRect(pUDMI.um.hdc, byref(pUDMI.dis.rcItem), DARK_BG_BRUSH)
            gdi32.SetBkMode(pUDMI.um.hdc, TRANSPARENT)
            gdi32.SetTextColor(pUDMI.um.hdc, DARK_TEXT_COLOR)
            user32.DrawTextW(pUDMI.um.hdc, mii.dwTypeData, len(mii.dwTypeData), byref(pUDMI.dis.rcItem), DT_CENTER | DT_SINGLELINE | DT_VCENTER)
            return TRUE
        window.register_message_callback(WM_UAHDRAWMENUITEM, _on_WM_UAHDRAWMENUITEM)

        ########################################
        #
        ########################################
        def UAHDrawMenuNCBottomLine(hwnd, wparam, lparam):
            rcClient = RECT()
            user32.GetClientRect(hwnd, byref(rcClient))
            user32.MapWindowPoints(hwnd, None, byref(rcClient), 2)
            rcWindow = RECT()
            user32.GetWindowRect(hwnd, byref(rcWindow))
            user32.OffsetRect(byref(rcClient), -rcWindow.left, -rcWindow.top)
            # the rcBar is offset by the window rect
            rcAnnoyingLine = rcClient
            rcAnnoyingLine.bottom = rcAnnoyingLine.top
            rcAnnoyingLine.top -= 1
            hdc = user32.GetWindowDC(hwnd)

            # no line at all
            #user32.FillRect(hdc, byref(rcAnnoyingLine), DARK_BG_BRUSH)

            # dark line (same as toolbar button bg)
            user32.FillRect(hdc, byref(rcAnnoyingLine), DARK_SEPARATOR_BRUSH)

            user32.ReleaseDC(hwnd, hdc)

        ########################################
        #
        ########################################
        def _on_WM_NCPAINT(hwnd, wparam, lparam):
            user32.DefWindowProcW(hwnd, WM_NCPAINT, wparam, lparam)
            UAHDrawMenuNCBottomLine(hwnd, wparam, lparam)
            return TRUE
        window.register_message_callback(WM_NCPAINT, _on_WM_NCPAINT)

        ########################################
        #
        ########################################
        def _on_WM_NCACTIVATE(hwnd, wparam, lparam):
            user32.DefWindowProcW(hwnd, WM_NCACTIVATE, wparam, lparam)
            UAHDrawMenuNCBottomLine(hwnd, wparam, lparam)
            return TRUE
        window.register_message_callback(WM_NCACTIVATE, _on_WM_NCACTIVATE)

    else:
        window.unregister_message_callback(WM_UAHDRAWMENU)
        window.unregister_message_callback(WM_UAHDRAWMENUITEM)
        window.unregister_message_callback(WM_NCPAINT)
        window.unregister_message_callback(WM_NCACTIVATE)

########################################
#
########################################
def dark_dialog_init(hwnd):

    # Update colors of window titlebar
    dwm_use_dark_mode(hwnd, True)

    hfont = user32.SendMessageW(hwnd, WM_GETFONT, 0, 0)

    controls = []
    def _enum_child_func(hwnd_child, lparam):
        controls.append(hwnd_child)
        return TRUE
    user32.EnumChildWindows(hwnd, WNDENUMPROC(_enum_child_func), 0)

    for hwnd_control in controls:
        buf = create_unicode_buffer(32)
        user32.GetClassNameW(hwnd_control, buf, 32)
        window_class = buf.value

        ########################################
        # Button
        ########################################
        if window_class == WC_BUTTON:
            uxtheme.SetWindowTheme(hwnd_control, 'DarkMode_Explorer', None)

        ########################################
        # Edit
        ########################################
        elif window_class == 'Edit':

            user32.SetWindowLongA(hwnd_control, GWL_EXSTYLE,
                    user32.GetWindowLongA(hwnd_control, GWL_EXSTYLE) & ~WS_EX_STATICEDGE & ~WS_EX_CLIENTEDGE)
            user32.SetWindowLongA(hwnd_control, GWL_STYLE,
                    user32.GetWindowLongA(hwnd_control, GWL_STYLE) | WS_BORDER)

            rc = RECT()
            user32.GetWindowRect(hwnd_control, byref(rc))
            #w, h = rc.right - rc.left, rc.bottom - rc.top
            #user32.SendMessageW(hwnd_control, EM_SETMARGINS, EC_LEFTMARGIN, 2)
            user32.MapWindowPoints(None, user32.GetParent(hwnd_control), byref(rc), 2)
            user32.SetWindowPos(
                hwnd_control, 0,
                rc.left + 1, rc.top,
                rc.right - rc.left - 2, rc.bottom - rc.top,
                SWP_NOZORDER | SWP_FRAMECHANGED
            )

        ########################################
        # Static
        ########################################
        elif window_class == 'Static':
            ex_style = user32.GetWindowLongA(hwnd_control, GWL_EXSTYLE)
            if ex_style & WS_EX_STATICEDGE or ex_style & WS_EX_CLIENTEDGE:
                user32.SetWindowLongA(hwnd_control, GWL_EXSTYLE, ex_style & ~WS_EX_STATICEDGE & ~WS_EX_CLIENTEDGE)
                user32.SetWindowLongA(hwnd_control, GWL_STYLE, user32.GetWindowLongA(hwnd_control, GWL_STYLE) | WS_BORDER)

########################################
#
########################################
def dark_dialog_handle_messages(hwnd, msg, wparam):

    if msg == WM_ERASEBKGND:
        rc = RECT()
        user32.GetClientRect(hwnd, byref(rc))
        b = rc.bottom
        rc.bottom -= DIALOG_FOOTER_HEIGHT
        user32.FillRect(wparam, byref(rc), DARK_CONTROL_BG_BRUSH)
        rc.top = rc.bottom
        rc.bottom = b
        user32.FillRect(wparam, byref(rc), DARK_BG_BRUSH)
        return TRUE

#    elif msg == WM_CTLCOLORDLG or msg == WM_CTLCOLORSTATIC:
#        gdi32.SetTextColor(wparam, DARK_TEXT_COLOR)
#        gdi32.SetBkColor(wparam, DARK_BG_COLOR)
#        return DARK_BG_BRUSH

    elif msg == WM_CTLCOLORSTATIC:
        gdi32.SetTextColor(wparam, DARK_TEXT_COLOR)
        gdi32.SetBkColor(wparam, DARK_CONTROL_BG_COLOR)
        return DARK_CONTROL_BG_BRUSH

    elif msg == WM_CTLCOLORBTN:
        gdi32.SetDCBrushColor(wparam, DARK_BG_COLOR)
        return gdi32.GetStockObject(DC_BRUSH)

    elif msg == WM_CTLCOLOREDIT or msg == WM_CTLCOLORLISTBOX:
        gdi32.SetTextColor(wparam, DARK_TEXT_COLOR)
        gdi32.SetBkColor(wparam, 0x2A2A2A)  #DARK_CONTROL_BG_COLOR)
        gdi32.SetDCBrushColor(wparam, 0x2A2A2A)  #DARK_CONTROL_BG_COLOR)
        return gdi32.GetStockObject(DC_BRUSH)

    elif msg == WM_PAINT:
        ps = PAINTSTRUCT()
        hdc = user32.BeginPaint(hwnd, byref(ps))
#        ps.rcPaint.top = ps.rcPaint.bottom - DIALOG_FOOTER_HEIGHT
#        user32.FillRect(hdc, byref(ps.rcPaint), DARK_BG_BRUSH)
        user32.EndPaint(hwnd, byref(ps))
        return 0

    return FALSE
